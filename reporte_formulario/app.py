from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify, flash, session
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
import psycopg2
from funciones import enviar_mail, generar_pdf, conectar_bd
import os
from dotenv import load_dotenv

#----------PRUEBA--------------
load_dotenv()
#Prueba de git desarrollo a produccion

# Obtener el host y el puerto desde las variables de entorno
host = os.getenv("FLASK_HOST", "0.0.0.0")  # Valor por defecto: '0.0.0.0'
port = int(os.getenv("FLASK_PORT", 5000))  # Valor por defecto: 5000

app = Flask(__name__)

#MENSAJE DE PRUEBA

app.secret_key = os.getenv("SECRET_KEY")
usuarios = {
    'ssanchez': 'Emer1234',
    'acastillo': 'Emer1234',
    'acaballero': 'Emer1234',
    'jbordon': 'Emer1234',
    'erlopez': 'Emer1234',
    'yel':'Pami1234',
    'eaguirre':'Emer1234',   
    'amaguirre':'Emer1234',
    'lunrodriguez':'Emer1234',
    'gtesta':'Emer1234',
    'tobetko':'Emer1234',
    'jantunez': 'Pami1234',
    'slopez': 'Pami1234',
}


#aaa

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        if usuario in usuarios and usuarios[usuario] == contrasena:
            # Autenticación exitosa, redireccionar al inicio de la aplicación
            session['usuario'] = usuario  # Guardar el usuario en la sesión
            return redirect(url_for('index'))
        else:
            # Autenticación fallida, mostrar mensaje de error
            flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html')


@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/formulario_entrega')
def formulario():
    
    return render_template('formulario_entrega.html')


@app.route('/formulario_devolucion', methods=['GET', 'POST'])
def formulario_devolucion():
    conn = conectar_bd()
    cur = conn.cursor()
    
    try:
        asignado = request.form.get('asignado')  # Obtener el valor del campo "asignado" del formulario
        cur.execute(f"SELECT dispositivo FROM entrega WHERE asignado = '{asignado}' ")
        resultados = cur.fetchall()  # Recupera todos los resultados de la consulta
    except psycopg2.Error as e:
        print("Error al ejecutar la consulta SQL:", e)
        resultados = []
    finally:
        cur.close()
        conn.close()
    
    return render_template('resultados.html', dispositivos=resultados)

@app.route('/buscar_usuarios')
def buscar_usuarios():
    usuario = request.args.get('usuario', '').lower()

    # Conexión a la base de datos
    conn = conectar_bd()
    cursor = conn.cursor()

    try:
        # Ejecutar consulta SQL
        cursor.execute("SELECT dispositivo, modelo, fecha, devuelto, id, asignado, etiqueta FROM entrega WHERE lower(asignado) = lower (%s) and devuelto = 'F' order by id desc ", (usuario,))
        dispositivos = cursor.fetchall()
        return render_template('resultados.html', dispositivos=dispositivos, pagination=False)
    except psycopg2.Error as e:
        print("Error al ejecutar la consulta:", e)
    finally:
        cursor.close()
        conn.close()

    return render_template('resultados.html', dispositivos=[])

@app.route('/devolver', methods=['POST'])
def devolver_dispositivo():
    dispositivo_id = request.form.get('dispositivo_id')

    # Conectar a la base de datos
    conn = conectar_bd()
    cur = conn.cursor()

    try:
        # Obtener el dispositivo devuelto para poder actualizar el inventario
        cur.execute("SELECT dispositivo, leasing FROM entrega WHERE id = %s", (dispositivo_id,))
        dispositivo = cur.fetchone()

        if dispositivo:
            dispositivo_nombre = dispositivo[0]
            leasing = dispositivo[1]  # Asumiendo que el campo leasing es un booleano (True/False)

            # Actualizar el estado del dispositivo en la tabla 'entrega' a 'devuelto'
            cur.execute("UPDATE entrega SET devuelto = 'T' WHERE id = %s", (dispositivo_id,))
            conn.commit()

            # Validación para saber si es un dispositivo de leasing
            if leasing:  # Si el dispositivo es de leasing
                # Aumentar la cantidad de 'LEASING' en el inventario
                cur.execute("""
                    UPDATE inventario 
                    SET cantidad = cantidad + 1 
                    WHERE producto = 'LEASING'
                """)
            else:  # Si el dispositivo no es de leasing
                # Aumentar la cantidad en el inventario según el nombre del dispositivo
                cur.execute("""
                    UPDATE inventario 
                    SET cantidad = cantidad + 1 
                    WHERE producto = %s
                """, (dispositivo_nombre,))

            conn.commit()



    except psycopg2.Error as e:
        print("Error al devolver el dispositivo:", e)
        conn.rollback()

    finally:
        cur.close()
        conn.close()

    # Redireccionar a la página de resultados actualizada
    return redirect(url_for('buscar_usuarios'))


