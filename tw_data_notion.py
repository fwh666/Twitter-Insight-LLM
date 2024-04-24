# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime, timedelta
import re
import json
import time
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import logging
from config import TWITTER_AUTH_TOKEN
import os
from notion_client import Client


def get_message_ids():
    set_message_ids = set()
    # 判断文件是否存在
    result_path = os.path.join(os.path.dirname(__file__), "data", f'twitter-noiton.json')
    if not os.path.exists(result_path):
        print(f'[文件不存在:{result_path}')
        return set_message_ids
    # 读取json文件
    try:
        with open(result_path, 'r') as file:
            for line in file:
                if len(line) > 0:
                    obj = json.loads(line)
                    set_message_ids.add(obj['tweet_id'])
    except Exception as e:
        print(f'[初始化...已记录nodeId数量:{len(set_message_ids)}]')
    return set_message_ids


def fetch_tweets_detail_json(exist_ids, filename):
    # 文件是否存在
    if not os.path.exists(filename):
        return
    # urls=[]
    pages = []
    # exist_ids=self.get_message_ids()
    with open(filename) as f:
        for line in f:
            row = json.loads(line)

            url = row['url']
            # 判断数据是否存在
            tweet_id = re.search(r'/status/(\d+)', url).group(1)
            if tweet_id in exist_ids:
                continue
            page = {
                'tweet_id': tweet_id,
                'text': row['text'],
                'author_name': row['author_name'],
                'author_handle': row['author_handle'],
                'date': row['date'],
                'lang': row['lang'],
                'url': row['url'],
                'mentioned_urls': row['mentioned_urls'],
                'is_retweet': row['is_retweet'],
                'media_type': row['media_type'],
                'images_urls': row['images_urls'],
                'num_reply': row['num_reply'],
                'num_retweet': row['num_retweet'],
                'num_like': row['num_like'],
            }
            pages.append(page)
    return pages


class NotionClient:
    def __init__(self):
        """
        初始化
        """
        global global_query_results
        global global_notion
        global global_database_id
        global_token = "secret_SGSgYlUHk8knQRLcwJr1alzjzVTwXFwrr0UDBawy0Sw"
        global_database_id = "294cc39bf0424a5ca79de50d76e2f6e1"
        global_notion = Client(auth=global_token)
        global_query_results = global_notion.databases.query(database_id=global_database_id)
        print('Notion初始化...')

    """
    创建新的页面
    1. 属性名字和字段个数要对应上
    2. 不同的属性用不同的构参方式
    """

    def create_page(self, page):
        new_page = global_notion.pages.create(
            parent={
                'database_id': global_database_id
            },
            properties={
                'Name': {
                    'title': [
                        {
                            'text': {
                                'content': 'title'
                            }
                        }
                    ]
                },
                'tweet_id': {
                    'rich_text': [
                        {
                            'text': {
                                'content': page['tweet_id']
                            }
                        }
                    ]
                },
                '正文内容': {
                    'rich_text': [
                        {
                            'text': {
                                'content': page['text']
                            }
                        }
                    ]
                },
                "Tags": {
                    "multi_select": [
                        {
                            "name": "初始化"
                        }
                    ]
                },
                '昵称new': {
                    'rich_text': [
                        {
                            'text': {
                                'content': page['author_name']
                            }
                        }
                    ]
                },
                "点赞数": {
                    "number": page['num_like']
                },
                "评论数": {
                    "number": page['num_reply']
                },
                "转发数": {
                    "number": page['num_retweet']
                },
                '发布人': {
                    'rich_text': [
                        {
                            'text': {
                                'content': page['author_handle']
                            }
                        }
                    ]
                },
                "正文地址URL": {
                    'url': page['url']
                },
                "图片文件": {
                    "files": [
                        {
                            "name": "文件1",
                            "type": "external",
                            "external": {
                                "url": page['images_urls']
                                # "url": 'https://pbs.twimg.com/media/GL5a29dXUAAbvoM.jpg'
                            }
                        }
                    ]
                },
                'media_type': {
                    'select': {
                        'name': page['media_type']
                    }
                },
                "原始URL": {
                    'url': page['url']
                },
                "发布时间": {
                    "date": {
                        "start": page['date'],
                    }
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": page['text']
                                }
                            }
                        ]
                    }
                }
            ]
        )
        return new_page


def _save_to_notion(client, pages):
    try:
        inserted_pages = []
        for page in pages:
            try:
                # 判断数据是否存在
                new_page = client.create_page(page)
                store_page = {
                    "pageId": new_page['id'],
                    "tweet_id": page['tweet_id']
                }
                inserted_pages.append(store_page)
                print(f"Save Notion:  {page['tweet_id']}")
            except Exception as e:
                print(e)
                continue
        # Notion数据保存记录
        notion_path = os.path.join(os.path.dirname(__file__), "data", f'twitter-noiton.json')
        with open(notion_path, 'a') as f:
            for i in inserted_pages:
                json.dump(i, f)
                f.write('\n')
            f.close()
    except Exception as e:
        print(e)


def save_notion():
    from groq_util import groq_api
    client = NotionClient()
    file_path = '/Users/fwh/fuwenhao/Github/Twitter-Insight-LLM/data/ClutchPoints_2024-04-24_10-58-53.json'
    exist_ids = get_message_ids()
    # 分开查询详情
    pages = fetch_tweets_detail_json(exist_ids=exist_ids, filename=file_path)
    # 4. 大模型翻译
    for page in pages:
        if 'Image' in page['media_type']:
            URL = page['images_urls'][0].split("?")[0]
            page['images_urls'] = f'{URL}.png'
        if 'Video' in page['media_type']:
            page['images_urls'] = 'https://pbs.twimg.com/media/GL5a29dXUAAbvoM?format=jpg&name=small'
        if page['author_name'] in ['NBA', 'ClutchPoints']:
            page['text'] = groq_api(page['text'])
    _save_to_notion(client=client, pages=pages)
    # 删除json文件
    os.remove(file_path)


if __name__ == "__main__":
    save_notion()
