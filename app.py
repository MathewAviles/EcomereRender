#IMPORTS
from flask import Flask,render_template,request,redirect,url_for,session, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, FloatField, TextAreaField, FileField
from wtforms.validators import DataRequired, NumberRange
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os,io
import base64
from PIL import Image
from flask_wtf import FlaskForm
from functools import wraps
from sqlalchemy import func

#DB INIT
db = SQLAlchemy()

#DB TABLES
#Table Producto
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.LargeBinary, nullable=True)  # Campo para almacenar la imagen como datos binarios

    def __repr__(self):
        return f'<Product {self.titulo}>'
    
#Tabla Usuario
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='normal')  # 'normal' or 'admin'

    def __init__(self, username, email, password, role='normal'):
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    


#APP INIT
#Conexion
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ecomerce_cgb2_user:9oba2RXPeY23ahKktYqC1iSDpmUsaTP6@dpg-co9itjdjm4es73b03700-a.oregon-postgres.render.com/ecomerce_cgb2'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.secret_key = 'tu_clave_secreta'  # Clave secreta para las sesiones


    db.init_app(app)

    with app.app_context():
        db.create_all()
    return app
app=create_app()

#DECORADOR
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica si el usuario está autenticado y tiene el rol de administrador
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user.role == 'admin':
                # Si el usuario es un administrador, permite el acceso a la ruta
                return f(*args, **kwargs)
        # Si el usuario no está autenticado o no tiene el rol de administrador, redirige a la página de inicio
        flash('No tienes permisos para acceder a esta página.', 'error')
        return redirect(url_for('home'))
    return decorated_function


#ROUTES
#Ruta principal home
@app.route('/')
def home():
    productos = Product.query.all()
    for producto in productos:
        producto.imagen = convertir_imagen_base64(producto.imagen)  # Convierte la imagen a base64
    return render_template('home.html', productos=productos)


#ROUTES
#Ruta principal home
@app.route('/improplac')
def improplac():
    return render_template('improplac.html')


# Agrega una nueva ruta para el registro de usuarios
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    # Verifica si el usuario ya está autenticado, si es así, redirige a la página principal
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    # Verifica si el formulario ha sido enviado
    if request.method == 'POST':
        # Obtiene los datos del formulario
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        
        # Verifica si el nombre de usuario o correo electrónico ya existen en la base de datos
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso.', 'error')
        elif existing_email:
            flash('El correo electrónico ya está en uso.', 'error')
        else:
            # Crea un nuevo usuario y lo agrega a la base de datos
            new_user = User(username=username, email=email, password=password, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash('¡Registro exitoso! Por favor inicia sesión.', 'success')
            return redirect(url_for('login'))
    
    # Renderiza el formulario de registro
    return render_template('registro.html')


# Agrega una nueva ruta para el inicio de sesión de los usuarios
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Verifica si el usuario ya está autenticado, si es así, redirige a la página principal
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    # Verifica si el formulario ha sido enviado
    if request.method == 'POST':
        # Obtiene los datos del formulario
        email = request.form['email']
        password = request.form['password']
        
        # Busca al usuario por nombre de usuario o correo electrónico
        user = User.query.filter_by(email=email).first()
        if not user:
            # Si no se encuentra al usuario por nombre de usuario, intenta buscarlo por correo electrónico
            user = User.query.filter_by(email=email).first()
        
        # Verifica si se encontró al usuario y si la contraseña es correcta
        if user and user.check_password(password):
            # Si las credenciales son válidas, inicia sesión y redirige a la página principal
            session['user_id'] = user.id
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('home'))
        else:
            # Si las credenciales son incorrectas, muestra un mensaje de error
            flash('Credenciales incorrectas. Por favor, inténtalo de nuevo.', 'error')
    
    # Renderiza el formulario de inicio de sesión
    return render_template('login.html')



def comprimir_imagen(imagen):
    if imagen:
        # Abrir la imagen con Pillow
        img = Image.open(io.BytesIO(imagen))

        # Redimensionar la imagen para reducir su tamaño
        img.thumbnail((500, 500))  # Establece el tamaño máximo deseado
        
        # Guardar la imagen comprimida en un buffer de memoria
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG', quality=70)  # Calidad de compresión ajustable
        
        # Obtener los datos binarios de la imagen comprimida
        imagen_comprimida = img_buffer.getvalue()

        return imagen_comprimida
    return None



#Productos ADMIN
@app.route('/productosad')
@admin_required
def productosad():
    productos = Product.query.all()
    return render_template('productos.html', productos=productos)


