from decouple import config
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect, CSRF
from flask_login import login_required


import string
import random
import mysql.connector


app = Flask(__name__)
app.secret_key = config("CLAVE")

csrf = CSRFProtect()

# Configurar la conexión a la base de datos
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="acortador",
)


def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = "".join(random.choice(characters) for _ in range(6))
    return short_url


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Obtener la información del usuario desde la base de datos
        cursor = db.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            # Verificar la contraseña encriptada
            if check_password_hash(user[2], password):
                return redirect(url_for("home"))
        else:
            flash("Usuario o contraseña incorrecta")
            return render_template("auth/login.html")
    else:
        return render_template("auth/login.html")


@app.route("/home")
def home():
    return render_template("shorten.html")


@app.route("/registrar")
def registrar():
    return render_template("registrar.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    # Encriptar la contraseña
    hashed_password = generate_password_hash(password)

    # Insertar el usuario en la base de datos
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO usuarios (username, password) VALUES (%s, %s)",
        (username, hashed_password),
    )
    db.commit()
    cursor.close()

    return jsonify({"message": "Registro exitoso"})


@app.route("/shorten", methods=["POST"])
def shorten():
    original_url = request.form["original_url"]

    # Generar una URL corta
    short_url = generate_short_url()

    # Insertar la URL en la base de datos
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO urls (original_url, short_url) VALUES (%s, %s)",
        (original_url, short_url),
    )
    db.commit()
    cursor.close()

    return jsonify({"short_url": short_url})


@app.route("/<short_url>")
def redirect_to_original_url(short_url):
    # Obtener la URL original desde la base de datos
    cursor = db.cursor()
    cursor.execute("SELECT original_url FROM urls WHERE short_url = %s", (short_url,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        original_url = result[0]
        return redirect(original_url)

    return jsonify({"error": "URL no encontrada"})


def status_401(error):
    return redirect(url_for("login"))


def status_404(error):
    return "<h1>Página no encontrada</h1>", 404


if __name__ == "__main__":
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug=True, port=5000)
