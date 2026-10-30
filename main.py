
from fastapi import FastAPI, UploadFile, File, HTTPException
import boto3
import os
from botocore.exceptions import ClientError

app = FastAPI()

# S3 bucket configuration
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

if not BUCKET_NAME:
    raise ValueError("S3_BUCKET_NAME environment variable is not set")

# Create S3 client using EC2 IAM Role
s3 = boto3.client("s3")


@app.get("/")
def home():
    return {"message": "FastAPI server is running!"}


# Upload file to S3
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        s3.upload_fileobj(
            file.file,
            BUCKET_NAME,
            file.filename
        )

        return {
            "message": "File uploaded successfully",
            "filename": file.filename
        }

    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        await file.close()


# List files from S3
@app.get("/files")
def list_files():
    try:
        response = s3.list_objects_v2(
            Bucket=BUCKET_NAME
        )

        files = [
            obj["Key"] for obj in response.get("Contents", [])
        ]

        return {"files": files}

    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Download file using presigned URL
@app.get("/download/{filename}")
def download_file(filename: str):
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": filename
            },
            ExpiresIn=300
        )

        return {
            "message": "Download URL generated successfully",
            "download_url": url
        }

    except ClientError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Delete file from S3
@app.delete("/delete/{filename}")
def delete_file(filename: str):
    try:
        s3.delete_object(
            Bucket=BUCKET_NAME,
            Key=filename
        )

        return {"message": "File deleted successfully"}

    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
