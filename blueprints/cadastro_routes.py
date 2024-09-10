from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from config import mysql

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

        return redirect(url_for('login.login'))
