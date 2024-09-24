from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from config import mysql
import base64

cadastroProduto_blueprint = Blueprint('cadastroProduto', __name__)

@cadastroProduto_blueprint.route('/adicionar_prod', methods=['POST'])
def adicionar_prod():
    if request.method == 'POST':
        produtos = request.form

       # print(request.files)  # Verifique se a chave 'imagem' está presente

        imagem = request.files.get('imagem')
        
        imagem_data = imagem.read()

        query = """
            INSERT INTO CAD_PRODUTO(
                PRODUTO,
                PRECO,
                DESCRICAO,
                CATEGORIA,
                IMAGEM 
            )
            VALUES(
                %s,
                %s,
                %s,
                %s,
                %s
            );
        """

        cur = mysql.connection.cursor()
        # Execute com os parâmetros corretos
        cur.execute(query, (
            produtos['produto'],
            produtos['preco'],
            produtos['descricao'],
            produtos['categoria'],
            imagem_data
        ))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('cadastroProduto.listar_produto'))
    
@cadastroProduto_blueprint.route('/produto', methods=['GET'])
def listar_produto():
      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM CAD_PRODUTO")
      produto = cur.fetchall()
      cur.close()

      print(produto)

        # Codificar a imagem em base64
      produtos_com_imagem = []
      for prod in produto:
        imagem_b64 = base64.b64encode(prod[5]).decode('utf-8')  # Supondo que a imagem está no índice 5
        produtos_com_imagem.append((*prod[:5], imagem_b64))  # Adiciona a imagem codificada à tupla

      return render_template('index.html', produtos=produtos_com_imagem)
      
