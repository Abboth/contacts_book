import logging
from enum import Enum
from io import BytesIO
from urllib.parse import urlparse

import qrcode

import cloudinary
from cloudinary import api, uploader
from cloudinary.utils import cloudinary_url
from fastapi import HTTPException

from src.core.config import configuration

logging.basicConfig(level=logging.INFO)


class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=configuration.CLOUDINARY_CLOUD,
            api_key=configuration.CLOUDINARY_API_KEY,
            api_secret=configuration.CLOUDINARY_SECRET_KEY,
            secure=True,
        )

    class ImageTransformation(str, Enum):
        sepia = "sepia"
        grayscale = "grayscale"
        blur = "blur"
        art_audrey = "art:audrey"
        art_grayscale = "art:grayscale"
        art_sepia = "art:sepia"

    @staticmethod
    async def upload_file(file, folder: str, public_id: str, transformation: dict = None) -> str:
        upload_result = cloudinary.uploader.upload(
            file,
            folder=folder,
            public_id=public_id,
            overwrite=True
        )
        final_public_id = f"{folder}/{public_id}"

        url, _ = cloudinary_url(
            final_public_id,
            transformation=transformation,
            version=upload_result.get("version")
        )
        return url

    async def create_qr_code(self, link: str, folder: str, public_id: str) -> str:
        qr = qrcode.QRCode()
        qr.add_data(link)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        qr_link = await self.upload_file(img_buffer, folder, public_id)

        return qr_link

    @staticmethod
    async def get_public_id_from_url(url: str) -> str:
        path = urlparse(url).path
        parts = path.split('/')
        public_id_parts = parts[-3:]
        public_id = '/'.join(public_id_parts)
        return public_id

    async def delete_file(self, public_id: str) -> None:
        public_id = await self.get_public_id_from_url(public_id)
        try:
            cloudinary.uploader.destroy(public_id)
        except HTTPException as err:
            logging.info(err)

    @staticmethod
    async def delete_user_files(email: str) -> None:
        try:
            cloudinary.api.delete_folder(email)
        except HTTPException as err:
            logging.info(err)


cloudinary_services = CloudinaryService()
