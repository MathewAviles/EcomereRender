#IMPORTS
from flask import Flask,render_template,request,redirect,url_for,session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required

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
    #app.config['SECRET_KEY'] = 'clave_secreta'  # Clave secreta para la sesión
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


#Ruta principal Registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Obtén los datos del formulario
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Validación de campos (puedes agregar más validaciones según tus necesidades)
        if not username or not email or not password:
            return 'Por favor, completa todos los campos.', 400
        
        # Verifica si el usuario ya existe en la base de datos
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return 'El usuario ya existe. Por favor, elige otro correo electrónico.', 400
        
        # Hash de la contraseña antes de almacenarla en la base de datos
        hashed_password = generate_password_hash(password)
        
        # Crea un nuevo usuario
        new_user = User(username=username, email=email, password=hashed_password)
        # Guarda el nuevo usuario en la base de datos
        db.session.add(new_user)
        db.session.commit()
        
        # Redirecciona a alguna página después de registrar exitosamente
        return redirect(url_for('registro_exitoso'))
    
    # Si el método es GET, simplemente renderiza la plantilla de registro
    return render_template('registro.html')


#Ruta principal Login
# Método para iniciar sesión (login)
# Método para iniciar sesión (login)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtén los datos del formulario
        email = request.form['email']
        password = request.form['password']
        
        # Busca el usuario en la base de datos por su correo electrónico
        user = User.query.filter_by(email=email).first()
        
        # Verifica si se encontró el usuario y la contraseña es correcta
        if user and user.check_password(password):
            # Almacena el ID de usuario en la sesión
            session['user_id'] = user.id
            print("Inicio de sesión exitoso. Usuario:", user.username)

            # Redirecciona a alguna página después de iniciar sesión exitosamente
            return redirect(url_for('home'))
    
        
        # Si las credenciales son incorrectas, muestra un mensaje de error
        return 'Credenciales incorrectas. Por favor, inténtalo de nuevo.', 401
    
    # Si el método es GET, simplemente renderiza la plantilla de inicio de sesión
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