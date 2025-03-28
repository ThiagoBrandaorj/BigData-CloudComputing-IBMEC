from flask import Flask
from app.database import db
from app.config import Config
from app.controllers.usuario_controller import usuario_bp
from app.controllers.endereco_controller import endereco_bp
from app.controllers.cartao_controller import cartao_bp
from app.controllers.produto_controller import produto_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(usuario_bp, url_prefix="/usuario")
    app.register_blueprint(endereco_bp, url_prefix="/endereco")
    app.register_blueprint(cartao_bp, url_prefix="/cartao")
    app.register_blueprint(produto_bp, url_prefix="/produto")

    return app
