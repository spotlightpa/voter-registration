import boto3
import os
from pathlib import Path

def upload_to_s3():
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    aws_region = os.environ.get('AWS_REGION')
    
    if not bucket_name:
        raise ValueError("S3_BUCKET_NAME environment variable is not set")
    
    s3_client = boto3.client(
        's3',
        region_name=aws_region,
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )
    
    processed_dir = Path("data/processed")
    s3_base_path = "2025/voter-registration/"
    
    print(f"Uploading to bucket: {bucket_name}")
    print(f"S3 path: {s3_base_path}")
    
    if not processed_dir.exists():
        print(f"Warning: {processed_dir} does not exist")
        return
    
    uploaded_files = []
    for file_path in processed_dir.glob("*"):
        if file_path.is_file():

            s3_key = f"{s3_base_path}{file_path.name}"
            
            content_type = get_content_type(file_path.suffix)
            
            try:
                s3_client.upload_file(
                    str(file_path),
                    bucket_name,
                    s3_key,
                    ExtraArgs={
                        'ACL': 'public-read',
                        'ContentType': content_type
                    }
                )
                
                public_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{s3_key}"
                
                print(f"✓ Uploaded: {file_path.name}")
                print(f"  URL: {public_url}")
                uploaded_files.append(public_url)
                
            except Exception as e:
                print(f"Failed to upload {file_path.name}: {str(e)}")
    
    print(f"\nTotal files uploaded: {len(uploaded_files)}")
    return uploaded_files

def get_content_type(extension):
    content_types = {
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.csv': 'text/csv',
        '.json': 'application/json',
        '.txt': 'text/plain'
    }
    return content_types.get(extension.lower(), 'application/octet-stream')

if __name__ == "__main__":
    upload_to_s3()