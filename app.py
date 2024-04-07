#IMPORTS
from flask import Flask,render_template,request,redirect,url_for

#APP INIT
app= Flask(__name__)



#ROUTES
@app.route('/')
def inicio():
    return render_template('base.html')


#RUN APLICATION
if __name__ == "__main__":
    app.run(debug=True)