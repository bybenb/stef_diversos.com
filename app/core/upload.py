import cloudinary
import cloudinary.uploader
import os


cloudinary.config(secure=True)

def upload_imagem_cloudinary(arquivo):
    try:
        resposta = cloudinary.uploader.upload(arquivo.file)
        return resposta["secure_url"]
    except Exception as e:
        print(f"Erro no upload: {e}")
        return None