from flask import redirect

@app.route('/devolver_todo', methods=['POST'])
def devolver_todo():
    usuario = request.form.get('usuario').upper()
    print('el usuario es: ')
    print(usuario)
    usuario = usuario.lower()

    conn = conectar_bd()
    cur = conn.cursor()
    
    try:
        #cur.execute("UPDATE entrega SET devuelto = 'T' WHERE asignado = %s ", (usuario, ))
        cur.execute("UPDATE entrega SET devuelto = 'T' WHERE lower(asignado) = %s", (usuario,))
        conn.commit()
    except psycopg2.Error as e:
        print("Error al actualizar el estado del dispositivo:", e)
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('buscar_usuarios'))



@app.route('/generar_reporte', methods=['POST'])
def generar_reporte():
    # Obtener los datos del formulario
    form_data = request.form

    # Extraer los datos del formulario
    dispositivo = form_data.get('dispositivo', '').upper()
    modelo = form_data.get('modelo', '').upper()
    etiqueta = form_data.get('etiqueta', '').upper().replace(" ","")
    accesorios = form_data.get('accesorios', '').upper()
    asignado = form_data.get('asignado', '').upper()
    numero_ticket = form_data.get('nro_ticket', '')
    tecnico = form_data.get('tecnico', '').upper()
    fecha = form_data.get('fecha', '')
    observaciones = form_data.get('observaciones', '')
    nro_telefono = form_data.get('nro_telefono', '')
    organismo = form_data.get('organismo','').upper()
    ceco = form_data.get('ceco','').upper()
    leasing = form_data.get('leasing','') == 'on'
  
    

    try:
        # Formatear la fecha
        fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')
        print(fecha)

        # Insertar datos en la base de datos
        conn = conectar_bd()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO entrega 
            (dispositivo, etiqueta, accesorios, asignado, numero_ticket, tecnico, fecha, modelo, observaciones, nro_telefono, devuelto, organismo, ceco, leasing) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'F', %s, %s, %s) 
            RETURNING id""",
            (dispositivo, etiqueta, accesorios, asignado, numero_ticket, tecnico, fecha, modelo, observaciones, nro_telefono, organismo, ceco, leasing))
        
        conn.commit()
        ultimo_id = cur.fetchone()[0]

      
        # Actualizar la cantidad en el inventario   
        if dispositivo != 'LAPTOP' and leasing ==False and organismo != 'PAMI':
            cur.execute("""
                UPDATE inventario 
                SET cantidad = cantidad - 1 
                WHERE producto = %s AND cantidad > 0
            """, (dispositivo,))
            
            conn.commit()

        if organismo == 'PAMI' :
            cur.execute("""
                UPDATE inventario_pami 
                SET cantidad = cantidad - 1 
                WHERE producto = %s AND cantidad > 0
            """, (dispositivo,))
            
            conn.commit()

        if leasing == True:
            cur.execute("""
                UPDATE inventario 
                SET cantidad = cantidad - 1 
                WHERE producto = 'LEASING'
            """)
            conn.commit()

        # Generar el PDF
        pdf_bytes = generar_pdf(dispositivo, modelo, etiqueta, accesorios, asignado, numero_ticket, tecnico, fecha, observaciones, ultimo_id, nro_telefono)

        # Enviar el PDF por correo electrónico siempre que el organismo no sea de PAMI
        if organismo != 'PAMI':
            enviar_mail(pdf_bytes, ultimo_id, asignado, fecha)

        # Crear una respuesta HTTP
        response = make_response(pdf_bytes)

        # Obtener la fecha actual
        fecha_actual = datetime.now()
        anio = fecha_actual.strftime("%Y")
        mes = fecha_actual.strftime("%m")
        dia = fecha_actual.strftime("%d")
        
        # Directorio donde se guardará el archivo
        directorio_destino = os.path.join('D:\\', anio, mes, dia)
        
        # Verificar si el directorio destino existe, si no, crearlo
        if not os.path.exists(directorio_destino):
            os.makedirs(directorio_destino)
        

        # Configurar el encabezado Content-Disposition para establecer el nombre del archivo
        response.headers['Content-Disposition'] = f'inline; filename={ultimo_id}-{asignado}-{fecha}.pdf'

        nombre_archivo = f'{ultimo_id}-{asignado}-{fecha}.pdf'
        ruta_archivo = os.path.join(directorio_destino, nombre_archivo)

        # Establecer el tipo de contenido como PDF
        response.mimetype = 'application/pdf'

        with open(ruta_archivo, 'wb') as archivo:
            archivo.write(pdf_bytes)

        return response

    except psycopg2.Error as e:
        print("Error al insertar datos en la base de datos:", e)
        return "Error al generar el reporte", 500
    finally:
        cur.close()
        conn.close()

@app.route('/stock')
def stock():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute('SELECT producto, cantidad FROM inventario order by producto asc;')
    inventario = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('stock.html', inventario=inventario)

@app.route('/agregar_item', methods=['GET', 'POST'])
def agregar_item():
    if request.method == 'POST':
        producto = request.form['producto'].upper()
        cantidad = request.form['cantidad'].upper()
        
        conn = conectar_bd()
        cur = conn.cursor()
        
        try:
            cur.execute("INSERT INTO inventario (producto, cantidad) VALUES (%s, %s)", (producto, cantidad))
            conn.commit()
            flash('Item agregado exitosamente', 'success')
            return redirect(url_for('stock'))
        except psycopg2.Error as e:
            print("Error al insertar en la base de datos:", e)
            conn.rollback()
            flash('Error al agregar el item', 'error')
        finally:
            cur.close()
            conn.close()

    return render_template('agregar_item.html')

@app.route('/agregar_stock', methods=['GET', 'POST'])
def agregar_stock():
    if request.method == 'POST':
        producto = request.form['producto'].upper()
        cantidad = int(request.form['cantidad'])

        conn = conectar_bd()
        cur = conn.cursor()
        try:
            # Verificar si el producto ya existe
            cur.execute("SELECT cantidad FROM inventario WHERE producto = %s", (producto,))
            resultado = cur.fetchone()

            if resultado:
                # Actualizar la cantidad existente
                cur.execute("UPDATE inventario SET cantidad = cantidad + %s WHERE producto = %s", (cantidad, producto))
            else:
                # Insertar un nuevo producto si no existe
                cur.execute("INSERT INTO inventario (producto, cantidad) VALUES (%s, %s)", (producto, cantidad))

            conn.commit()
            flash('Stock actualizado exitosamente', 'success')
        except psycopg2.Error as e:
            print("Error al actualizar el stock:", e)
            conn.rollback()
            flash('Error al actualizar el stock', 'error')
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('stock'))

    # En caso de GET, obtenemos los productos para llenar el select
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("SELECT producto FROM inventario")
    productos = cur.fetchall()
    cur.close()
    conn.close()

    # Renderizamos la plantilla HTML pasando los productos
    return render_template('agregar_stock.html', productos=productos)

    
def obtener_productos():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("SELECT producto FROM inventario")
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return productos

@app.route('/restar_stock', methods=['GET', 'POST'])
def restar_stock():
    if request.method == 'POST':
        producto = request.form['producto'].upper()
        cantidad = int(request.form['cantidad'])

        conn = conectar_bd()
        cur = conn.cursor()
        
        try:
            # Verificar si el producto ya existe
            cur.execute("SELECT cantidad FROM inventario WHERE producto = %s", (producto,))
            resultado = cur.fetchone()

            if resultado:
                cantidad_actual = resultado[0]
                if cantidad_actual >= cantidad:
                    # Restar la cantidad
                    cur.execute("UPDATE inventario SET cantidad = cantidad - %s WHERE producto = %s", (cantidad, producto))
                    flash('Stock restado exitosamente', 'success')
                else:
                    flash('No hay suficiente stock para restar', 'error')
            else:
                flash('El producto no existe en el inventario', 'error')

            conn.commit()
        except psycopg2.Error as e:
            print("Error al restar el stock:", e)
            conn.rollback()
            flash('Error al restar el stock', 'error')
        finally:
            cur.close()
            conn.close()
        
        return redirect(url_for('stock'))

    # En caso de GET, obtenemos los productos para llenar el select
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("SELECT producto FROM inventario")
    productos = cur.fetchall()
    cur.close()
    conn.close()

    # Renderizamos la plantilla HTML pasando los productos
    return render_template('restar_stock.html', productos=productos)

#---------------------------------------------------------------------------------------
@app.route('/stock_pami')
def stock_pami():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute('SELECT producto, cantidad FROM inventario_pami ORDER BY producto ASC;')
    inventario = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('stock_pami.html', inventario=inventario)

@app.route('/agregar_item_pami', methods=['GET', 'POST'])
def agregar_item_pami():
    if request.method == 'POST':
        producto = request.form['producto'].upper()
        cantidad = request.form['cantidad'].upper()
        
        conn = conectar_bd()
        cur = conn.cursor()
        
        try:
            cur.execute("INSERT INTO inventario_pami (producto, cantidad) VALUES (%s, %s)", (producto, cantidad))
            conn.commit()
            flash('Item agregado exitosamente', 'success')
            return redirect(url_for('stock_pami'))
        except psycopg2.Error as e:
            print("Error al insertar en la base de datos:", e)
            conn.rollback()
            flash('Error al agregar el item', 'error')
        finally:
            cur.close()
            conn.close()

    return render_template('agregar_item_pami.html')

@app.route('/agregar_stock_pami', methods=['GET', 'POST'])
def agregar_stock_pami():
    if request.method == 'POST':
        producto = request.form['producto'].upper()
        cantidad = int(request.form['cantidad'])

        conn = conectar_bd()
        cur = conn.cursor()
        try:
            cur.execute("SELECT cantidad FROM inventario_pami WHERE producto = %s", (producto,))
            resultado = cur.fetchone()

            if resultado:
                cur.execute("UPDATE inventario_pami SET cantidad = cantidad + %s WHERE producto = %s", (cantidad, producto))
            else:
                cur.execute("INSERT INTO inventario_pami (producto, cantidad) VALUES (%s, %s)", (producto, cantidad))

            conn.commit()
            flash('Stock actualizado exitosamente', 'success')
        except psycopg2.Error as e:
            print("Error al actualizar el stock:", e)
            conn.rollback()
            flash('Error al actualizar el stock', 'error')
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('stock_pami'))

    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("SELECT producto FROM inventario_pami")
    productos = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('agregar_stock_pami.html', productos=productos)

@app.route('/restar_stock_pami', methods=['GET', 'POST'])
def restar_stock_pami():
    if request.method == 'POST':
        producto = request.form['producto'].upper()
        cantidad = int(request.form['cantidad'])

        conn = conectar_bd()
        cur = conn.cursor()
        
        try:
            cur.execute("SELECT cantidad FROM inventario_pami WHERE producto = %s", (producto,))
            resultado = cur.fetchone()

            if resultado:
                cantidad_actual = resultado[0]
                if cantidad_actual >= cantidad:
                    cur.execute("UPDATE inventario_pami SET cantidad = cantidad - %s WHERE producto = %s", (cantidad, producto))
                    flash('Stock restado exitosamente', 'success')
                else:
                    flash('No hay suficiente stock para restar', 'error')
            else:
                flash('El producto no existe en el inventario', 'error')

            conn.commit()
        except psycopg2.Error as e:
            print("Error al restar el stock:", e)
            conn.rollback()
            flash('Error al restar el stock', 'error')
        finally:
            cur.close()
            conn.close()
        
        return redirect(url_for('stock_pami'))

    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("SELECT producto FROM inventario_pami")
    productos = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('restar_stock_pami.html', productos=productos)


#---------------------------------------------------------------------------------------
@app.route('/leasing')
def leasing():
    conn = conectar_bd()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT etiqueta, modelo, asignado, fecha, tecnico
            FROM entrega
            WHERE leasing = TRUE and devuelto = FALSE
            ORDER BY id DESC
        """)
        rows = cur.fetchall()

        # Reformatar las fechas al formato dd/mm/yyyy
        datos = [
            (row[0], row[1], row[2], row[3].strftime('%d/%m/%Y'), row[4])
            for row in rows
        ]
                # Consulta para contar los registros
        cur.execute("""
            SELECT COUNT(*)
            FROM entrega
            WHERE leasing = TRUE and devuelto = FALSE
        """)
        total_entregados = cur.fetchone()[0]

        cur.execute("""
                select cantidad from inventario                 
                WHERE producto = 'LEASING'
            """)
        restantes = cur.fetchone()[0]


        conn.commit()
# Calcular stock restante
        stock_inicial = 150
        stock_restante = stock_inicial - total_entregados
    except psycopg2.Error as e:
        print("Error al ejecutar la consulta:", e)
        datos = []
    finally:
        cur.close()
        conn.close()

    return render_template('leasing.html', datos=datos, total_entregados=total_entregados, restantes=restantes)

@app.route('/reportes')
def reportes():
    return render_template ('reportes.html')

if __name__ == '__main__':
     app.run(host=host, port=port)

#if __name__ == '__main__':
#    app.run(debug=True)fd