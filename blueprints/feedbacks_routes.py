from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from config import mysql
from datetime import datetime

feedback_blueprint = Blueprint('feedback', __name__)

@feedback_blueprint.route('/feedbacks', methods=['GET', 'POST'])
def feedbacks():
    if request.method == 'POST':
        usuario_id = session.get('usuario_id')  # Certifique-se de que o usuário está logado
        mensagem = request.form.get('mensagem')

        if usuario_id and mensagem:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO FEEDBACKS (usuario_id, mensagem) VALUES (%s, %s)", (usuario_id, mensagem))
            mysql.connection.commit()
            cur.close()
            flash("Feedback enviado com sucesso!")
            return redirect(url_for('feedback.feedbacks'))
        else:
            flash("É necessário estar logado e preencher a mensagem do feedback.")


    # Listar feedbacks
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT U.NOME, F.mensagem, F.data_envio FROM FEEDBACKS F JOIN USUARIOS U ON F.usuario_id = U.ID ORDER BY F.data_envio DESC")
    feedbacks_raw = cursor.fetchall()
    cursor.close()

    feedbacks = []
    for row in feedbacks_raw:
        feedbacks.append({
         'NOME': row[0], 
         'mensagem': row[1], 
         'data_envio': datetime.strptime(str(row[2]), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
        })

    return render_template('feedback.html', feedbacks=feedbacks)
