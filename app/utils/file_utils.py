from fastapi import UploadFile, HTTPException
import shutil
import os

UPLOAD_FOLDER = "images/"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif"}

def validate_file(file: UploadFile, allowed_extensions=ALLOWED_EXTENSIONS, allowed_mime=ALLOWED_MIME_TYPES):
    filename = file.filename
    if not filename or "." not in filename:
        raise HTTPException(status_code=400, detail="Arquivo sem extensão válida")

    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Extensão '{ext}' não permitida")

    if file.content_type not in allowed_mime:
        raise HTTPException(status_code=400, detail=f"Tipo MIME '{file.content_type}' não permitido")

    return ext

def save_upload_file(upload_file: UploadFile, folder: str, filename: str, old_image: str):
    if old_image:
        caminho_imagem = os.path.join(UPLOAD_FOLDER, old_image)
        if os.path.exists(caminho_imagem):
            os.remove(caminho_imagem)

    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
    return filepath