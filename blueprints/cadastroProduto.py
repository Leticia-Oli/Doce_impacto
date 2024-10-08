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
    # Aqui você precisaria identificar o usuário atual (por exemplo, através de um login).
    usuario_id = session.get('usuario_id')  # Exemplo de como pegar o ID do usuário logado
    
    if not usuario_id:
        flash('Você precisa estar logado para adicionar ao carrinho.')
        return redirect(url_for('login.login'))  # Redireciona para login se o usuário não estiver logado

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
    usuario_id = session.get('usuario_id')  # Identifique o usuário logado

    if not usuario_id:
        flash('Você precisa estar logado para ver o carrinho.')
        return redirect(url_for('login'))

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
    # Limpar o carrinho na sessão
    usuario_id = session.get('usuario_id')
    session.pop('carrinho', None)  # Remove o carrinho da sessão
    
    cur = mysql.connection.cursor()
    cur.execute("""
            DELETE FROM CARRINHO WHERE usuario_id= %s
        """, (usuario_id,))
    mysql.connection.commit ()

    flash('Carrinho limpo com sucesso!')  # Mensagem de sucesso
    return redirect(url_for('cadastroProduto.ver_carrinho'))  # Redireciona para a página do carrinho

     

