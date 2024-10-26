from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from config import mysql
import base64
from datetime import datetime

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
                QUANTIDADE,
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

      return render_template('produto.html', produtos=produtos_com_imagem)

def usuario_logado():
    usuario_id = session.get('usuario_id')  # Exemplo de como pegar o ID do usuário logado
    
    if not usuario_id:
        flash('Você precisa estar logado para adicionar ao carrinho.')
        return None
    return usuario_id


# Adicionar item ao carrinho
@cadastroProduto_blueprint.route('/add_to_cart/<int:produto_id>', methods=['POST'])
def add_to_cart(produto_id):
    
    usuario_id = usuario_logado()
    if not usuario_id:
        return redirect(url_for('login.login'))
    
    # Verifica se o produto já está no carrinho do usuário
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * FROM CARRINHO WHERE usuario_id = %s AND produto_id = %s
    """, (usuario_id, produto_id))
    item = cur.fetchone()

    if item:
        # Se o item já está no carrinho, incrementa a quantidade
        cur.execute("""
            UPDATE CARRINHO SET quantidade = quantidade + 1 WHERE usuario_id = %s AND produto_id = %s
        """, (usuario_id, produto_id))
    else:
        # Se o item não está no carrinho, insere um novo registro
        cur.execute("""
            INSERT INTO CARRINHO (usuario_id, produto_id, quantidade) VALUES (%s, %s, %s)
        """, (usuario_id, produto_id, 1))

    mysql.connection.commit()
    cur.close()

    flash(f'Produto foi adicionado ao carrinho com sucesso!')
    return redirect(url_for('cadastroProduto.listar_produto'))

@cadastroProduto_blueprint.route('/ver_carrinho', methods=['GET'])
def ver_carrinho():
    usuario_id = usuario_logado()
    if not usuario_id:
        return redirect(url_for('login.login'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT CARRINHO.produto_id, CAD_PRODUTO.PRODUTO, CAD_PRODUTO.PRECO, CARRINHO.quantidade, CAD_PRODUTO.IMAGEM 
        FROM CARRINHO 
        JOIN CAD_PRODUTO ON CARRINHO.produto_id = CAD_PRODUTO.id 
        WHERE CARRINHO.usuario_id = %s
    """, (usuario_id,))
    
    itens_carrinho = cur.fetchall()
    cur.close()

    # Calcular o total
    total = sum(float(item[2]) * int(item[3]) for item in itens_carrinho)
    
    # Preparar os produtos para renderizar no template
    produtos = []
    for item in itens_carrinho:
        imagem_b64 = base64.b64encode(item[4]).decode('utf-8')
        produtos.append({
            'id': item[0],
            'nome': item[1],
            'preco': item[2],
            'quantidade': item[3],
            'imagem': imagem_b64
        })

    return render_template('carrinho.html', carrinho=produtos, total=total)

@cadastroProduto_blueprint.route('/limpar_carrinho', methods=['POST'])
def limpar_carrinho():
    usuario_id = usuario_logado()
    if not usuario_id:
        return redirect(url_for('login.login'))
    
    cur = mysql.connection.cursor()
    cur.execute("""
            DELETE FROM CARRINHO WHERE usuario_id= %s
        """, (usuario_id,))
    mysql.connection.commit ()

    flash('Carrinho limpo com sucesso!')  # Mensagem de sucesso
    return redirect(url_for('cadastroProduto.ver_carrinho'))  # Redireciona para a página do carrinho

@cadastroProduto_blueprint.route('/resumo_pedido', methods=['GET'])
def resumo_pedido():
    usuario_id = usuario_logado()
    if not usuario_id:
        return redirect(url_for('login.login'))
    
    cur = mysql.connection.cursor()

    # 1. Buscar itens do carrinho
    cur.execute("""
        SELECT CARRINHO.produto_id, CARRINHO.quantidade, CAD_PRODUTO.PRECO
        FROM CARRINHO 
        JOIN CAD_PRODUTO ON CARRINHO.produto_id = CAD_PRODUTO.id 
        WHERE CARRINHO.usuario_id = %s
    """, (usuario_id,))
    itens_carrinho = cur.fetchall()
    cur.close()

    if not itens_carrinho:
        flash('Seu carrinho está vazio.')
        return redirect(url_for('cadastroProduto.listar_produto'))

    
    return render_template('resumo_pedido.html')


# Função para registrar pedido
@cadastroProduto_blueprint.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    usuario_id = usuario_logado()
    if not usuario_id:
        return redirect(url_for('login.login'))

    cur = mysql.connection.cursor()

    # 1. Buscar itens do carrinho
    cur.execute("""
        SELECT CARRINHO.produto_id, CARRINHO.quantidade, CAD_PRODUTO.PRECO
        FROM CARRINHO 
        JOIN CAD_PRODUTO ON CARRINHO.produto_id = CAD_PRODUTO.id 
        WHERE CARRINHO.usuario_id = %s
    """, (usuario_id,))
    itens_carrinho = cur.fetchall()

    if not itens_carrinho:
        flash('Seu carrinho está vazio.')
        return redirect(url_for('cadastroProduto.listar_produto'))

    # 2. Calcular o total do pedido
    total_pedido = sum(float(item[2]) * int(item[1]) for item in itens_carrinho)

    # 3. Inserir o pedido na tabela 'ORDERS'
    cur.execute("""
        INSERT INTO PEDIDOS (usuario_id, order_date, total)
        VALUES (%s, NOW(), %s)
    """, (usuario_id, total_pedido))
    pedido_id = cur.lastrowid  # Pega o ID do pedido recém-criado

    # 4. Transferir os itens do carrinho para a tabela 'ORDER_ITEMS'
    for item in itens_carrinho:
        cur.execute("""
            INSERT INTO PEDIDOS_ITEMS (pedido_id, produto_id, quantidade, preco)
            VALUES (%s, %s, %s, %s)
        """, (pedido_id, item[0], item[1], item[2]))


    flash('Compra finalizada com sucesso!')
    return redirect(url_for('cadastroProduto.listar_produto'))


