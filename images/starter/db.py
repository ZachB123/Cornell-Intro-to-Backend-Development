import base64
import boto3 #aws
import datetime
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from mimetypes import guess_extension, guess_type #images/png -> guess_extension -> .png
import os
from PIL import Image
import random
import re #regular expression
import string


db = SQLAlchemy()

EXTENSIONS = ["png", "gif", "jpg", "jpeg"]

BASE_DIR = os.getcwd() #get current working directory
S3_BUCKET = "zachdemo8"
S3_BASE_URL = f"https://{S3_BUCKET}.s3-us-east-2.amazonaws.com"

class Asset(db.Model):
    __tablename__ = "asset"
    id = db.Column(db.Integer, primary_key=True)
    base_url = db.Column(db.String, nullable=False)
    salt = db.Column(db.String, nullable=False)
    extensions = db.Column(db.String, nullable=False) #extension of file
    height = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, **kwargs):
        self.create(kwargs.get("image_data")) #image data is the base 64 string we passed in
        # data:image/png;base64,sjlhsadk gskhgksmvghdf

    def serialize(self):
        return {
            "url": f"{self.base_url}/{self.salt}.{self.extension}",
            "created_at": str(self.created_at)
        }

    def create(self, image_data):
        try:
            ext = guess_extension(guess_type(image_data)[0])[1:]
            if ext not in EXTENSIONS:
                raise Exception(f"Extension {ext} not supported")
            salt = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(16))

            img_str = re.sub("^data:image/.+;base64,", "", image_data)
            img_data = base64.decode(img_str)
            img = Image.open(BytesIO(img_data))

            self.base_url = S3_BASE_URL
            self.salt = salt
            self.extension = ext
            self.height = img.height
            self.width = img.width
            self.created_at = datetime.datetime.now()

            img_filename = f"{salt}.{ext}"
            self.upload(img, img_filename)

        except Exception as e:
            print("error:", e)

    def upload(self, img, img_filename):
        try:
            img_temploc = f"{BASE_DIR}/{img_filename}"
            img.save(img_temploc)

            s3_client = boto3.client("s3")
            s3_client.upload_file(img_temploc, S3_BUCKET, img_filename)

            s3_resource = boto3.resource("s3")
            object_acl = s3_resource.ObjectAcl(S3_BUCKET, img_filename)
            object_acl.put(ACL="public-read")
            os.remove(img_temploc)
        except Exception as e:
            print("upload failed:", e)
