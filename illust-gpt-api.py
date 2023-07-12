# -*- Coding: utf-8 -*-
import json
import codecs
import os

if __name__ == '__main__':
    ghatgpt_api_token = os.environ.get("CHATGPT_API_TOKEN")

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

    f1 = codecs.open("public/generated_doraemon_illust.json", "w", "utf-8")
    json.dump(sample_data, f1, ensure_ascii=False)
