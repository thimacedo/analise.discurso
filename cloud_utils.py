import boto3
import os
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

def upload_results_to_s3(file_list):
    """
    Realiza o upload dos artefatos da análise para o Amazon S3.
    """
    bucket = os.getenv('AWS_BUCKET_NAME')
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION', 'us-east-1')

    if not all([bucket, access_key, secret_key]):
        print("⚠️ Cloud Storage: Credenciais AWS não configuradas. Pulando upload.")
        return False

    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        for file_path in file_list:
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                print(f"  ☁️ Enviando {file_name} para o S3...")
                s3.upload_file(
                    file_path, 
                    bucket, 
                    file_name,
                    ExtraArgs={'ACL': 'public-read'} # Torna o arquivo legível pela Vercel
                )
            else:
                print(f"  ! Arquivo não encontrado para upload: {file_path}")
        
        print("✅ Sincronização com Cloud concluída.")
        return True
    except NoCredentialsError:
        print("❌ AWS: Credenciais inválidas.")
        return False
    except Exception as e:
        print(f"❌ Erro no upload para S3: {e}")
        return False
