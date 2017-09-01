# -*- coding:utf-8 -*_
import requests
import re,os


mail = os.getenv('mail')
password = os.getenv('password')
api_key = os.getenv('api_key')

headers={
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"zh-CN,zh;q=0.8",
    "Cache-Control":"no-cache",
    "Connection":"keep-alive",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36"
}
def send_simple_message(sms):
    return requests.post(
        "https://api.mailgun.net/v3/sandbox3a97c3cdddf14319a592252d5a6a0192.mailgun.org/messages",
        auth=("api", api_key),
        data={"from": "Mailgun Sandbox <postmaster@sandbox3a97c3cdddf14319a592252d5a6a0192.mailgun.org>",
              "to": "dataos <mail.dataos@mailhero.io>",
              "subject": "ss node info",
              "text": sms})

def cccat(url,email,pwd):
    print(url)
    loginUrl=url+'/user/_login.php'
    checkinUrl=url+'/user/_checkin.php'
    indexUrl=url+'/user/index.php'
    nodeUrl=url+'/user/node.php'
    data={}
    data["email"] = email
    data["passwd"] = pwd
    data["remember_me"] = 'week'
    session = requests.Session()
    session.headers = headers
    #登陆
    login=session.post(loginUrl,data=data)
    #index page
    indexPage1=session.get(indexUrl).text
    # 签到
    patternCheckined = re.compile(r'<p><a class="btn btn-success btn-flat disabled" href="#">(.*?)</a> </p>', re.S)
    checkinedItems = re.findall(patternCheckined, indexPage1)
    session.get(checkinUrl)
    #获取流量信息traffic
    indexPage = session.get(indexUrl).text

    pattern_indexPage=re.compile(r'<p> 已用流量：(.*?GB).*?<p> 剩余流量：(.*?GB).*?<p> 最后使用时间：(.*?) </p>.*?<p>上次签到时间：<code>(.*?)</code></p>',re.S)
    trafficContents=re.findall(pattern_indexPage,indexPage)
    tracfficInfo=trafficContents[0][0]+"/"+trafficContents[0][1]
    lastUsed=trafficContents[0][2]
    lastCheckin=trafficContents[0][3]
    userInfo=tracfficInfo+" "+lastUsed+" "+lastCheckin
    # print(userInfo)

    #节点信息
    nodesPage=session.get(nodeUrl).text
    patterns_nodePage=re.compile(r'class="node-info" role="menuitem" tabindex="-1" href="(node_qr.*?)">.*?</a></li>\s+</ul>\s+</li>\s+<li.*? class="fa fa-angle-right"></i>(.*?)</li>',re.S)
    nodeQRUrls=re.findall(patterns_nodePage,nodesPage)
    ssrInfos = []
    ssrInfos.append(url)
    ssrInfos.append(userInfo)
    for nodeqr in nodeQRUrls:
        ssrLocation=nodeqr[1]
        nodeQRUrl=url+"/user/"+nodeqr[0]
        nodeQRPage=session.get(nodeQRUrl).text
        patternQR=re.compile(r'<p class="well well-sm" style="overflow-wrap: break-word;">(ssr://.*?)</p>',re.S)
        ssrUrl=re.findall(patternQR,nodeQRPage)
        ssrInfo=ssrLocation.strip()+"\r\n"+ssrUrl[1].strip()
        print(ssrInfo)
        ssrInfos.append(ssrInfo)
    # print(ssrInfos)
    send_simple_message(ssrInfos)

cccat('https://cccat.pw',mail,password)
