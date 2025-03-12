import os
import sys

# `app/` のパスを明示的に追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, render_template
from app.scraper import toei_scraping_main

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")  # ✅ テンプレートフォルダを明示

@app.route('/')
def home():
    return render_template('index.html')  # ✅ パスを修正

@app.route('/scraping', methods=['GET'])
def scraping():
    """BeautifulSoup を使ったスクレイピングを実行"""
    try:
        toei_scraping_main()  # ✅ スクレイピング処理を実行
        return render_template('success.html')  # ✅ パスを修正
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
