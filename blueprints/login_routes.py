from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
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
      if usuario.get('TIPO') == 0:  # Supondo que admin é um campo booleano/int na tabela
            return redirect(url_for('login.admin_cad'))  # Redireciona para página de admin
      else:
            #flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('cadastroProduto.listar_produto'))
    else:
        return redirect(url_for('login.home'))  # Credenciais inválidas

    return render_template("login.html")

@login_blueprint.route('/admin_cad', methods=['GET'])
def admin_cad():
    return render_template('cadastroProduto.html')  # Página para cadastro de produtos
