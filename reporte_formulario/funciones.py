from email.mime.text import MIMEText
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from smtplib import SMTP_SSL

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io
from datetime import datetime
import os

# Cargar variables de entorno desde un archivo .env (opcional)
from dotenv import load_dotenv


import psycopg2


load_dotenv()


ruta_logo = os.getenv('RUTA_LOGO')
def conectar_bd():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST")
        )
        return conn
    except psycopg2.Error as e:
        print("Error al conectar a la base de datos:", e)

def enviar_mail(pdf_bytes, ultimo_id, asignado, fecha):
    from_address = "entrega_activos@emergencias.com.ar"
    to_address = f'{asignado}@emergencias.com.ar'
    
    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = f'NO RESPONDER: Comprobante de entrega' # del usaurio {asignado}'

    # Attach PDF to the email
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(pdf_bytes)
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', f"attachment; filename={ultimo_id}-{asignado}-{fecha}.pdf")
    msg.attach(attachment)

    # Add message to the body
    msg.attach(MIMEText(f'En el siguiente correo se adjunta la solicitud de entrega del usuario  "{asignado}".\n\n\n\nSi No aun no recibio el equipo, ya se van a cominucar para pasar a retirarlo y firmar el comprobante en el lugar.\nNOTA: No es necesario imprimir el comprobante.' ))

    # Setup the SMTP server
    smtp = SMTP("srv-smtp01-mel", 25)
    #smtp.connect("outlook.office365.com", 587
    #smtp.starttls()
    smtp.ehlo()
    #smtp.login(from_address, "ctxztdfpqbwgfvcy")

    # Send the email
    smtp.sendmail(from_address, to_address, msg.as_string())
    smtp.quit()


def generar_pdf(dispositivo, modelo, etiqueta, accesorios, asignado, numero_ticket, tecnico, fecha, observaciones, ultimo_id, nro_telefono):

    fecha_formateada = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
    # Crear el lienzo del PDF
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)  

    #directorio_script = os.path.dirname(os.path.abspath(__file__))
    #ruta_logo = os.path.join(directorio_script, 'static', 'logo_emer.png')
    ruta_logo = os.getenv('RUTA_LOGO')
    #ruta_logo = "\\Desarrollo\\reporte_formulario\\static\\logo_emer.png"

    importante = "<br/><br/><br/><b>IMPORTANTE:</b> Los elementos entregados son para uso exclusivo como herramienta de trabajo para el despeño de mis actividades (no se permite colocar ningun tipo de decoracion sobre el equipo), con ocasion del vinculo laboral que nos une, quedando excluido su uso para fines personales <br/><br/> Asimismo, dejo constancia que me comprometo a su inmediata devolucion, en las mismas condiciones en que se me fuera entregada en la oportunidad de extincion de la relacion laboral, por cualquier causa o a requerimiento de la empresa <br/><br/> En caso de nodevolver los dispositivos que se entregaron como herramienta de trabajo, te haremos saber que podremos retener el importe por el valor equivalente de tu liquidacion final"
    # Definir los datos para la tabla
    data = [
        ["", "Detalle"],
        ["Dispositivo:", dispositivo],
        ["Modelo:", modelo],
        ["Etiqueta:", etiqueta],
        ["Accesorios:", accesorios],
        ["Asignado a:", asignado],
        ["Número de Ticket:", numero_ticket],
        ["Técnico:", tecnico],
        ["Fecha:", fecha_formateada],
        ["Observaciones",observaciones],
        ["Nro de entrega",ultimo_id]
        
    ]

    if nro_telefono:
            data.insert(3,["Número de teléfono:", nro_telefono])

    # Configurar estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Encabezado de tabla gris
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Color del texto blanco
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación central de todos los elementos
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente en negrita para encabezado
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Añadir un poco de espacio entre el encabezado y el resto de la tabla
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Color de fondo blanco para filas de datos
        ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Agregar bordes a todas las celdas
    ])

    # Crear la tabla
    tabla = Table(data)
    tabla.setStyle(style)

    # Ajustar el tamaño de las celdas
    tabla._argW[0] = 100  # Ancho de la primera columna
    tabla._argW[1] = 400  # Ancho de la segunda columna

    # Define el espacio adicional
    espacio_logo_tabla = Spacer(1, 20)

    # Agregar la imagen del logo de la empresa
    imagen_logo = Image(ruta_logo, width=150, height=70)

    # Añadir la tabla al PDF
    elementos = [imagen_logo, espacio_logo_tabla, tabla, Spacer(1, 50)]

    # Agregar la firma y la aclaración
    estilos = getSampleStyleSheet()
    firma = Paragraph("<br/><br/><br/><br/><br/><b>Firma:</b>___________________________", estilos['Normal'])
    aclaracion = Paragraph("<br/><br/><b>Aclaración:</b>______________________________", estilos['Normal'])
    nota = Paragraph(f"{importante}", estilos['Normal'])
    elementos.append(firma)
    elementos.append(aclaracion)
    elementos.append(nota)

    # Construir el PDF
    pdf.build(elementos)

    # Obtener el contenido del PDF como bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes




