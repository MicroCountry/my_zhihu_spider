#!/usr/bin/env python
#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import requests
import redis
from lxml import html
import re
from multiprocessing.dummy import Pool
import time
from mongodbs import Zhihu_User_Profile

from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Spider():
    def __init__(self,url,option="print_data_out",proxy=None):
        self.url = url
        try:
            self.number =re.search("([\w|-]+)$",url).group(1)
        except:
            self.number=''
        self.option = option
        self.proxy = proxy
        self.header = {}
        self.header["User-Agent"] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0"
        self.cookies = {
            "q_c1":"fa7be38aa96544b1ac3d3fb6c1538971|1499914412000|1483015223000",
            "d_c0":"AJACTMq5EguPTkQ_iRg2bEN8SRcDRt-r35E=|1483015224",
            "__utma":"51854390.1211345587.1501807644.1501830767.1501850851.6",
            "__utmz":"51854390.1501850851.6.2.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/",
            "_zap":"f4737b72-343c-40ad-9c98-37509a9bfedd",
            "q_c1":"fa7be38aa96544b1ac3d3fb6c1538971|1499914412000|1483015223000",
            "cap_id":"M2Y3MTQ5YmJjZTM3NDg4Y2JiZDdmZGZjNzQyOTYzZWY=|1501852381|dba9c86c422b69eca236f4cdf616c5292124dbb7",
            "_xsrf":"7a8351fb3a3e387369d8bdfe8afd6120",
            "__utmv":"51854390.000--|2=registration_date=20150827=1^3=entry_date=20161229=1",
            "aliyungf_tc":"AQAAAK5S9DLCxwMAtf70ZfT9IyG7Usg7",
            "_xsrf":"7a8351fb3a3e387369d8bdfe8afd6120",
            "anc_cap_id":"c5d51ffdeab443c3855c698f397677b3",
            "__utmb":"51854390.0.10.1501850851",
            "__utmc":"51854390",
            "l_cap_id":"YmI5ODkyOTUyMTkyNDlhNGFiNmJmYzVkYzkyNjJjNjc=|1501852381|f649166aff12151902f98f099b07f063a018a6c8",
            "auth_type":"cXFjb25u|1501852438|587fb292ca436760260f9a8006a00ff728866723",
            "atoken":"AE030245440FF4CCDB56A733303F6583",
            "atoken_expired_in":"7776000",
            "token":"QUUwMzAyNDU0NDBGRjRDQ0RCNTZBNzMzMzAzRjY1ODM=|1501852438|df6fdabc0eaefc72db1e9b4dfbfb47227bfb80aa",
            "client_id":"N0Q5RjhCNDRGOUI1RDUwQTdBNkIyRTZBNjkwQzkyNDc=|1501852438|2379214c81d4f275ba0db3359a8f6439f5d489cc",
            "z_c0":"Mi4wQUNDQ0VSNXNLd3dBa0FKTXlya1NDeGNBQUFCaEFsVk5KUUNzV1FCajVpeW9Gc0VLZmgzNkZKV01zeGdBbHAydHhB|1501852453|938f57cd161ec8278ca7674c447cffbb659c317e",
            "unlock_ticket":"QUNDQ0VSNXNLd3dYQUFBQVlRSlZUUzE2aEZtUFZMLVJpYzlGWDhZX2lXRklpX19LNDRHMXpRPT0=|1501852453|40afa3ed0a7fb2c025ab5d37ba59262e4b3a1246"
        }

    def doRequestNoProxy(self, urlPath):
        reqUrl = self.url + urlPath
        try:
            get_html = requests.get(reqUrl, cookies=self.cookies,
                                    headers=self.header, verify=False)
        except Exception, e:
            print "requests get error !", e.message
            red.lpush('red_to_spider', self.url)
            return
        txt = get_html.text
        if get_html.status_code == 200:
            if urlPath == "/following":
                self.analy_following_profile(txt)
            elif urlPath == "/followers":
                content = get_html.content
                self.analy_followers_profile(txt,content)
            return
        else:
            red.lpush('red_to_spider', self.url)

    def doRequestProxy(self, urlPath):
        reqUrl = self.url + urlPath
        try:
            get_html = requests.get(reqUrl,
                                    headers=self.header, verify=False, proxies={"http": "http://{}".format(self.proxy)})
        except Exception, e:
            print "requests get error !", e.message
            red.lpush('red_to_spider', self.url)
            delete_proxy(self.proxy)
            return
        txt = get_html.text
        if get_html.status_code == 200:
            if urlPath == "/following":
                self.analy_following_profile(txt)
            elif urlPath == "/followers":
                content = get_html.content
                self.analy_followers_profile(txt,content)
            return
        else:
            red.lpush('red_to_spider', self.url)
            delete_proxy(self.proxy)

    def get_user_followers_data(self):
        if type(self.proxy) == None or self.proxy is None:
            self.doRequestNoProxy("/followers")
        else:
            self.doRequestProxy("/followers")


    def get_user_following_data(self):
        if type(self.proxy) == None or self.proxy is None:
            self.doRequestNoProxy("/following")
        else:
            self.doRequestProxy("/following")

    def get_xpath_source(self,source):
        if len(source) <= 0:
            return 0

        if source:
            return source[0]
        else:
            return ''

    def analy_following_profile(self,html_text):
        tree = html.fromstring(html_text)
        url_list = tree.xpath("//h2[@class='ContentItem-title']//span[@class='UserLink UserItem-name']//a[@class='UserLink-link']/@href")
        for target_url in url_list:
            target_url = "https://www.zhihu.com" + target_url
            target_url = target_url.replace("https", "http")
            if red.sadd('red_had_spider', target_url):
                red.lpush('red_to_spider', target_url)

    def analy_followers_profile(self,html_text,content):
        tree = html.fromstring(html_text)
        self.user_name = self.get_xpath_source(tree.xpath("//span[@class='ProfileHeader-name']/text()"))
        male = tree.xpath("//div[@class='ProfileHeader-iconWrapper']//svg[@class='Icon Icon--male']")
        female = tree.xpath("//div[@class='ProfileHeader-iconWrapper']//svg[@class='Icon Icon--female']")

        if len(male) > 0 or len(female) >0:
            if len(male) > 0:
                self.user_gender = "male"
            if len(female) > 0:
                self.user_gender = "female"
        else:
            self.user_gender = "none"

        self.answers=self.get_xpath_source(tree.xpath("//div[@id='ProfileMain']//li[@aria-controls='Profile-answers']//span[@class='Tabs-meta']/text()"))
        self.asks=self.get_xpath_source(tree.xpath("//div[@id='ProfileMain']//li[@aria-controls='Profile-asks']//span[@class='Tabs-meta']/text()"))
        self.posts=self.get_xpath_source(tree.xpath("//div[@id='ProfileMain']//li[@aria-controls='Profile-posts']//span[@class='Tabs-meta']/text()"))
        self.columns=self.get_xpath_source(tree.xpath("//div[@id='ProfileMain']//li[@aria-controls='Profile-columns']//span[@class='Tabs-meta']/text()"))
        self.pins=self.get_xpath_source(tree.xpath("//div[@id='ProfileMain']//li[@aria-controls='Profile-pins']//span[@class='Tabs-meta']/text()"))
        self.collections=self.get_xpath_source(tree.xpath("//div[@class='Menu']//a[@aria-controls='Profile-collections']//span[@class='Link-meta']/text()"))
        global red
        try:
            self.user_followees = tree.xpath("//div[@class='Card FollowshipCard']//div[@class='NumberBoard-value']")[0].text
            self.user_followers = tree.xpath("//div[@class='Card FollowshipCard']//div[@class='NumberBoard-value']")[1].text
        except BaseException,e:
            print "error...."+self.url
            red.lpush('red_to_spider', self.url)
            return

        '''
        self.user_be_agreed = tree.xpath("//div[@class='Profile-sideColumn']/div[@class='Card']//div[@class='Profile-sideColumnItem']/div[@class='IconGraf']//svg[@class='Icon IconGraf-icon Icon--like']/../../../text()")
        self.user_be_thanked = tree.xpath("//div[@class='Profile-sideColumn']/div[@class='Card']//div[@class='Profile-sideColumnItem']/div[@class='IconGraf']//svg[@class='Icon IconGraf-icon Icon--like']/../../../div[class='Profile-sideColumnItemValue']/text()")
        self.collected =tree.xpath("//div[@class='Profile-sideColumn']/div[@class='Card']//div[@class='Profile-sideColumnItem']/div[@class='IconGraf']//svg[@class='Icon IconGraf-icon Icon--like']/../../../div[class='Profile-sideColumnItemValue']/text()")
        '''
        try:
            self.user_be_agreed = re.search('获得\\s*(\\d+)\\s*次赞同',content).group(1)
        except:
            self.user_be_agreed = 0
        try:
            self.user_be_thanked = re.search('获得 (\\d+) 次感谢',content).group(1)
        except:
            self.user_be_thanked = 0

        try:
            self.collected = re.search('(\\d+) 次收藏',content).group(1)
        except:
            self.collected = 0

        if self.option == "print_data_out":
            self.print_data_out()
        else:
            self.store_data_to_mongo()

        url_list = tree.xpath("//h2[@class='ContentItem-title']//span[@class='UserLink UserItem-name']//a[@class='UserLink-link']/@href")
        for target_url in url_list:
            target_url = "https://www.zhihu.com"+ target_url
            target_url = target_url.replace("https","http")
            if red.sadd('red_had_spider',target_url):
                red.lpush('red_to_spider',target_url)

    def print_data_out(self):
        print "*" * 60
        print '用户名:%s\n' % self.user_name
        print '用户编号:%s\n'% self.number
        print "用户性别:%s\n" % self.user_gender
        print "回答次数:%s\n" % self.answers
        print "提问次数:%s\n" % self.asks
        print "文章数量:%s\n" % self.posts
        print "专栏数量:%s\n" % self.columns
        print "分享次数:%s\n" % self.pins
        print "收藏数量:%s\n" % self.collections
        print "赞同次数:%s\n" % self.user_be_agreed
        print "感谢次数:%s\n" % self.user_be_thanked
        print "被收藏次数:%s\n" % self.collected
        print "被关注:%s\n" % self.user_followers
        print "关注了:%s\n" % self.user_followees
        print "*" * 60

    def store_data_to_mongo(self):
        new_profile = Zhihu_User_Profile(
            user_name=str(self.user_name),
            user_number = str(self.number),
            user_be_agreed=str(self.user_be_agreed),
            user_be_thanked=str(self.user_be_thanked),
            user_followees=str(self.user_followees),
            user_followers=str(self.user_followers),
            answers=str(self.answers),
            asks=str(self.asks),
            posts=str(self.posts),
            columns=str(self.columns),
            pins=str(self.pins),
            collections=str(self.collections),
            user_gender=str(self.user_gender),
            collected=str(self.collected),
            user_url=str(self.url)
        )
        new_profile.save()
        print "saved: %s \n" % self.user_name

