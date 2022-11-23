# -*- Coding: utf-8 -*-
from pixivpy3 import *
import json
import csv
import codecs
import requests
import pathlib
import cv2
import os
import numpy as np
from PIL import Image
from sklearn.decomposition import PCA
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

def parse_pixiv(refresh_token, user_num):
    illust_count = 0
    illust_total_view = 0
    illust_total_bookmark = 0
    illust_total_comments = 0

    manga_count = 0
    manga_total_view = 0
    manga_total_bookmark = 0
    manga_total_comments = 0

    each_illusts = []

    each_years = {
        "2022": [],
        "2021": [],
        "2020": [],
        "2019": [],
        "2018": [],
        "2017": [],
        "2016": [],
        "2015": [],
        "2014": [],
        "2013": [],
        "2012": [],
        "2011": [],
        "2010": [],
        "2009": [],
        "2008": []
    }

    api = AppPixivAPI()
    api.auth(refresh_token=refresh_token)

    json_result = api.user_illusts(user_num)
    for illust in json_result.illusts:
        year = illust.create_date.split('-')[0]
        each_years[year].append(illust.id)

        illust_count = illust_count + 1
        illust_total_view = illust_total_view + illust.total_view
        illust_total_bookmark = illust_total_bookmark + illust.total_bookmarks
        illust_total_comments = illust_total_comments + illust.total_comments

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

                each_illusts.append(get_illust_obj(illust))

            next_url = next_result.next_url
            print(next_url)
        except Exception as e:
            print("end")
            flag = 1

    json_result_manga = api.user_illusts(user_num, type="manga")
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
            print("end")
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

    target_list = ['http://embed.pixiv.net/decorate.php?illust_id=' + str(p['id']) + '&mode=sns-automator' for p in each_illusts]
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
        resized_img = cv2.resize(img, (128, 128))
        cv2.imwrite(png_path, resized_img)

        print("convert image to webp:" + str(output))
        image_webp = Image.open(png_path).convert('RGB')
        image_webp.save(webp_path, 'webp')
    return

def apply_tsne(each_illusts):
    target_dir = 'public/thumbs/'
    path = pathlib.Path(target_dir).glob('*.png')

    path_list = [pathlib.Path(target_dir + str(p['id']) + '.png') for p in each_illusts]

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

'''
get reflesh token
https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362
https://gist.github.com/upbit/6edda27cb1644e94183291109b8a5fde
'''
if __name__ == '__main__':
    refresh_token = os.environ.get("REFLESH_TOKEN")
    user_num = os.environ.get("USER_NUM")

    each_illusts_json, each_years_json, total_stat_json = parse_pixiv(refresh_token, user_num)
    each_illusts_json = each_illusts_json[0:500]

    download_image_from_pixiv(each_illusts_json)
    each_illusts_tsne_json = apply_tsne(each_illusts_json)

    f1 = codecs.open("public/each_illusts.json", "w", "utf-8")
    json.dump(each_illusts_tsne_json, f1, ensure_ascii=False)

    f2 = codecs.open("public/each_years.json", "w", "utf-8")
    json.dump(each_years_json, f2, ensure_ascii=False)

    f3 = codecs.open("public/total_stat.json", "w", "utf-8")
    json.dump(total_stat_json, f3, ensure_ascii=False)
