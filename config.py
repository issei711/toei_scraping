import os
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    GOOGLE_CREDENTIALS = os.path.join(BASE_DIR, "config.json")  # Google API 認証ファイル
    SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY")  # 環境変数から取得
