from fastapi import FastAPI, Response
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import textwrap
import threading
import os

app = FastAPI()
lock = threading.Lock()
COUNTER_FILE = "counter.txt"

class FormData(BaseModel):
    exporter: str
    consignee: str
    pre_carriage_by: str
    place_of_receipt: str
    vessel_flight_no: str
    port_of_loading: str
    lc_no: str
    port_of_discharge: str
    final_destination: str
    bl_awb_no: str
    marks_nosandcontainer_no: str
    num_and_kind_of_pkgs: str
    description_of_goods: str
    quantity: str
    destination: str
    consignor: str
    invoice_number: str
    manufacturer: str
    nationality: str
    total_quantity: str
    date: str
    exporter_signature: str
    certification_place: str

def get_next_counter():
    with lock:
        if not os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "w") as f:
                f.write("1")
            return 1
        with open(COUNTER_FILE, "r+") as f:
            count = int(f.read())
            f.seek(0)
            f.write(str(count + 1))
            f.truncate()
            return count

@app.post("/generate-origin-pdf/")
async def generate_origin_pdf(data: FormData):
    pdf_number = get_next_counter()
    filename = f"origin_certificate_{pdf_number}.pdf"

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    image_path = "Certificate of Origin (CII)_page-0001.jpg"
    try:
        c.drawImage(ImageReader(image_path), 0, 0, width=width, height=height)
    except Exception as e:
        c.drawString(100, 800, f"Error loading image: {str(e)}")

    c.setFont("Helvetica", 9)

    # ✅ Exporter (multiline)
    exporter_lines = textwrap.wrap(data.exporter, width=45)
    for i, line in enumerate(exporter_lines):
        c.drawString(60, 730 - i * 12, line)

    # ✅ Consignee (multiline)
    consignee_lines = textwrap.wrap(data.consignee, width=45)
    for i, line in enumerate(consignee_lines):
        c.drawString(60, 615 - i * 12, line)

    # ✅ Single-line fields
    c.drawString(60, 525, data.pre_carriage_by)
    c.drawString(160, 525, data.place_of_receipt)
    c.drawString(60, 495, data.vessel_flight_no)
    c.drawString(160, 495, data.port_of_loading)
    c.drawString(300, 495, data.lc_no)
    c.drawString(60, 465, data.port_of_discharge)
    c.drawString(160, 465, data.final_destination)
    c.drawString(300, 465, data.bl_awb_no)

    # ✅ Marks/Kind/Desc/Qty in table row (aligned)
    marks_lines = textwrap.wrap(data.marks_nosandcontainer_no, width=22)
    kind_lines = textwrap.wrap(data.num_and_kind_of_pkgs, width=15)
    desc_lines = textwrap.wrap(data.description_of_goods, width=22)
    qty_lines = textwrap.wrap(data.quantity, width=10)
    max_lines = max(len(marks_lines), len(kind_lines), len(desc_lines), len(qty_lines))
    def pad(lines, count): return lines + [""] * (count - len(lines))
    marks_lines = pad(marks_lines, max_lines)
    kind_lines = pad(kind_lines, max_lines)
    desc_lines = pad(desc_lines, max_lines)
    qty_lines = pad(qty_lines, max_lines)
    start_y = 410
    for i in range(max_lines):
        c.drawString(55, start_y - i * 12, marks_lines[i])
        c.drawString(150, start_y - i * 12, kind_lines[i])
        c.drawString(280, start_y - i * 12, desc_lines[i])
        c.drawString(420, start_y - i * 12, qty_lines[i])

    # ✅ Bottom section
    c.drawString(130, 300, data.destination)
    c.drawString(130, 265, data.consignor)
    c.drawString(140, 235, data.invoice_number)
    c.drawString(130, 220, data.manufacturer)
    c.drawString(130, 200, data.nationality)
    c.drawString(470, 160, data.total_quantity) 
    c.drawString(100, 40,  data.date)
    c.drawString(100, 25, data.certification_place)
    c.drawString(200, 50, data.exporter_signature)

    c.showPage()
    c.save()
    buffer.seek(0)

    return Response(
        content=buffer.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
