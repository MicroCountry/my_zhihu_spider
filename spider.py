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
from mongodbs import Zhihu_User_Profile

from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Spider():
    def __init__(self,url,option="print_data_out"):
        self.url = url
        try:
            self.number =re.search("([\w|-]+)$",url).group(1)
        except:
            self.number=''
        self.option = option
        self.header = {}
        self.header["User-Agent"] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0"
        self.cookies = {
            "q_c1": "=fa7be38aa96544b1ac3d3fb6c1538971|1499914412000|1483015223000",
            "d_c0": "AJACTMq5EguPTkQ_iRg2bEN8SRcDRt-r35E=|1483015224",
            "__utma": "51854390.897571603.1501758969.1501758969.1501758969.1",
            "__utmz": "51854390.1501758969.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
            "_zap": "f4737b72-343c-40ad-9c98-37509a9bfedd",
            "q_c1": "fa7be38aa96544b1ac3d3fb6c1538971|1499914412000|1483015223000",
            "r_cap_id": "Y2UyZDM2NmZmYzQ5NDRhNDg4M2VmODE2M2QyYmY2OWI=|1501736351|502679beb3e669a2d29759cc0649a267d4b35f76",
            "cap_id": "ZjY4YWRlMzA0NGVlNDkyMDgxY2FkYTk2NjMyNjhkNDU=|1501736351|8a8b387193ecbf73eaf067e9b08efa17684cc4ad",
            "z_c0": "Mi4wQUJBTXY0bEZtd2dBa0FKTXlya1NDeGNBQUFCaEFsVk5wenFxV1FBVmxBZ1NNRktFcTRCWnZ2Yk9ESUdZM25BaGV3|1501736359|af0689b40970ddce49f7779e21229e611831b44e",
            "__utmv": "51854390.100-1|2=registration_date=20150827=1^3=entry_date=20150827=1"
        }

    def get_user_data(self):
        followee_url = self.url + "/followers"
        try:
            get_html = requests.get(followee_url,cookies=self.cookies,
                                    headers=self.header,verify=False)
        except:
            print "requests get error !"
            return
        txt = get_html.text
        content = get_html.content
        if get_html.status_code == 200:
            self.analy_profile(txt,content)
            return

    def get_xpath_source(self,source):
        if len(source) <= 0:
            return 0

        if source:
            return source[0]
        else:
            return ''

    def analy_profile(self,html_text,content):
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

        try:
            self.user_followees = tree.xpath("//div[@class='Card FollowshipCard']//div[@class='NumberBoard-value']")[0].text
            self.user_followers = tree.xpath("//div[@class='Card FollowshipCard']//div[@class='NumberBoard-value']")[1].text
        except BaseException,e:
            print "error...."
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
        global red
        url_list = tree.xpath("//h2[@class='ContentItem-title']//a[@class='UserLink-link']/@href")
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
            user_name=self.user_name,
            user_number = self.number,
            user_be_agreed=self.user_be_agreed,
            user_be_thanked=self.user_be_thanked,
            user_followees=self.user_followees,
            user_followers=self.user_followers,
            answers=self.answers,
            asks=self.asks,
            posts=self.posts,
            columns=self.columns,
            pins=self.pins,
            collections=self.collections,
            user_gender=self.user_gender,
            collected=self.collected,
            user_url=self.url
        )
        new_profile.save()
        print "saved: %s \n" % self.user_name

def BFS_Search(option):
    global red
    while True:
        temp = red.rpop('red_to_spider')
        if type(temp) == None:
            print "empty"
            break
        if temp is None:
            print "empty"
            break
        result = Spider(temp,option)
        result.get_user_data()
    return "ok"


if __name__ == '__main__':
    try:
        option = sys.argv[1]
    except:
        print 'argv is not accepted'
        sys.exit()
    red = redis.Redis(host='127.0.0.1',port=6379,db=1)
    red.lpush('red_to_spider',"https://www.zhihu.com/people/tian-yuan-dong")
    #option = "print_data_out"
    #option = "db"
    BFS_Search(option)

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