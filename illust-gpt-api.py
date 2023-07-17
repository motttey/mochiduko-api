# -*- Coding: utf-8 -*-
import json
import codecs
import os
import requests
import urllib.request

def generate_image_response(prompt=''):
	API_KEY = os.environ.get("CHATGPT_TOKEN")

	# promptがない場合
	if not prompt:
		return

	headers = {
		'Content-Type': 'application/json',
		'Authorization': 'Bearer ' + API_KEY
	}

	data = {
		# 'model': 'text-curie-001', # 動作テスト用（料金的に）
		'prompt': prompt,
		"n": 2,
		"size": "1024x1024"
	}

	response = requests.post('https://api.openai.com/v1/images/generations', headers=headers, data=json.dumps(data))

	# レスポンス受け取り後の処理
	response_data = response.json()
	return response_data

if __name__ == '__main__':
    response_data = generate_image_response(prompt='Doraemon in Japanese Cartoon Style')
    illust_data = response_data["data"]
    output_array = []
    for index, illust in enumerate(illust_data):
        fname = "generated_1_{0}.jpg".format(index)
        urllib.request.urlretrieve(illust["url"], "public/" + fname)
        output_array.append({
              "image": fname,
              "url": illust["url"]
        })

    f1 = codecs.open("public/generated_doraemon_illust.json", "w", "utf-8")
    json.dump({
          "created": response_data,
          "data": output_array
    }, f1, ensure_ascii=False)
