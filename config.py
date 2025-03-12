import os
import json
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY")  # 環境変数から取得

    # Google API 認証情報を環境変数から取得
    GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if GOOGLE_CREDENTIALS_JSON:
        GOOGLE_CREDENTIALS = os.path.join(BASE_DIR, "config.json")
        with open(GOOGLE_CREDENTIALS, "w") as f:
            json.dump(json.loads(GOOGLE_CREDENTIALS_JSON), f)
    else:
        raise ValueError("環境変数 GOOGLE_CREDENTIALS_JSON が設定されていません。")
