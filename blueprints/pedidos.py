from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash, request
from config import mysql
from datetime import datetime


pedidos_blueprint = Blueprint('pedidos', __name__)

def usuario_logado():
    usuario_id = session.get('usuario_id')  
    
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

    pagamento = request.form.get('pagamento')
    if not pagamento:
        flash("Forma de pagamento não informada!")
        return redirect(url_for('pedidos.resumo_pedido'))

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

 
    total = sum(float(item[1]) * int(item[2]) for item in itens_carrinho)

    
    cur.execute("""
        INSERT INTO PEDIDOS (usuario_id, order_date, total, forma_pagamento)
        VALUES (%s, NOW(), %s, %s)
    """, (usuario_id, total, pagamento))
    pedido_id = cur.lastrowid

    for item in itens_carrinho:
        produto_id = item[0]
        preco = float(item[1])
        quantidade = int(item[2])
        cur.execute("""
            INSERT INTO PEDIDOS_ITEMS (pedido_id, produto_id, quantidade, preco)
            VALUES (%s, %s, %s, %s)
        """, (pedido_id, produto_id, quantidade, preco))

        cur.execute("""
            UPDATE CAD_PRODUTO
            SET quantidade = quantidade - %s
            WHERE id = %s
        """, (quantidade, produto_id))


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

@pedidos_blueprint.route('/meus_pedidos')
def meus_pedidos():
    usuario_id = usuario_logado()
    if not usuario_id:
        flash('Você precisa estar logado para acessar seus pedidos.')
        return redirect(url_for('login.login'))  # Redireciona para login se não estiver logado
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT p.id, p.usuario_id, p.order_date, p.total, p.forma_pagamento, p.status, u.nome 
            FROM PEDIDOS p
            JOIN USUARIOS u ON p.usuario_id = u.id
            WHERE p.usuario_id = %s
        """, (usuario_id,))
        pedidos = cur.fetchall()

        lista_pedidos = []
        for pedido in pedidos:
            pedido_id = pedido[0]
            
            # Consulta para obter os itens do pedido
            cur.execute("""
                SELECT pi.produto_id, pi.quantidade, pi.preco, cp.PRODUTO 
                FROM PEDIDOS_ITEMS pi
                JOIN CAD_PRODUTO cp ON pi.produto_id = cp.ID
                WHERE pi.pedido_id = %s
            """, (pedido_id,))            
            itens = cur.fetchall()

            # Adiciona os dados do pedido e seus itens à lista
            lista_pedidos.append({
                'id': pedido[0],
                'usuario_id': pedido[1],
                'order_date': pedido[2],
                'total': pedido[3],
                'forma_pagamento': pedido[4],
                'status': pedido[5],
                'nome_cliente':pedido[6],
                'itens': [{'produto_id': item[0], 'quantidade': item[1], 'preco': item[2], 'nome_produto': item[3]} for item in itens]
            })

        cur.close()

        if lista_pedidos:
            return render_template('pedidos_cliente.html', pedidos=lista_pedidos)
        else:
            flash("Você ainda não fez nenhum pedido.")
            return redirect(url_for('cadastroProduto.listar_produto'))  # Redireciona caso não haja pedidos

    except Exception as e:
        flash(f"Erro ao listar pedidos: {e}")
        return redirect(url_for('pedidos.meus_pedidos'))  # Redireciona para a mesma página se ocorrer um erro




# Parte Administrativa
@pedidos_blueprint.route('/listar_pedidos')
def listar_pedidos():
    try:   
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT p.id, p.usuario_id, p.order_date, p.total, p.forma_pagamento, p.status, u.nome 
            FROM PEDIDOS p
            JOIN USUARIOS u ON p.usuario_id = u.id
        """)
        pedidos = cur.fetchall()

        lista_pedidos = []
        for pedido in pedidos:
            pedido_id = pedido[0]
            
            # Consulta para obter os itens do pedido
            cur.execute("""
                SELECT pi.produto_id, pi.quantidade, pi.preco, cp.PRODUTO 
                FROM PEDIDOS_ITEMS pi
                JOIN CAD_PRODUTO cp ON pi.produto_id = cp.ID
                WHERE pi.pedido_id = %s
            """, (pedido_id,))            
            itens = cur.fetchall()

            # Adiciona os dados do pedido e seus itens à lista
            lista_pedidos.append({
                'id': pedido[0],
                'usuario_id': pedido[1],
                'order_date': pedido[2],
                'total': pedido[3],
                'forma_pagamento': pedido[4],
                'status': pedido[5],
                'nome_cliente':pedido[6],
                'itens': [{'produto_id': item[0], 'quantidade': item[1], 'preco': item[2], 'nome_produto': item[3]} for item in itens]
            })

        cur.close()
        return lista_pedidos
    
    except Exception as e:
        print("Erro ao listar pedidos:", str(e))
        return "Erro ao listar pedidos", 500

@pedidos_blueprint.route('/atualizar_status/<int:pedido_id>', methods=['POST'])
def atualizar_status(pedido_id):
    try:
        cur = mysql.connection.cursor()

        # Atualizando o status do pedido para "Concluído"
        cur.execute("UPDATE PEDIDOS SET status = 'Concluído' WHERE id = %s", (pedido_id,))
        mysql.connection.commit()

        cur.close()

        # Redireciona de volta para a lista de pedidos
        return redirect(url_for('pedidos.listar_pedidos'))

    except Exception as e:
        print(f"Erro ao atualizar status do pedido: {e}")
        return "Erro ao atualizar status", 500