def get_proxy():
    return requests.get("http://127.0.0.1:5000/get/").content

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5000/delete/?proxy={}".format(proxy))

def BFS_Search(option,proxyFlag='no'):
    global red
    while True:
        proxy = None
        if proxyFlag == 'proxy':
            proxy = get_proxy()
            if type(proxy) == None:
                print "proxy empty"
                break
            if proxy is None:
                print "proxy empty"
                break
        else:
            time.sleep(4)
        temp = red.rpop('red_to_spider')
        if type(temp) == None or temp is None:
            print "url empty"
            break
        result = Spider(temp,option,proxy)
        result.get_user_followers_data()
        result.get_user_following_data()

    return "ok"


if __name__ == '__main__':
    try:
        option = sys.argv[1]
        proxyFlag = sys.argv[2]
        print "==="+proxyFlag+"==="
    except:
        print 'argv is not accepted'
        sys.exit()
    red = redis.Redis(host='127.0.0.1',port=6379,db=1)
    red.lpush('red_to_spider',"https://www.zhihu.com/people/tian-yuan-dong")
    #option = "print_data_out"
    #option = "db"
    BFS_Search(option,proxyFlag)

    '''
    res = []
    process_pool = Pool(4)
    for i in range(4):
        res.append(process_pool.apply_async(BFS_Search,(option,)))
    
    process_pool.close()
    process_pool.join()
    for num in res:
        print ":::", num.get()
    print 'Work had done!'
    '''
