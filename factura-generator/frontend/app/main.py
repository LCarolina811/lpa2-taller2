from flask import Flask, render_template, request, send_file
import requests
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)

API_URL = "http://backend:8000"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generar", methods=["POST"])
def generar():

    numero = request.form["numero_factura"]

    response = requests.get(
        f"{API_URL}/facturas/v1/{numero}"
    )

    factura = response.json()

    buffer = BytesIO()

    pdf = canvas.Canvas(buffer)

    pdf.drawString(100, 800, f"Factura: {factura['numero_factura']}")
    pdf.drawString(100, 780, f"Cliente: {factura['cliente']['nombre']}")
    pdf.drawString(100, 760, f"Total: ${factura['total']}")

    y = 720

    for item in factura["detalle"]:
        texto = f"{item['descripcion']} - {item['cantidad']} x ${item['precio_unitario']}"
        pdf.drawString(100, y, texto)
        y -= 20

    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{numero}.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)