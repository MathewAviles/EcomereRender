#IMPORTS
from flask import Flask,render_template,request,redirect,url_for,session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

#DB INIT
db = SQLAlchemy()

#DB TABLES
#Table Producto
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)

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
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ecomerce_cgb2_user:9oba2RXPeY23ahKktYqC1iSDpmUsaTP6@dpg-co9itjdjm4es73b03700-a.oregon-postgres.render.com/ecomerce_cgb2'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.secret_key = 'tu_clave_secreta'  # Clave secreta para las sesiones


    db.init_app(app)

    with app.app_context():
        db.create_all()
        print("Conexión a la base de datos establecida correctamente.")
    return app
app=create_app()



#ROUTES
#Ruta principal home
@app.route('/')
def home():
    productos = Product.query.all()
    return render_template('home.html', productos=productos)

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



#Métodos Crear Producto
@app.route('/productos', methods=['GET', 'POST'])
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
                nuevo_producto = Product(titulo=titulo, descripcion=descripcion, precio=precio)
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
    

@app.route('/logout')
def logout():
    # Elimina el ID de usuario de la sesión, si está presente
    session.pop('user_id', None)
    # Redirige al usuario al inicio de sesión (o a cualquier otra página que desees)
    return redirect(url_for('home'))

#RUN APLICATION
if __name__ == "__main__":
    app.run(debug=True)