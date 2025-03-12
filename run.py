import sys
import os

# `app/` のパスを明示的に追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from app.scraper import toei_scraping_main

app = Flask(__name__)

@app.route('/scraping', methods=['GET'])
def scraping():
    """BeautifulSoup を使ったスクレイピングを実行"""
    try:
        toei_scraping_main()
        return jsonify({"message": "Scraping completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
