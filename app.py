#IMPORTS
from flask import Flask,render_template,request,redirect,url_for

#APP INIT
app= Flask(__name__)



#ROUTES
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def inicio():
    return render_template('login.html')


#RUN APLICATION
if __name__ == "__main__":
    app.run(debug=True)