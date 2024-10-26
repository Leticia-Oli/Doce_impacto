from flask import Blueprint, flash, request, jsonify, render_template, redirect, url_for, session
from config import db

login_blueprint = Blueprint('login', __name__)


@login_blueprint.route('/', methods=['GET'])
def home():
    return redirect(url_for('login.login_page'))

@login_blueprint.route('/login', methods=['GET'])
def login_page():
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

@login_blueprint.route('/login', methods=['POST'])
def login1():
    
      email = request.form['email']
      senha = request.form['senha']

    # Consultando o banco de dados   
      cursor = db.cursor(dictionary=True)
      cursor.execute('select * from USUARIOS WHERE email = %s AND senha = %s', (email, senha))
      usuario = cursor.fetchone()

     # Verificando se o usuário existe
      if usuario:
        session['usuario_id'] = usuario ['ID']
        if usuario['TIPO'] == 0:  # Supondo que admin é um campo booleano/int na tabela
                return redirect(url_for('login.admin_cad'))  # Redireciona para página de admin
        else:
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('cadastroProduto.listar_produto'))
      else:
        flash('Credenciais inválidas. Tente novamente.', 'danger')
        return redirect(url_for('login.home'))  # Credenciais inválidas

        return redirect(url_for('login.login_page'))

@login_blueprint.route('/admin_cad', methods=['GET'])
def admin_cad():
    return render_template('cadastroProduto.html')  # Página para cadastro de produtos


