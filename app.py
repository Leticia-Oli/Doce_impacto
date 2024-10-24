from config import app
from blueprints.login_routes import login_blueprint
from blueprints.cadastro_routes import cadastro_blueprint
from blueprints.cadastroProduto import cadastroProduto_blueprint

app.register_blueprint(login_blueprint)
app.register_blueprint(cadastro_blueprint)
app.register_blueprint(cadastroProduto_blueprint)


if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])
