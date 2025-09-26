import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin,urlparse
import re


# 保存先フォルダ
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'report')
)
os.makedirs(BASE_DIR, exist_ok=True)

# トップページ URL
base_url = 'https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/reports/SS20241129/'

# トップページを取得
resp = requests.get(base_url)
resp.encoding = resp.apparent_encoding
soup = BeautifulSoup(resp.text, 'html.parser')


# 政党ページへのリンクをすべて取得
party_pages = []  # party_pages に (prefix, code, html_url) を保持
#soup.select('table a') がテーブル内の <a> を全部拾ってくる
for a in soup.select('table a[href$=".html"]'):
    href = a['href']
    full_url = urljoin(base_url, href)
    path = urlparse(full_url).path.strip('/').split('/')
    prefix = path[-2]                   # SF, SL, SC, SS, S0 など
    code = os.path.splitext(path[-1])[0]  # 000010, 000020, …（拡張子前）
    party_pages.append((prefix, code, full_url))



for prefix, code, party_url in party_pages:
    r = requests.get(party_url)
    r.encoding = r.apparent_encoding
    soup2 = BeautifulSoup(r.text, 'html.parser')

    for a in soup2.select('a[href$=".pdf"]'):
        pdf_url = urljoin(party_url, a['href'])
        filename = os.path.basename(urlparse(pdf_url).path)

        # “prefix/code” フォルダを作成
        target_dir = os.path.join(BASE_DIR, prefix, code)
        os.makedirs(target_dir, exist_ok=True)

        dst = os.path.join(target_dir, filename)
        if os.path.exists(dst):
            print("skip:", dst)
            continue

        pdf_resp = requests.get(pdf_url)
        with open(dst, 'wb') as fw:
            fw.write(pdf_resp.content)
        print("downloaded:", dst)