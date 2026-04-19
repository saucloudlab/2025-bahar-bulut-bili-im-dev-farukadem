from minio import Minio
import io
import json

# Python'un MinIO'ya ulaşması için İç Ağ adını kullanıyoruz:
MINIO_INTERNAL_ENDPOINT = "minio:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "deneme60605252" 

client = Minio(
    MINIO_INTERNAL_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

bucket_name = "modeller"

# Kova yoksa oluştur
if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)

# Dünyaya Okuma İzni Ver (Policy)
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
        }
    ]
}
client.set_bucket_policy(bucket_name, json.dumps(policy))

def upload_file(file_name, file_data, content_type):
    client.put_object(
        bucket_name,
        file_name,
        io.BytesIO(file_data),
        length=len(file_data),
        content_type=content_type
    )
    return f"http://94.138.211.148:9000/{bucket_name}/{file_name}"
