from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas, storage
from database import engine, get_db


models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Malzeme Kütüphanesi API")

app.mount("/vitrin", StaticFiles(directory="static", html=True), name="static")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

@app.get("/")
def ana_sayfa():
    return {"mesaj": "API aktif, kullanıcı kaydı hazır!"}


@app.post("/users/", response_model=schemas.User)
def kullanici_kaydet(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kullanımda.")

    hashed_pwd = pwd_context.hash(user.password)
    yeni_kullanici = models.User(email=user.email, hashed_password=hashed_pwd)
    db.add(yeni_kullanici)
    db.commit()
    db.refresh(yeni_kullanici)
    return yeni_kullanici


@app.post("/login/")
def giris_yap(email: str, sifre: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı!")
    if not pwd_context.verify(sifre, user.hashed_password):
        raise HTTPException(status_code=400, detail="Hatalı şifre girdiniz!")

    return {"mesaj": "Giriş başarılı! Hoş geldin.", "kullanici_id": user.id, "email": user.email}


@app.post("/upload-model/{user_id}")
async def model_yukle(
    user_id: int, 
    name: str = Form(...), 
    dimensions: str = Form("Bilinmiyor"), 
    usage_area: str = Form("Genel"), 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    file_content = await file.read()
    file_url = storage.upload_file(file.filename, file_content, file.content_type)

    yeni_model = models.Material(
        name=name, file_url=file_url, owner_id=user_id,
        dimensions=dimensions, usage_area=usage_area
    )
    db.add(yeni_model)
    db.commit()
    db.refresh(yeni_model)
    return {"mesaj": "Model başarıyla yüklendi!", "detay": yeni_model}

# --- MODELLERİ LİSTELEME ---

@app.get("/models/", response_model=list[schemas.Material])
def tum_modelleri_getir(db: Session = Depends(get_db)):
    return db.query(models.Material).all()

# --- YORUM YAP VE BİLDİRİM GÖNDER ---

@app.post("/models/{model_id}/comments")
def yorum_yap(model_id: int, user_id: int, comment_data: schemas.CommentBase, db: Session = Depends(get_db)):
    yeni_yorum = models.Comment(text=comment_data.text, user_id=user_id, material_id=model_id)
    db.add(yeni_yorum)
    
    model = db.query(models.Material).filter(models.Material.id == model_id).first()
    if model and model.owner_id != user_id:
        yeni_bildirim = models.Notification(
            message=f"'{model.name}' isimli modelinize yeni bir yorum geldi!",
            user_id=model.owner_id
        )
        db.add(yeni_bildirim)
        
    db.commit()
    return {"mesaj": "Yorum başarıyla eklendi"}

# --- BİLDİRİMLERİ GETİR ---

@app.get("/notifications/{user_id}", response_model=list[schemas.Notification])
def bildirimleri_getir(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Notification).filter(models.Notification.user_id == user_id).order_by(models.Notification.id.desc()).all()

# --- MODEL SİLME (GÜVENLİ) ---

@app.delete("/models/{model_id}")
def model_sil(model_id: int, kullanici_id: int, db: Session = Depends(get_db)):
    silinecek_model = db.query(models.Material).filter(models.Material.id == model_id).first()
    if not silinecek_model:
        raise HTTPException(status_code=404, detail="Böyle bir model bulunamadı!")
    if silinecek_model.owner_id != kullanici_id:
        raise HTTPException(status_code=403, detail="Erişim reddedildi: Sadece kendi modellerinizi silebilirsiniz!")

    db.delete(silinecek_model)
    db.commit()
    return {"mesaj": f"ID'si {model_id} olan model başarıyla silindi!"}
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas, storage
from database import engine, get_db

# Veritabanı tablolarını oluştur (Eksik tablo varsa yaratır, var olanı bozmaz)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Malzeme Kütüphanesi API")

# --- ÖNYÜZ (VİTRİN) BAĞLANTISI ---
app.mount("/vitrin", StaticFiles(directory="static", html=True), name="static")

# ŞİFRE GÜVENLİĞİ: Şifreleri "hash"lemek (şifrelemek) için araç
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

@app.get("/")
def ana_sayfa():
    return {"mesaj": "API aktif, kullanıcı kaydı hazır!"}

# --- KULLANICI İŞLEMLERİ ---

@app.post("/users/", response_model=schemas.User)
def kullanici_kaydet(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kullanımda.")

    hashed_pwd = pwd_context.hash(user.password)

    yeni_kullanici = models.User(email=user.email, hashed_password=hashed_pwd)
    db.add(yeni_kullanici)
    db.commit()
    db.refresh(yeni_kullanici)
    return yeni_kullanici

# --- GİRİŞ YAP (LOGIN) ---

@app.post("/login/")
def giris_yap(email: str, sifre: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı!")

    if not pwd_context.verify(sifre, user.hashed_password):
        raise HTTPException(status_code=400, detail="Hatalı şifre girdiniz!")

    return {
        "mesaj": "Giriş başarılı! Hoş geldin.",
        "kullanici_id": user.id,
        "email": user.email
    }

# --- GELİŞMİŞ MODEL YÜKLEME --- 

@app.post("/upload-model/{user_id}")
async def model_yukle(
    user_id: int, 
    name: str = Form(...), 
    dimensions: str = Form("Bilinmiyor"), 
    usage_area: str = Form("Genel"), 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    file_content = await file.read()
    file_url = storage.upload_file(file.filename, file_content, file.content_type)

    yeni_model = models.Material(
        name=name, 
        file_url=file_url, 
        owner_id=user_id,
        dimensions=dimensions, 
        usage_area=usage_area
    )
    db.add(yeni_model)
    db.commit()
    db.refresh(yeni_model)
    return {"mesaj": "Model başarıyla yüklendi!", "detay": yeni_model}

# --- MODELLERİ LİSTELEME ---

@app.get("/models/", response_model=list[schemas.Material])
def tum_modelleri_getir(db: Session = Depends(get_db)):
    modeller = db.query(models.Material).all()
    return modeller

# --- YORUM YAP VE BİLDİRİM GÖNDER ---

@app.post("/models/{model_id}/comments")
def yorum_yap(model_id: int, user_id: int, comment_data: schemas.CommentBase, db: Session = Depends(get_db)):
    yeni_yorum = models.Comment(text=comment_data.text, user_id=user_id, material_id=model_id)
    db.add(yeni_yorum)
    
    model = db.query(models.Material).filter(models.Material.id == model_id).first()
    
    if model and model.owner_id != user_id:
        yeni_bildirim = models.Notification(
            message=f"'{model.name}' isimli modelinize yeni bir yorum geldi!",
            user_id=model.owner_id
        )
        db.add(yeni_bildirim)
        
    db.commit()
    return {"mesaj": "Yorum başarıyla eklendi"}

# --- BİLDİRİMLERİ GETİR ---

@app.get("/notifications/{user_id}", response_model=list[schemas.Notification])
def bildirimleri_getir(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Notification).filter(models.Notification.user_id == user_id).order_by(models.Notification.id.desc()).all()


@app.delete("/models/{model_id}")
def model_sil(model_id: int, kullanici_id: int, db: Session = Depends(get_db)):
    silinecek_model = db.query(models.Material).filter(models.Material.id == model_id).first()
    
    if not silinecek_model:
        raise HTTPException(status_code=404, detail="Böyle bir model bulunamadı!")

    if silinecek_model.owner_id != kullanici_id:
        raise HTTPException(status_code=403, detail="Erişim reddedildi: Sadece kendi modellerinizi silebilirsiniz!")

    db.delete(silinecek_model)
    db.commit()
    
    return {"mesaj": f"ID'si {model_id} olan model başarıyla silindi!"}
