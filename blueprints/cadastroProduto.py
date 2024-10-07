from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
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

# Adicionar item ao carrinho
@cadastroProduto_blueprint.route('/add_to_cart/<int:produto_id>', methods=['POST'])
def add_to_cart(produto_id):
    print(f"Tentativa de adicionar o produto com ID: {produto_id}")
    # Pegar o produto do banco de dados
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM CAD_PRODUTO WHERE id = %s", (produto_id,))
    produto = cur.fetchone()
    cur.close()

    print(f"Produto buscado: {produto}")

    if produto:
        item = {
            'id': produto[0],
            'nome': produto[1],
            'preco': produto[2],
            'descricao': produto[3],
            'categoria': produto[4],
            'imagem': base64.b64encode(produto[5]).decode('utf-8')  # Codifica a imagem
        }

        # Adicionar o produto ao carrinho na sessão
        if 'carrinho' not in session:
            session['carrinho'] = []

        session['carrinho'].append(item)
        session.modified = True  # Atualiza a sessão

        print(f"Carrinho após adição: {session['carrinho']}")

        flash(f'Produto "{produto[1]}" foi adicionado ao carrinho com sucesso!')
        return redirect(url_for('cadastroProduto.listar_produto'))
    
    flash('Produto não encontrado.')
    return redirect(url_for('cadastroProduto.listar_produto'))

@cadastroProduto_blueprint.route('/ver_carrinho', methods=['GET'])
def ver_carrinho():
    carrinho = session.get('carrinho', [])
    print(f"Carrinho ao visualizar: {carrinho}")

    if not carrinho:
        flash("Carrinho vazio!")
    total = sum([item['preco'] for item in carrinho])
    return render_template('carrinho.html', carrinho=carrinho, total=total)

      

