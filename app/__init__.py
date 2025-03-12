from flask import Flask
from config import Config  # ルートの `config.py` をインポート

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # 設定を適用

    from app.routes import main
    app.register_blueprint(main)

    return app
