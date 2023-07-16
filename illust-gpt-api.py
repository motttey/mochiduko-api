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
    '''
    sample_data = {
        "created": 1688992473,
        "data": [
            {
                "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/org-7gTS3GqOAZliITd7wz9gaFW3/user-5KZ3kkHahE5MRRmCBJOeu9vB/img-kk8psla1OH8NUXTFtzRScful.png?st=2023-07-10T11%3A34%3A33Z&se=2023-07-10T13%3A34%3A33Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-07-09T14%3A52%3A35Z&ske=2023-07-10T14%3A52%3A35Z&sks=b&skv=2021-08-06&sig=gSL7EZE%2BgNiC0TEu1c1eCPSj2TY6ygDL/qn6rJpgS/s%3D"
            },
            {
                "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/org-7gTS3GqOAZliITd7wz9gaFW3/user-5KZ3kkHahE5MRRmCBJOeu9vB/img-yXP6mLs6k5jlZLVyZjnQ9rSk.png?st=2023-07-10T11%3A34%3A33Z&se=2023-07-10T13%3A34%3A33Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-07-09T14%3A52%3A35Z&ske=2023-07-10T14%3A52%3A35Z&sks=b&skv=2021-08-06&sig=GQuH8SlgXnYrqpimIyo6HIvHgWDYrt7s8HN/tl9uCzs%3D"
            }
        ]
    }
    '''

    response_data = generate_image_response(prompt='Doraemon in Japanese Cartoon Style')
    illust_data = response_data["data"]
    output_array = []
    for index, illust in enumerate(illust_data):
        fname = "generated_1_{0}.jpg",format(index)
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
