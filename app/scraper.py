import os
import requests
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from config import Config  # Flask の `config.py` をインポート

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

# HTMLから要素を取得する関数（XPATH）
def get_element(soup, selector):
    element = soup.select_one(selector)
    return element.get_text(strip=True) if element else ""

# フラグやその他リストの要素を取得
def get_list_elements(soup, xpaths):
    elements = []
    for xpath in xpaths:
        element = get_element(soup, xpath)
        if element:
            elements.append(element)
    return "\n".join(list(set([flag for elem in elements for flag in elem.split("\n") if flag])))

# スクレイピング処理
def toei_scraping_main():
    print("Starting scraping process...")  # ✅ デバッグログ追加

    # Google API 認証設定
    SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_dict(Config.GOOGLE_CREDENTIALS, SCOPE)
    GC = gspread.authorize(CREDENTIALS)
    WORKSHEET = GC.open_by_key(Config.SPREADSHEET_KEY).worksheet('新規案件URL貼り付け')

    try:
        # 最終行の取得
        url_last_row = len(WORKSHEET.col_values(2))
        print(f"Last row in spreadsheet: {url_last_row}")  # ✅ デバッグログ追加
        # start_row = int(WORKSHEET.acell('A1').value) + 1
        start_row = int(WORKSHEET.acell('A1').value) + 1
        end_row = url_last_row
        urls = [row[0] for row in WORKSHEET.get(f"B{start_row}:B{end_row}") if row]

        for url in urls:
            print(f"Fetching data from {url}")  # ✅ デバッグログ追加
            headers = {"User-Agent": USER_AGENTS[0]}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # データを抽出
            job_num = get_element(soup, "#contents > div:nth-of-type(4) > div > div > p:nth-of-type(2) > span").split("仕事No.：")[-1]
            title = get_element(soup, "#contents > div:nth-of-type(2) > div > div:nth-of-type(2) > h2")
            sub_title = get_element(soup, "#contents > div:nth-of-type(2) > div > div:nth-of-type(2) > p")
            salary = get_element(soup, "#contents > div:nth-of-type(3) > div > div > div:nth-of-type(1) > div > dl:nth-of-type(2) > dd > ul:nth-of-type(2) > li > p > em")
            salary_detail = get_element(soup, "#contents > div:nth-of-type(3) > div > div > div:nth-of-type(1) > div > dl:nth-of-type(2) > dd > div > ul:nth-of-type(2) > li > ul")
            job_time = get_element(soup, "#contents > div:nth-of-type(3) > div > div > div:nth-of-type(1) > div > dl:nth-of-type(3) > dd > ul:nth-of-type(2) > li > p > em")
            job_time_detail = get_element(soup, "#contents > div:nth-of-type(3) > div > div > div:nth-of-type(1) > div > dl:nth-of-type(3) > dd > ul:nth-of-type(3) > li > ul")
            area = get_element(soup, "#contents > div:nth-of-type(3) > div > div > div:nth-of-type(1) > div > dl:nth-of-type(4) > dd > dl:nth-of-type(3) > dd > ul > li")
            access = get_element(soup, "#contents > div:nth-of-type(3) > div > div > div:nth-of-type(1) > div > dl:nth-of-type(4) > dd > dl:nth-of-type(2) > dd")
            job = get_element(soup, "#contents > div:nth-of-type(8) > div > div:nth-of-type(2) > div > div > dl:nth-of-type(1) > dd > p")
            between_detail = get_element(soup, "#contents > div:nth-of-type(8) > div > div:nth-of-type(2) > div > div > dl:nth-of-type(3) > dd > p").split("\n")[1] if "\n" in get_element(soup, "#contents > div:nth-of-type(8) > div > div:nth-of-type(2) > div > div > dl:nth-of-type(3) > dd > p") else ""
            holiday = get_element(soup, "#contents > div:nth-of-type(8) > div > div:nth-of-type(2) > div > div > dl:nth-of-type(4) > dd > p")
            experience = get_element(soup, "#contents > div:nth-of-type(8) > div > div:nth-of-type(2) > div > div > dl:nth-of-type(5) > dd > p")
            benefits = get_element(soup, "#contents > div:nth-of-type(8) > div > div:nth-of-type(2) > div > div > dl:nth-of-type(6) > dd > p")

            # 社員登用後の条件
            after_selectors = [
            "#contents > div:nth-of-type(9) > div > div:nth-of-type(2) > div > dl:nth-of-type(1) > dt > span",
            "#contents > div:nth-of-type(9) > div > div:nth-of-type(2) > div > dl:nth-of-type(2) > dt > span",
            "#contents > div:nth-of-type(9) > div > div:nth-of-type(2) > div > dl:nth-of-type(3) > dt > span",
            "#contents > div:nth-of-type(9) > div > div:nth-of-type(2) > div > dl:nth-of-type(1) > dd > p",
            "#contents > div:nth-of-type(9) > div > div:nth-of-type(2) > div > dl:nth-of-type(2) > dd > p",
            "#contents > div:nth-of-type(9) > div > div:nth-of-type(2) > div > dl:nth-of-type(3) > dd > p"
            ]
            after_values = []

            for selector in after_selectors:
                element = get_element(soup, selector)
                element = replace_newlines(element)
                after_values.append(element)

            # フラグ取得
            flags_string = get_list_elements(soup, [
                "#contents > div:nth-of-type(3) > div > div > div:nth-of-type(1) > div > dl:nth-of-type(2) > dd > ul:nth-of-type(1)",
                "#contents > div:nth-of-type(3) > div > div > div:nth-of-type(1) > div > dl:nth-of-type(3) > dd > ul:nth-of-type(1)",
                "#contents > div:nth-of-type(3) > div > div > div:nth-of-type(1) > div > dl:nth-of-type(4) > dd > ul",
                "#contents > div:nth-of-type(6) > div > div:nth-of-type(2) > dl:nth-of-type(1) > dd > ul",
                "#contents > div:nth-of-type(6) > div > div:nth-of-type(2) > dl:nth-of-type(2) > dd > ul",
                "#contents > div:nth-of-type(6) > div > div:nth-of-type(2) > dl:nth-of-type(3) > dd > ul",
                "#contents > div:nth-of-type(6) > div > div:nth-of-type(2) > dl:nth-of-type(4) > dd > ul",
                "#contents > div:nth-of-type(6) > div > div:nth-of-type(2) > dl:nth-of-type(5) > dd > ul",
                "#contents > div:nth-of-type(6) > div > div:nth-of-type(2) > dl:nth-of-type(7) > dd > ul",
                "#contents > div:nth-of-type(8) > div > div:nth-of-type(2) > div > div > dl:nth-of-type(4) > dd > ul",
                "#contents > div:nth-of-type(8) > div > div:nth-of-type(2) > div > div > dl:nth-of-type(5) > dd > ul",
                "#contents > div:nth-of-type(8) > div > div:nth-of-type(2) > div > div > dl:nth-of-type(6) > dd > ul"
            ])

            # 改行を<BR>に変換
            values = [
                replace_newlines(job_num), replace_newlines(title), replace_newlines(sub_title),
                replace_newlines(salary), replace_newlines(salary_detail), replace_newlines(job_time),
                replace_newlines(job_time_detail), replace_newlines(area), replace_newlines(access),
                replace_newlines(job), replace_newlines(between_detail), replace_newlines(holiday),
                replace_newlines(experience), replace_newlines(benefits), replace_newlines(flags_string)
            ]

            WORKSHEET.update(f'C{start_row}:Q{start_row}', [values])  # メインの情報
            WORKSHEET.update(f'R{start_row}:W{start_row}', [after_values])  # 社員登用後の条件
            print(f"Saved to spreadsheet: {values}")  # ✅ デバッグログ追加
            start_row += 1

    except Exception as e:
        print(f"Scraping failed due to: {e}")  # ✅ エラーログ追加
