import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(secure=True)

def upload_imagem_cloudinary(arquivo):
    try:
        if hasattr(arquivo, "file"):
            arquivo.file.seek(0)
            resposta = cloudinary.uploader.upload(arquivo.file, folder="stef_produtos")
        else:
            resposta = cloudinary.uploader.upload(arquivo, folder="stef_produtos")
        return resposta.get("secure_url") or resposta.get("url")
    except Exception as e:
        print(f"Erro no upload para Cloudinary: {e}")
        return None
