import base64
import copy
import json
import os
import pprint
import re
from io import BytesIO
from math import ceil

import requests
from pdf2image import convert_from_path
from prompt import prompt

#環境変数からAPIキーを取得
api_key = os.environ["OPENAI_API_KEY"]

initial_json = {
    "団体情報": {},
    "収入": {
        "合計": 0,
        "会費": 0,
        "個人寄附": 0,
        "法人寄附": 0,
        "政治団体寄附": 0,
        "借入金": [],
        "その他の収入": []
    },
    "支出": {
        "合計": 0,
        "経常経費": {},
        "政治活動費": {}
    },
    "寄附者一覧": []
}

result_json = initial_json

#LLMのコマンドからJSON更新
def apply_updates_to_json(base_json: dict, updates: list) -> dict:
    result = copy.deepcopy(base_json)  # 元を壊さないようにコピー

    for update in updates:
        path_keys = update["path"].split(".")
        data_to_add = update["data"]

        # 階層をたどって target をセット
        target = result
        for key in path_keys[:-1]:
            target = target.setdefault(key, {})

        last_key = path_keys[-1]

        # まだ存在しない場合は初期化
        if last_key not in target:
            # data_to_addの要素がリストかつ中身が辞書なら → list初期化
            if isinstance(data_to_add, list) and all(isinstance(item, dict) for item in data_to_add):
                target[last_key] = []
            # 辞書型（単なるオブジェクト）の場合 → dict初期化
            elif isinstance(data_to_add, list) and all(not isinstance(item, dict) for item in data_to_add):
                target[last_key] = {}
            else:
                # 基本は list 初期化（安全）
                target[last_key] = []

        # 値の型に応じて追加
        if isinstance(target[last_key], list):
            target[last_key].extend(data_to_add)
        elif isinstance(target[last_key], dict):
            for k, v in data_to_add[0].items():
                target[last_key][k] = v
        else:
            raise TypeError(f"パス '{update['path']}' はリストでも辞書でもありません")

    return result

# 解析する画像のファイルパスを指定します。
# スクリプトのあるディレクトリを基準にする場合
base_dir = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(base_dir, "../../data/report/SF/000010/000010_0012.pdf")
images = convert_from_path(pdf_path, dpi=300)

# 画像ファイルをBase64形式にエンコードする関数
def encode_image(image_obj):
    buffer = BytesIO()
    image_obj.save(buffer, format="JPEG")  # PNGでもOK
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

#画像3枚ずつAPIリクエストを送信
batch_size = 3
for batch_index in range(ceil(len(images) / batch_size)):
    start = batch_index * batch_size
    end = start + batch_size
    image_batch = images[start:end]

    # Vision API用コンテンツ構成
    content = [{"type": "text", "text": prompt}]
    for img in image_batch:
        base64_img = encode_image(img)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_img}",
                "detail": "high"
            }
        })

    # APIリクエストを送信するためのヘッダーを設定します。
    headers = {
    "Content-Type": "application/json",  # コンテンツタイプをJSON形式に指定
    "Authorization": f"Bearer {api_key}"  # 認証情報としてBearerトークンを設定
    }

    # APIリクエストの本文（ペイロード）を設定します。
    payload = {
    "model": "gpt-4o",  # 使用するモデル名
    "messages": [
        {
        "role": "user",
        "content": content
        }
    ],
    "max_tokens": 2000  # 最大トークン数を指定
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    data = response.json()
    print(data)
    llm_output = data["choices"][0]["message"]["content"]
    print(llm_output)
    # 差分を適用
    # result_json = apply_update_command(result_json, llm_output)

    # 差分ログを格納するディレクトリを作成
    log_dir = os.path.join(base_dir, "diff_logs")
    os.makedirs(log_dir, exist_ok=True)
    # 差分ログ保存（任意）
    with open(f"diff_batch_{batch_index + 1}.txt", "w", encoding="utf-8") as f:
        f.write(llm_output)
#出力確認
pprint.pprint(result_json, width=120)

