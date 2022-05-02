from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random 
import string
import os

app = Flask(__name__)
#Defino la configuración de BD
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Instanciamos el objeto de BD
db = SQLAlchemy(app)

#Si no existe la BD, se crea
@app.before_first_request
def create_tables():
    db.create_all()

#Definición de la clase para el modelo de la BD
class Urls(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long_url = db.Column("long_url", db.String())
    short_url = db.Column("short_url", db.String(15))
    cant_usos = db.Column("cant_usos", db.Integer, default = 1)
    fecha_creacion = db.Column("fecha_creacion", db.Date, default = datetime.now)

    def __init__(self, long_url, short_url):
        self.long_url = long_url
        self.short_url = short_url

#Fn de Creación de la URL corta
def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase
    while True:
        rand_letters = random.choices(letters, k=3)
        rand_letters = "".join(rand_letters)
        short_url = Urls.query.filter_by(short_url=rand_letters).first()
        if not short_url:
            return rand_letters

#Fn Principal, recibe la URL Larga y devuelve la URL corta
#Si ingresamos la URL corta y existe en la BD, devuelve la URL original
@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        url_received = request.form["nm"]
        found_url = Urls.query.filter_by(long_url=url_received).first()

        if found_url:
            cantidad = found_url.cant_usos + 1
            found_url.cant_usos = cantidad
            db.session.commit()
            return redirect(url_for("display_short_url", url=found_url.short_url))
        else:
            found_url_long = Urls.query.filter_by(short_url=url_received.rsplit('/', 1)[-1]).first()
            if found_url_long:
                return redirect(url_for("display_long_url", url=url_received.rsplit('/', 1)[-1]))
            else:
                short_url = shorten_url()
                print(short_url)
                new_url = Urls(url_received, short_url)
                db.session.add(new_url)
                db.session.commit()
                return redirect(url_for("display_short_url", url=short_url))
    else:
        return render_template('url_page.html')

#Fn redirecciona a la URL original, a partir de la URL Corta
@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short_url=short_url).first()
    if long_url:
        return redirect(long_url.long_url)
    else:
        return f'<h1>El sitio Ingresado no Existe</h1>'

#Fn muestra la URL corta generada o encontrada en la BD
@app.route('/display/<url>')
def display_short_url(url):
    return render_template('url_corta.html', short_url_display=url)

#Fn muestra la URL original encontrada en la BD
@app.route('/display_orig/<url>')
def display_long_url(url):
    found_url_long = Urls.query.filter_by(short_url=url).first()
    if found_url_long:    
        return render_template('url_orig.html', long_url_display=found_url_long.long_url)

#Fn muestra los registros de la BD y permite el borrado de registros
@app.route('/all_urls', methods=['POST', 'GET'])
def display_all():

    if request.method == "GET":
        return render_template('all_urls.html', vals=Urls.query.all())
    else:        
        lista = (request.form.getlist('check'))
        print(lista)
        #return "done"
        for url_corta in lista:
            found_url = Urls.query.filter_by(short_url=url_corta).first()            
            if found_url:
                db.session.delete(found_url)
                db.session.commit()
        
        return render_template('all_urls.html', vals=Urls.query.all())


if __name__ == '__main__':
    app.run(port=5000, debug=True)