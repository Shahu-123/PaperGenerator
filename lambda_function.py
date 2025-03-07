import boto3
import sqlite3
from PIL import Image
import tempfile
import io
import generator
import json
import base64

def lambda_handler(event, context):
    # Initialize S3 client
    s3 = boto3.client('s3')

    # Download the SQLite database file from S3
    s3_bucket = 'shahu-exam'
    s3_key = 'examcopy.db'
    local_file_path = '/tmp/my-database.db'  # Local file path to download the SQLite database
    s3.download_file(s3_bucket, s3_key, local_file_path)
    
    raw_paper = generator.exam(event['topic'], event['mark'], event['subjectId'], event['info'])
    if raw_paper == "Error":
        url = "Error"
    else:
        x = raw_paper[0]
        pdf_filename = "/tmp/shahu.pdf"
        x.save(pdf_filename, "PDF", resolution=100.0, save_all=True, append_images=raw_paper[1:])
        object_name = "new-exam.pdf"
        s3.upload_file(pdf_filename, "shahu-exam", object_name)
        
        url = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': 'shahu-exam',
            'Key': object_name
        },
        ExpiresIn=3600  # URL will expire in 1 hour
        )
        
        with open(pdf_filename, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
            base64_pdf_data = base64.b64encode(pdf_data).decode('utf-8')
    
    

    response = {
        'statusCode': 200,
        'url': json.dumps(url)
    }
    
    return response
