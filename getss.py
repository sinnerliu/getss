#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os

mail = os.getenv('mail')
password = os.getenv('password')
api_key = os.getenv('api_key')



def sspanel_v2(url,email,pwd,ss_conf):
    headers = {
        'Host': url,
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'https://'+url,
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'DNT': '1',
        'Referer': 'https://'+url+'/auth/login',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    # proxies = {"http": "http://127.0.0.1:1085", }
    data = {}
    data["email"] = email
    data["passwd"] = pwd
    data["remember_me"] = 'week'
    session = requests.Session()
    session.headers = headers

    # login = session.post('https://'+url+'/auth/login', data=data, headers=headers, proxies=proxies)
    login = session.post('https://' + url + '/auth/login', data=data, headers=headers)
    #签到
    session.post('https://'+url+'/user/checkin', headers=headers)

    re = session.get('https://'+url+'/user').content.decode('UTF-8')
    soup_user = BeautifulSoup(re, "lxml")
    total = soup_user.select(".dl-horizontal")[0].select("dd")[0].get_text()
    used = soup_user.select(".dl-horizontal")[0].select("dd")[1].get_text()
    surplus = soup_user.select(".dl-horizontal")[0].select("dd")[2].get_text()
    last_signed = soup_user.select("code")[0].get_text()

    re_ss = session.get('https://'+url+'/user/node').content.decode('UTF-8')
    soup = BeautifulSoup(re_ss, "lxml")
    ss_num = len(soup.select(".product-info"))
    # print(ss_num)
    ss_conf.append("# 网址："+url+" 节点数："+str(ss_num)+" 总流量：" + total + " 使用流量：" + used + " 剩余流量：" + surplus + " 最后签到时间：" + last_signed )
    for ss_node in soup.select(".product-info"):
        node1 = ss_node.select(".product-title")[0]['href'].replace('.', '')
        country = soup.select(".product-title")[0].get_text().split(" ")[0]
        node_url = 'https://'+url+'/user' + node1
        re_node = session.get(node_url).content.decode('UTF-8')
        soup_node = BeautifulSoup(re_node, "lxml")
        ss_json = soup_node.select(".form-control")[0].get_text()
        ss_info = "#"+country + "\n" + ss_json
        print("# 网址："+url+" 节点数："+str(ss_num)+" 总流量：" + total + " 使用流量：" + used + " 剩余流量：" + surplus + " 最后签到时间：" + last_signed)
        ss_conf.append(ss_info)
    # print(ss_conf)
    # send_simple_message(ss_conf)

def send_simple_message(sms):
    return requests.post(
        "https://api.mailgun.net/v3/sandbox3a97c3cdddf14319a592252d5a6a0192.mailgun.org/messages",
        auth=("api", api_key),
        data={"from": "Mailgun Sandbox <postmaster@sandbox3a97c3cdddf14319a592252d5a6a0192.mailgun.org>",
              "to": "dataos <mail.dataos@mailhero.io>",
              "subject": "ss node info",
              "text": sms})

if __name__ == '__main__':
    ss_conf=[]
    sspanel_v2_url=[
        ['s2.ysee.me',mail,password],
        ['ssplain.com', mail, password],
        ['www.libertyss.cn', mail, password]

    ]

    for urlinfo in sspanel_v2_url:
        print(urlinfo[0])
        sspanel_v2(urlinfo[0],urlinfo[1],urlinfo[2],ss_conf)

    send_simple_message(ss_conf)

    print("over!")
