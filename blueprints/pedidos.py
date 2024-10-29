from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from config import mysql
from datetime import datetime


pedidos_blueprint = Blueprint('pedidos', __name__)

def usuario_logado():
    usuario_id = session.get('usuario_id')  # Exemplo de como pegar o ID do usuário logado
    
    if not usuario_id:
        flash('Você precisa estar logado para adicionar ao carrinho.')
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

    forma_pagamento = request.form.get('pagamento')
    
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

    # 3. Inserir o pedido na tabela 'PEDIDOS'
    cur.execute("""
        INSERT INTO PEDIDOS (usuario_id, order_date, total, forma_pagamento)
        VALUES (%s, NOW(), %s, %s)
    """, (usuario_id, total_pedido, forma_pagamento))
    pedido_id = cur.lastrowid # Pega o ID do pedido recém-criado

    # 4. Transferir os itens do carrinho para a tabela 'PEDIDOS_ITEMS'
    for item in itens_carrinho:
        cur.execute("""
            INSERT INTO PEDIDOS_ITEMS (pedido_id, produto_id, quantidade, preco)
            VALUES (%s, %s, %s, %s)
        """, (pedido_id, item[0], item[1], item[2]))
    
    cur.execute("DELETE FROM CARRINHO WHERE usuario_id = %s", (usuario_id,))

    mysql.connection.commit()
    cur.close()

    flash('Compra finalizada com sucesso!')
    return redirect(url_for('cadastroProduto.listar_produto'))



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


