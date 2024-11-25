from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from config import mysql
import base64
from flask_mysqldb import MySQL
import MySQLdb

cadastroProduto_blueprint = Blueprint('cadastroProduto', __name__)

# Area Administrativa
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
            produtos['quantidade'],
            imagem_data
        ))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login.admin_cad'))
    
@cadastroProduto_blueprint.route('/admin/produtos', methods=['GET'])
def listar_produtos_admin():
    
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM CAD_PRODUTO")
        produtos = cur.fetchall()
        cur.close()

        print("Produtos retornados do banco:", produtos, flush=True ) # Verifique os dados aqui
        produtos_com_imagem = []
        for produto in produtos:
            imagem_b64 = base64.b64encode(produto[5] or b'').decode('utf-8') if produto[5] else 'fallback-image.png'
            produtos_com_imagem.append({
            "id": produto[0],
            "nome": produto[1],
            "preco": produto[2],
            "descricao": produto[3],
            "quantidade": produto[4],
            "imagem": imagem_b64  
        })

            print("Produtos enviados ao template:", produtos_com_imagem)  # Verifique aqui também

        return render_template('areaADM.html', produtos=produtos_com_imagem)

        

@cadastroProduto_blueprint.route('/editar_produto/<int:produto_id>', methods=['GET', 'POST'])
def editar_produto(produto_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'GET':
        cur.execute("SELECT * FROM CAD_PRODUTO WHERE ID = %s", (produto_id,))
        produto = cur.fetchone()
        
        if not produto:
            flash('Produto não encontrado.', 'danger')
            return redirect(url_for('login.admin_cad'))        
        
        return render_template('editar_produto.html', produto=produto)

    elif request.method == 'POST':
            # Atualizar o produto com os novos dados do formulário
            nome = request.form['produto']
            preco = request.form['preco']
            descricao = request.form['descricao']
            quantidade = request.form['quantidade']
            imagem = request.files.get('imagem')
            
            if imagem and imagem.filename !='':
                imagem_data = imagem.read()
                cur.execute("""
                    UPDATE CAD_PRODUTO 
                    SET PRODUTO = %s, PRECO = %s, DESCRICAO = %s, QUANTIDADE = %s, IMAGEM = %s
                    WHERE ID = %s
                """, (nome, preco, descricao, quantidade, imagem_data, produto_id))
            else:
                cur.execute("""
                    UPDATE CAD_PRODUTO 
                    SET produto = %s, preco = %s, descricao = %s, quantidade = %s
                    WHERE id = %s
                """, (nome, preco, descricao, quantidade, produto_id))

            mysql.connection.commit()
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('login.admin_cad'))

    

@cadastroProduto_blueprint.route('/deletar_produto/<int:id>', methods=["POST"])
def deletar_produto(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("UPDATE CAD_PRODUTO SET ATIVO = 0 WHERE ID = %s", (id,))
    mysql.connection.commit()

    return redirect(url_for('login.admin_cad'))

@cadastroProduto_blueprint.route('/reativar_produto/<int:id>', methods=["POST"])
def reativar_produto(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("UPDATE CAD_PRODUTO SET ATIVO = 1 WHERE ID = %s", (id,))
    mysql.connection.commit()

    return redirect(url_for('login.admin_cad'))

# Área do Cliente #

def usuario_logado():
    usuario_id = session.get('usuario_id') 
    
    if not usuario_id:
        flash('Você precisa estar logado para adicionar ao carrinho.')
        return None
    return usuario_id
   
@cadastroProduto_blueprint.route('/produto', methods=['GET'])
def listar_produto():
      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM CAD_PRODUTO WHERE ATIVO =1")
      produto = cur.fetchall()
      cur.close()

        # Codificar a imagem em base64
      produtos_com_imagem = []
      for prod in produto:
        imagem_b64 = base64.b64encode(prod[5]).decode('utf-8')  
        produtos_com_imagem.append((*prod[:5], imagem_b64))  

      return render_template('produto.html', produtos=produtos_com_imagem)

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

@cadastroProduto_blueprint.route('/atualizar_quantidade', methods=['POST'])
def atualizar_quantidade():
    data = request.get_json()
    item_id = data.get('item_id')
    nova_quantidade = data.get('nova_quantidade')

    if not item_id or not nova_quantidade:
        return jsonify({'error': 'Dados inválidos'}), 400

    usuario_id = usuario_logado()
    if not usuario_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE CARRINHO
        SET quantidade = %s
        WHERE produto_id = %s AND usuario_id = %s
    """, (nova_quantidade, item_id, usuario_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({'success': True})