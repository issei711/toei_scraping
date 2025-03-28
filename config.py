import os
import json
import base64
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

class Config:
    SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY")
    GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

    print("GOOGLE_CREDENTIALS_JSON:", os.getenv("GOOGLE_CREDENTIALS_JSON")[:30])
    print("SPREADSHEET_KEY:", os.getenv("SPREADSHEET_KEY"))

    if not GOOGLE_CREDENTIALS_JSON:
        raise ValueError("環境変数 GOOGLE_CREDENTIALS_JSON が設定されていません。")

    try:
        # ✅ `base64` からデコードして JSON に戻す
        json_str = base64.b64decode(GOOGLE_CREDENTIALS_JSON).decode('utf-8')
        GOOGLE_CREDENTIALS = json.loads(json_str)
    except Exception as e:
        raise ValueError(f"GOOGLE_CREDENTIALS_JSON のデコードに失敗しました: {e}")