#Métodos Crear Producto
@app.route('/productos', methods=['GET', 'POST'])
@admin_required
def crear_producto():
    # Verifica si el usuario está logueado y su rol es "admin"
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'admin':
            # Si el usuario es un administrador, permite el acceso al formulario de creación de producto
            if request.method == 'POST':
                # Procesa el formulario de creación de producto
                titulo = request.form['titulo']
                descripcion = request.form['descripcion']
                precio = float(request.form['precio'])
                imagen = request.files['imagen'].read()  # Lee los datos de la imagen cargada
                imagen_comprimida = comprimir_imagen(imagen)
                nuevo_producto = Product(titulo=titulo, descripcion=descripcion, precio=precio, imagen=imagen_comprimida)
                db.session.add(nuevo_producto)
                db.session.commit()
                return redirect(url_for('home'))
            return render_template('crear_producto.html')
        else:
             # Muestra un mensaje de error usando flash y redirige a la misma página
            flash('No tienes permisos para acceder a esta página.', 'error')
            return redirect(url_for('home'))
    else:
        # Si el usuario no está logueado, redirige al usuario al inicio de sesión
        return redirect(url_for('login'))
    


# Formulario para editar producto
class ProductForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    precio = FloatField('Precio', validators=[DataRequired(), NumberRange(min=0.01)])
    imagen = FileField('Imagen')

# Ruta para editar un producto
@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'admin':
            producto = Product.query.get_or_404(id)
            form = ProductForm(obj=producto)
            if request.method == 'POST':
                try:
                    form.populate_obj(producto)
                    # Verificar si se cargó una nueva imagen
                    if form.imagen.data:
                        # Leer los datos de la nueva imagen cargada
                        imagen = form.imagen.data.read()
                        # Comprimir la imagen si es necesario
                        imagen_comprimida = comprimir_imagen(imagen)
                        producto.imagen = imagen_comprimida
                    # Si no se cargó una nueva imagen, mantener la imagen existente
                    else:
                        # Recuperar la imagen existente desde la base de datos
                        imagen_existente = producto.imagen
                        # Comprimir la imagen existente
                        imagen_comprimida = comprimir_imagen(imagen_existente)
                        producto.imagen = imagen_comprimida
                    db.session.commit()
                    flash('Producto actualizado correctamente.', 'success')
                    return redirect(url_for('home'))
                except Exception as e:
                    flash('Error al actualizar el producto: {}'.format(str(e)), 'error')
            # Modificar el formulario para cargar la imagen existente
            form.imagen.data = producto.imagen
            return render_template('editar_producto.html', form=form)
        else:
            flash('No tienes permisos para acceder a esta página.', 'error')
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


# Ruta para Eliminar Producto
@app.route('/eliminar_producto/<int:producto_id>', methods=['POST'])
@admin_required
def eliminar_producto(producto_id):
    # Verifica si el usuario está logueado y su rol es "admin"
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'admin':
            # Busca el producto por su ID
            producto = Product.query.get(producto_id)
            if producto:
                # Elimina el producto de la base de datos
                db.session.delete(producto)
                db.session.commit()
                flash('Producto eliminado exitosamente.', 'success')
            else:
                flash('No se encontró el producto a eliminar.', 'error')
        else:
            # Si el usuario no es un administrador, muestra un mensaje de error
            flash('No tienes permisos para eliminar productos.', 'error')
    else:
        # Si el usuario no está logueado, redirige al usuario al inicio de sesión
        flash('Debes iniciar sesión para eliminar productos.', 'error')
    
    # Redirige al usuario a la página principal de productos después de eliminar
    return redirect(url_for('home'))

# Ruta para buscar un producto
@app.route('/buscar')
def buscar_producto():
    # Obtener el término de búsqueda de la query string
    termino_busqueda = request.args.get('q').lower()

    # Buscar productos que coincidan con el término de búsqueda
    productos = Product.query.filter(func.lower(Product.titulo).like(f"%{termino_busqueda}%")).all()

    # Convertir las imágenes de los productos a base64
    for producto in productos:
        producto.imagen = convertir_imagen_base64(producto.imagen)

    # Verificar si no se encontraron resultados
    if not productos:
        flash(f"No se encontraron resultados para '{termino_busqueda}'.", 'warning')
        return redirect(url_for('home'))

    # Renderizar el template con los productos encontrados
    return render_template('resultados_busqueda.html', productos=productos, termino_busqueda=termino_busqueda)


    

@app.route('/logout')
def logout():
    # Elimina el ID de usuario de la sesión, si está presente
    session.pop('user_id', None)
    # Redirige al usuario al inicio de sesión (o a cualquier otra página que desees)
    return redirect(url_for('home'))


def convertir_imagen_base64(imagen_binaria):
    if imagen_binaria:
        # Convierte los datos binarios de la imagen a una cadena base64
        imagen_base64 = base64.b64encode(imagen_binaria).decode('utf-8')
        return imagen_base64
    return None



#RUN APLICATION
if __name__ == "__main__":
    app.run(debug=True)