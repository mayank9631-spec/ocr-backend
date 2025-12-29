from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PyPDF2 import PdfReader, PdfWriter
import os, uuid
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
from docx import Document

app = FastAPI()

# Create uploads folder
UPLOADS = "uploads"
os.makedirs(UPLOADS, exist_ok=True)

# Mount static folder to serve index.html
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# PDF -> Word OCR endpoint
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

# Edit PDF endpoint
@app.post("/edit")
async def edit_pdf(file: UploadFile = File(...), page_number: int = 0, new_text: str = ""):
    pdf_path = f"{UPLOADS}/{uuid.uuid4()}.pdf"
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        if i == page_number and new_text:
            # NOTE: Simple overwrite, for advanced editing use other libraries
            # PyPDF2 cannot directly write text; this is placeholder logic
            pass
        writer.add_page(page)

    output_path = f"{UPLOADS}/{uuid.uuid4()}_edited.pdf"
    with open(output_path, "wb") as f:
        writer.write(f)

    return FileResponse(output_path, filename="edited.pdf")
