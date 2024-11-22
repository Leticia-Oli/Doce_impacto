from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from config import mysql
from datetime import datetime

cadastro_blueprint = Blueprint('cadastro', __name__)

@cadastro_blueprint.route('/criar-usuario', methods=['POST'])
def criar_usuario():
    if request.method == 'POST':
        usuario = request.form

        query = f"""
            INSERT INTO USUARIOS(
                NOME,
                EMAIL,
                SENHA,
                TELEFONE,
                SEXO,
                DATA_NASC,
                CURSO_CARGO,
                TURNO,
                TIPO
            )
            VALUES(
                '{usuario['nome']}',
                '{usuario['email']}',
                '{usuario['senha']}',
                 {usuario['telefone']},
                '{usuario['genero']}',
                '{usuario['data_nasc']}',
                '{usuario['curso_cargo']}',
                '{usuario['turno']}',
                1
            );
        """

        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()

        return redirect(url_for('login.login_page'))

@cadastro_blueprint.route('/minha_conta')
def minha_conta():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('login.login')) 

 
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT nome, email, telefone, sexo, data_nasc, curso_cargo, turno 
        FROM USUARIOS WHERE id = %s
    """, (usuario_id,))
    usuario = cur.fetchone()
    cur.close()

    if not usuario:
        flash("Usuário não encontrado.")
        return redirect(url_for('login.login'))
    
    usuario_data = {
        'nome': usuario[0],
        'email': usuario[1],
        'telefone': usuario[2],
        'sexo': usuario[3], 
        'data_nasc': usuario[4].strftime("%d/%m/%Y") if usuario[4] else None,
        'curso_cargo': usuario[5],
        'turno': usuario[6]
    }

    return render_template('profile.html', usuario=usuario_data)