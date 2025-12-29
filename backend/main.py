from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os, uuid
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
from docx import Document

app = FastAPI()

UPLOADS = "uploads"
os.makedirs(UPLOADS, exist_ok=True)

@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    pdf_path = f"{UPLOADS}/{uuid.uuid4()}.pdf"
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    images = convert_from_path(pdf_path, dpi=300)
    doc = Document()

    for img in images:
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        img = cv2.threshold(
            img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

        text = pytesseract.image_to_string(
            img, lang="eng", config="--oem 3 --psm 6"
        )
        doc.add_paragraph(text)

    output = f"{UPLOADS}/{uuid.uuid4()}.docx"
    doc.save(output)

    return FileResponse(output, filename="output.docx")

