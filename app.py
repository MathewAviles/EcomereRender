#IMPORTS
from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy

#DB INIT
db = SQLAlchemy()

#DB TABLES
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.titulo}>'



#APP INIT
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ecomerce_cgb2_user:9oba2RXPeY23ahKktYqC1iSDpmUsaTP6@dpg-co9itjdjm4es73b03700-a.oregon-postgres.render.com/ecomerce_cgb2'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    db.init_app(app)

    with app.app_context():
        db.create_all()
        print("Conexión a la base de datos establecida correctamente.")
    return app
app=create_app()


#ROUTES
@app.route('/')
def home():
    productos = Product.query.all()
    return render_template('home.html', productos=productos)

@app.route('/login')
def inicio():
    return render_template('login.html')

#Métodos
@app.route('/productos', methods=['GET', 'POST'])
def crear_producto():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        nuevo_producto = Product(titulo=titulo, descripcion=descripcion, precio=precio)
        db.session.add(nuevo_producto)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('crear_producto.html')


#RUN APLICATION
if __name__ == "__main__":
    app.run(debug=True)