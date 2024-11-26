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
    
    telefone_formatado = f"({str(usuario[2])[:2]}) {str(usuario[2])[2:7]}-{str(usuario[2])[7:11]}" if usuario[2] else None

    usuario_data = {
        'nome': usuario[0],
        'email': usuario[1],
        'telefone': telefone_formatado,
        'sexo': usuario[3], 
        'data_nasc': usuario[4].strftime("%d/%m/%Y") if usuario[4] else None,
        'curso_cargo': usuario[5],
        'turno': usuario[6]
    }

    return render_template('profile.html', usuario=usuario_data)

@cadastro_blueprint.route('/editar_dados', methods=['GET', 'POST'])
def editar_dados():
    
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT nome, email, telefone, sexo, data_nasc, curso_cargo, turno
        FROM USUARIOS WHERE id = %s
    """, (usuario_id,))
    usuario = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        sexo = request.form['sexo']
        data_nasc = request.form['data_nasc']
        curso_cargo = request.form['curso_cargo']
        turno = request.form['turno']

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE USUARIOS
            SET nome = %s, email = %s, telefone = %s, sexo = %s, data_nasc = %s, curso_cargo = %s, turno = %s
            WHERE id = %s
        """, (nome, email, telefone, sexo, data_nasc, curso_cargo, turno, usuario_id))
        mysql.connection.commit()
        cur.close()
        
        flash('Dados atualizados com sucesso!', 'success')
        return redirect(url_for('cadastro.minha_conta'))  

    return render_template('editar_conta.html', usuario=usuario)

@cadastro_blueprint.route('/contato', methods=['GET', 'POST'])
def enviar_mensagem():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        mensagem = request.form.get('mensagem')
        
        if not (nome and email and mensagem):
            flash('Por favor, preencha todos os campos.', 'danger')
            return render_template('contato.html')

    try:
        cur = mysql.connection.cursor()
        query = "INSERT INTO MSG_CONTATO (nome, email, mensagem) VALUES (%s, %s, %s)"
        valores = (nome, email, mensagem)
        cur.execute(query, valores)
        mysql.connection.commit()
        cur.close()

        flash('Mensagem enviada com sucesso!', 'success')
        return redirect(url_for('cadastro.enviar_mensagem'))
        
    except Exception as e:
            flash('')
            return render_template('contato.html')


@cadastro_blueprint.route('/exibir_mensagens', methods=['GET'])
def exibir_mensagens():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nome, email, mensagem, data_envio FROM MSG_CONTATO ORDER BY data_envio DESC")
    mensagens = cur.fetchall()
    cur.close()
    
    return mensagens
