import os
import requests
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from config import Config  # Flask の `config.py` をインポート

# Google API 認証設定
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name(Config.GOOGLE_CREDENTIALS, SCOPE)
GC = gspread.authorize(CREDENTIALS)
WORKSHEET = GC.open_by_key(Config.SPREADSHEET_KEY).worksheet('テスト')

# ユーザーエージェントリスト
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
]

# 改行を `<BR>` に変換する関数
def replace_newlines(value):
    if isinstance(value, str):
        return value.replace("\n", "<BR>")
    elif isinstance(value, list):
        return [replace_newlines(v) for v in value]
    return value

# HTML から要素を取得する関数
def get_element(soup, selector):
    element = soup.select_one(selector)
    return element.get_text(strip=True) if element else ""

# スクレイピング処理
def toei_scraping_main():
    # 最終行の取得
    url_last_row = len(WORKSHEET.col_values(2))
    print(f"last row: {url_last_row}")
    start_row = int(WORKSHEET.acell('A1').value) + 1
    end_row = url_last_row
    urls = [row[0] for row in WORKSHEET.get(f"B{start_row}:B{end_row}") if row]

    for url in urls:
        print(f"Fetching data from {url}")
        try:
            print(f"Fetching data from {url}")

            # HTTPリクエストの送信
            headers = {"User-Agent": USER_AGENTS[0]}
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # BeautifulSoup で HTML を解析
            soup = BeautifulSoup(response.text, "html.parser")

            # データを抽出
            job_num = get_element(soup, "#contents div:nth-of-type(4) div div p:nth-of-type(2) span").split("仕事No.：")[-1]
            title = get_element(soup, "#contents div:nth-of-type(2) div div:nth-of-type(2) h2")
            salary = get_element(soup, "#contents div:nth-of-type(3) div div div:nth-of-type(1) div dl:nth-of-type(2) dd ul:nth-of-type(2) li p em")
            area = get_element(soup, "#contents div:nth-of-type(3) div div div:nth-of-type(1) div dl:nth-of-type(4) dd dl:nth-of-type(3) dd ul li")
            access = get_element(soup, "#contents div:nth-of-type(3) div div div:nth-of-type(1) div dl:nth-of-type(4) dd dl:nth-of-type(2) dd")
            job = get_element(soup, "#contents div:nth-of-type(8) div div:nth-of-type(2) div div dl:nth-of-type(1) dd p")

            # フラグ取得
            flags = soup.select("#contents div:nth-of-type(3) div div div:nth-of-type(1) div dl:nth-of-type(2) dd ul:nth-of-type(1) li")
            flags_text = "\n".join([flag.get_text(strip=True) for flag in flags])

            # データをスプレッドシートに保存
            values = [replace_newlines(job_num), replace_newlines(title), replace_newlines(salary),
                      replace_newlines(area), replace_newlines(access), replace_newlines(job),
                      replace_newlines(flags_text)]

            WORKSHEET.update(f'C{start_row}:I{start_row}', [values])
            start_row += 1

        except Exception as e:
            print(f"Failed to fetch data from {url} due to {e}")
