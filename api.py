from pixivpy3 import *
import json
import codecs
import requests
import pathlib
import cv2
import os
import numpy as np
from PIL import Image
from sklearn.manifold import TSNE

def get_illust_obj(illust):
    return {
        "title": illust.title,
        "date": illust.create_date.split('T')[0],
        "id": illust.id,
        "view": illust.total_view,
        "bookmark": illust.total_bookmarks,
        "comments": illust.total_comments,
        "url": illust.image_urls['large'],
        "tags": illust.tags,
        "width": illust.width,
        "height": illust.height
    }

def parse_pixiv(refresh_token, user_id):
    illust_count = 0
    illust_total_view = 0
    illust_total_bookmark = 0
    illust_total_comments = 0

    manga_count = 0
    manga_total_view = 0
    manga_total_bookmark = 0
    manga_total_comments = 0

    # 取得したイラストを格納するarray
    each_illusts = []

    # 年ごとに実績を格納するdict
    each_years = {}

    # 非公開イラストのリスト
    ignored_id_list = [95871491, 101336714]

    api = AppPixivAPI()
    api.auth(refresh_token=refresh_token)

    json_result = api.user_illusts(user_id)
    for illust in json_result.illusts:
        year = illust.create_date.split('-')[0]
        if year not in each_years:
            each_years[year] = []
        each_years[year].append(illust.id)
        # print(illust)

        illust_count = illust_count + 1
        illust_total_view = illust_total_view + illust.total_view
        illust_total_bookmark = illust_total_bookmark + illust.total_bookmarks
        illust_total_comments = illust_total_comments + illust.total_comments

        # 公開イラストに絞る
        if int(illust.id) not in ignored_id_list:
            each_illusts.append(get_illust_obj(illust))

    next_url = json_result.next_url
    flag = 0

    while flag == 0:
        try:
            next_qs = api.parse_qs(next_url)
            next_result = api.user_illusts(**next_qs)

            for illust in next_result.illusts:
                year = illust.create_date.split('-')[0]
                each_years[year].append(illust.id)

                illust_count = illust_count + 1
                illust_total_view = illust_total_view + illust.total_view
                illust_total_bookmark = illust_total_bookmark + illust.total_bookmarks
                illust_total_comments = illust_total_comments + illust.total_comments

                if int(illust.id) not in ignored_id_list:
                    each_illusts.append(get_illust_obj(illust))

            next_url = next_result.next_url
            print(next_url)
        except Exception as e:
            print("end")
            flag = 1

    json_result_manga = api.user_illusts(user_id, type="manga")
    for manga in json_result_manga.illusts:
        year = manga.create_date.split('-')[0]

        each_years[year].append(manga.id)
        # for page in manga.meta_pages:
        #     each_years[year].append(page)

        manga_count = manga_count + 1
        manga_total_view = manga_total_view + manga.total_view
        manga_total_bookmark = manga_total_bookmark + manga.total_bookmarks
        manga_total_comments = manga_total_comments + manga.total_comments

        each_illusts.append(get_illust_obj(manga))

    next_url = json_result_manga.next_url
    flag = 0
    while flag == 0:
        try:
            next_qs = api.parse_qs(next_url)
            next_result = api.user_illusts(**next_qs)

            for manga in next_result.illusts:
                year = manga.create_date.split('-')[0]

                each_years[year].append(manga.id)
                # for page in manga.meta_pages:
                #    each_years[year].append(page)

                manga_count = manga_count + 1
                manga_total_view = manga_total_view + manga.total_view
                manga_total_bookmark = manga_total_bookmark + manga.total_bookmarks
                manga_total_comments = manga_total_comments + manga.total_comments

                each_illusts.append(get_illust_obj(manga))

            next_url = next_result.next_url
            print(next_url)
        except Exception as e:
            print(e)
            flag = 1

    each_years_stat = []
    for key, values in each_years.items():
        each_years_stat.append({
            "year": key,
            "illust_num": len(values)
        })

    total_stat = {
        "total_illusts": illust_count + manga_count,
        "total_views": illust_total_view + manga_total_view,
        "total_bookmarks": illust_total_bookmark + manga_total_bookmark,
        "total_comments": illust_total_comments + illust_total_comments
    }
    return [ each_illusts, each_years_stat, total_stat ]

def download_image_from_pixiv(each_illusts):
    target_dir = 'public/thumbs/'
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    target_list = [
        'http://embed.pixiv.net/decorate.php?illust_id=' + str(p['id']) + '&mode=sns-automator' 
        for p in each_illusts
    ]

    path_list = [pathlib.Path(target_dir + str(p['id'])) for p in each_illusts]

    for target, output in zip(target_list, path_list):
        print("download:" + str(output))

        response = requests.get(target)
        image = response.content
        png_path = str(output) + '.png'
        webp_path = str(output) + '.webp'

        with open(png_path, 'wb') as f:
            f.write(image)

        img = cv2.imread(png_path)

        # 画像がなければcontinue
        if img is None: continue

        resized_img = cv2.resize(img, (128, 128))
        cv2.imwrite(png_path, resized_img)

        print("convert image to webp:" + str(output))
        image_webp = Image.open(png_path).convert('RGB')
        image_webp.save(webp_path, 'webp')
    return

def apply_tsne(each_illusts):
    target_dir = 'public/thumbs/'

    # 画像がダウンロードできたものだけに絞る
    filtered_illusts = [illust for illust in each_illusts if pathlib.Path(target_dir + str(illust['id']) + '.png').exists()]
    path_list = [pathlib.Path(target_dir + str(illust['id']) + '.png') for illust in filtered_illusts]       

    images = np.concatenate([cv2.resize(cv2.imread(str(p)),(64,64)).flatten().reshape(1,-1) for p in path_list], axis=0)

    # t-SNE適用
    tsne = TSNE(n_components=3)
    images_embedded = tsne.fit_transform(images)
    print(images_embedded)

    for i in range(len(each_illusts)):
        each_illusts[i]['tsne-X'] = images_embedded[i][0].astype(float)
        each_illusts[i]['tsne-Y'] = images_embedded[i][1].astype(float)
        each_illusts[i]['tsne-Z'] = images_embedded[i][2].astype(float)

    return each_illusts

def output_file(fname, content):
    output_dir_prefix = "public/"
    f = codecs.open(output_dir_prefix + fname, "w", "utf-8")
    json.dump(content, f, ensure_ascii=False)

'''
get reflesh token
https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362
https://gist.github.com/upbit/6edda27cb1644e94183291109b8a5fde
'''
if __name__ == '__main__':
    refresh_token = os.environ.get("REFLESH_TOKEN")
    user_id = os.environ.get("USER_NUM")
    max_illust_num = 600

    each_illusts_json, each_years_json, total_stat_json = parse_pixiv(refresh_token, user_id)
    each_illusts_json = each_illusts_json[0: max_illust_num]

    download_image_from_pixiv(each_illusts_json[0: max_illust_num])
    each_illusts_tsne_json = apply_tsne(each_illusts_json)

    output_file("each_illusts.json", each_illusts_tsne_json)

    output_file("each_years.json", each_years_json)

    output_file("total_stat.json", total_stat_json)
