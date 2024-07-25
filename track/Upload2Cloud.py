# -*- coding: utf-8 -*-
import requests

def send_json_to_url(json_data,token,url):
    # 设置要发送的JSON数据
    params = json_data
    # 设置请求头
    headers = {
        "Authorization": token  # 替换为您的访问令牌
    }
    # 发送POST请求，传送JSON数据
    response = requests.post(url, json=params, headers=headers)
    # 检查响应
    if response.status_code == 200:
        print('111')
    else:
        print('000')

def send_delete_to_url(token,url):
    # 设置请求头
    headers = {
        "Authorization": token  # 替换为您的访问令牌
    }
    # 发送POST请求，传送JSON数据
    response = requests.get(url, headers=headers)
    # 检查响应
    if response.status_code == 200:
        print('111')
    else:
        print('000')


if __name__ == '__main__':
    json_data = {
        'name': 'value1',
        'id': 2
    }
    url = "http://10.161.148.203:8881/Unrestricted/cin"
    send_json_to_url(json_data,url)
