import boto3
import os
from botocore.exceptions import NoCredentialsError

def upload_para_s3(local_file, s3_name):
    bucket = os.getenv('AWS_BUCKET_NAME')
    s3 = boto3.client('s3', 
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    
    try:
        # ExtraArgs garante que o dashboard consiga ler o arquivo sem erro de permissão
        s3.upload_file(local_file, bucket, s3_name, ExtraArgs={
            'ACL': 'public-read',
            'ContentType': 'text/csv'
        })
        url = f"https://{bucket}.s3.amazonaws.com/{s3_name}"
        print(f"✅ Sincronizado: {url}")
        return url
    except Exception as e:
        print(f"❌ Erro no Upload S3: {e}")
        return None
