from flask import Flask, render_template, request, send_file, abort
import requests
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from io import BytesIO
import os

app = Flask(__name__)

BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:8000')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar-pdf', methods=['POST'])
def generar_pdf():

    try:
        id_factura = request.form['id_factura']

        response = requests.get(
            f'{BACKEND_URL}/facturas/v1/{id_factura}'
        )

        if response.status_code != 200:
            abort(404, description="Factura no encontrada")

        factura = response.json()

        # Crear buffer y documento PDF
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20
        )

        styles = getSampleStyleSheet()

        elements = []

        # Título
        titulo = Paragraph(
            f"<b>FACTURA #{factura['numero_factura']}</b>",
            styles['Title']
        )

        elements.append(titulo)
        elements.append(Spacer(1, 10))

        # Información empresa
        empresa = factura['empresa']

        info_empresa = Paragraph(
            f"""
            <b>Empresa:</b> {empresa['nombre']}<br/>
            <b>Dirección:</b> {empresa['direccion']}<br/>
            <b>Teléfono:</b> {empresa['telefono']}<br/>
            <b>Email:</b> {empresa['email']}
            """,
            styles['BodyText']
        )

        elements.append(info_empresa)
        elements.append(Spacer(1, 10))

        # Información cliente
        cliente = factura['cliente']

        info_cliente = Paragraph(
            f"""
            <b>Cliente:</b> {cliente['nombre']}<br/>
            <b>Dirección:</b> {cliente['direccion']}<br/>
            <b>Teléfono:</b> {cliente['telefono']}
            """,
            styles['BodyText']
        )

        elements.append(info_cliente)
        elements.append(Spacer(1, 15))

        # Tabla detalle factura
        data = [
            ['Cantidad', 'Descripción', 'Precio Unitario', 'Total']
        ]

        for item in factura['detalle']:
            data.append([
                item['cantidad'],
                item['descripcion'],
                f"${item['precio_unitario']}",
                f"${item['total']}"
            ])

        tabla = Table(data, colWidths=[30*mm, 60*mm, 40*mm, 40*mm])

        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),

            ('GRID', (0, 0), (-1, -1), 1, colors.black),

            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

            ('BACKGROUND', (0, 1), (-1, -1), colors.beige)
        ]))

        elements.append(tabla)
        elements.append(Spacer(1, 15))

        # Totales
        totales = Paragraph(
            f"""
            <b>Subtotal:</b> ${factura['subtotal']}<br/>
            <b>Impuesto:</b> ${factura['impuesto']}<br/>
            <b>Total:</b> ${factura['total']}
            """,
            styles['BodyText']
        )

        elements.append(totales)

        # Generar PDF
        doc.build(elements)

        buffer.seek(0)

        # Retornar PDF
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{id_factura}.pdf",
            mimetype='application/pdf'
        )

    except requests.exceptions.ConnectionError:
        abort(503, description="Error de conexión con el servidor")

    except Exception as e:
        abort(500, description=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)