from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from config import mysql
from datetime import datetime


pedidos_blueprint = Blueprint('pedidos', __name__)

def usuario_logado():
    usuario_id = session.get('usuario_id')  # Exemplo de como pegar o ID do usuário logado
    
    if not usuario_id:
        flash('Você precisa estar logado!')
        return None
    return usuario_id

#Parte do Cliente
@pedidos_blueprint.route('/resumo_pedido', methods=['GET'])
def resumo_pedido():
    usuario_id = usuario_logado()
    if not usuario_id:
        return redirect(url_for('login.login'))
    
    cur = mysql.connection.cursor()

    # 1. Buscar itens do carrinho
    cur.execute("""
        SELECT CARRINHO.produto_id, CARRINHO.quantidade, CAD_PRODUTO.PRECO, CAD_PRODUTO.PRODUTO
        FROM CARRINHO 
        JOIN CAD_PRODUTO ON CARRINHO.produto_id = CAD_PRODUTO.id 
        WHERE CARRINHO.usuario_id = %s
    """, (usuario_id,))
    itens_carrinho = cur.fetchall()
    cur.close()

    if not itens_carrinho:
        flash('Seu carrinho está vazio.')
        return redirect(url_for('cadastroProduto.listar_produto'))

 # 2. Calcular o total do pedido
    total_pedido = sum(float(item[2]) * int(item[1]) for item in itens_carrinho)

    # 3. Preparar a lista de itens para o template
    carrinho = []
    for item in itens_carrinho:
        # Adicione uma verificação para garantir que todos os índices existem
        #if len(item) >= 4:
            carrinho.append({
                'produto_id': item[0],
                'quantidade': item[1],
                'preco': item[2],
                'nome': item[3]
    } )

    
    return render_template('resumo_pedido.html', carrinho=carrinho, total=total_pedido)


# Função para registrar pedido
@pedidos_blueprint.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    usuario_id = usuario_logado()
    if not usuario_id:
        return redirect(url_for('login.login'))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT CARRINHO.produto_id, CAD_PRODUTO.PRECO, CARRINHO.quantidade
        FROM CARRINHO
        JOIN CAD_PRODUTO ON CARRINHO.produto_id = CAD_PRODUTO.id
        WHERE CARRINHO.usuario_id = %s
    """, (usuario_id,))
    itens_carrinho = cur.fetchall()

    if not itens_carrinho:
        flash("Seu carrinho está vazio!")
        return redirect(url_for('cadastroProduto.ver_carrinho'))

    # Calcular o total do pedido
    total = sum(float(item[1]) * int(item[2]) for item in itens_carrinho)

    # Inserir um novo pedido na tabela PEDIDOS
    cur.execute("""
        INSERT INTO PEDIDOS (usuario_id, order_date, total)
        VALUES (%s, NOW(), %s)
    """, (usuario_id, total))
    pedido_id = cur.lastrowid  # Obter o ID do pedido recém-criado

    # Inserir itens do pedido na tabela PEDIDOS_ITEMS
    for item in itens_carrinho:
        produto_id = item[0]
        preco = float(item[1])
        quantidade = int(item[2])
        cur.execute("""
            INSERT INTO PEDIDOS_ITEMS (pedido_id, produto_id, quantidade, preco)
            VALUES (%s, %s, %s, %s)
        """, (pedido_id, produto_id, quantidade, preco))

    # Limpar o carrinho do usuário
    cur.execute("DELETE FROM CARRINHO WHERE usuario_id = %s", (usuario_id,))
    mysql.connection.commit()
    cur.close()

    flash("Compra finalizada com sucesso!")
    return redirect(url_for('pedidos.ver_pedido', pedido_id=pedido_id))

@pedidos_blueprint.route('/ver_pedido/<int:pedido_id>', methods=['GET'])
def ver_pedido(pedido_id):
    usuario_id = usuario_logado()
    if not usuario_id:
        return redirect(url_for('login.login'))

    # Recuperar informações do pedido
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT PEDIDOS.id, PEDIDOS.order_date, PEDIDOS.total
        FROM PEDIDOS
        WHERE PEDIDOS.id = %s AND PEDIDOS.usuario_id = %s
    """, (pedido_id, usuario_id))
    pedido = cur.fetchone()

    if not pedido:
        flash("Pedido não encontrado!")
        return redirect(url_for('cadastroProduto.ver_carrinho'))

    # Recuperar itens do pedido
    cur.execute("""
        SELECT PEDIDOS_ITEMS.produto_id, CAD_PRODUTO.PRODUTO, PEDIDOS_ITEMS.quantidade, PEDIDOS_ITEMS.preco
        FROM PEDIDOS_ITEMS
        JOIN CAD_PRODUTO ON PEDIDOS_ITEMS.produto_id = CAD_PRODUTO.id
        WHERE PEDIDOS_ITEMS.pedido_id = %s
    """, (pedido_id,))
    itens_pedido = cur.fetchall()
    cur.close()

    return render_template('pedidos.html', pedido=pedido, itens=itens_pedido)


# Parte Administrativa
@pedidos_blueprint.route('/listar_pedidos')
def listar_pedidos():
    cur = mysql.connection.cursor()
        
    cur.execute("SELECT id, usuario_id, order_date, total, forma_pagamento FROM PEDIDOS")
    pedidos = cur.fetchall()

    # Consultar os itens de cada pedido
    lista_pedidos = []
    for pedido in pedidos:
        pedido_id = pedido[0]
        
        # Buscar itens do pedido
        cur.execute("SELECT produto_id, quantidade, preco FROM PEDIDOS_ITEMS WHERE pedido_id = %s", (pedido_id,))
        itens = cur.fetchall()

        lista_pedidos.append({
            'id': pedido[0],
            'usuario_id': pedido[1],
            'order_date': pedido[2],
            'total': pedido[3],
            'forma_pagamento': pedido[4],
            'itens': [{'produto_id': item[0], 'quantidade': item[1], 'preco': item[2]} for item in itens]
        })

    # Fechar cursor
    cur.close()

    # Renderizar template com os dados de pedidos
    return render_template('Pedidos_admin.html', pedidos=lista_pedidos)

