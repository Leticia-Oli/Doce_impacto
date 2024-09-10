from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from config import db

login_blueprint = Blueprint('login', __name__)


@login_blueprint.route('/', methods=['GET'])
def login():
    return render_template('login.html')

@login_blueprint.route('/read_login_form', methods=['GET', 'POST'])
def read_login_form():
    if request.method == 'POST':
        return redirect(url_for('login.index'))
    
    return render_template('index.html')

@login_blueprint.route('/index', methods=['GET'])
def index():
    return render_template('index.html')

@login_blueprint.route('/cadastro', methods=['GET'])
def cadastro():
    return render_template('cadastro.html')

@login_blueprint.route('/login', methods=['GET','POST'])
def login1():
    if request.method == 'POST':
      email = request.form['email']
      senha = request.form['senha']

    # Consultando o banco de dados   
      cursor = db.cursor(dictionary=True)
      cursor.execute('select * from USUARIOS WHERE email = %s AND senha = %s', (email, senha))
      usuario = cursor.fetchone()

     # Verificando se o usuário existe
      if usuario:
            #flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('login.dashboard'))
      else:
            #flash('Credenciais inválidas. Tente novamente.', 'danger')
            return redirect(url_for('home')) 

    return render_template("login.html")

@login_blueprint.route('/dashboard')
def dashboard():
    return "Bem-vindo ao Dashboard!"
