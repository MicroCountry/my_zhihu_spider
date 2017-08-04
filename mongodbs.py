#!/usr/bin/env python
#coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import mongoengine

mongoengine.connect('my_zhihu_data')

class Zhihu_User_Profile(mongoengine.Document):
    user_name = mongoengine.StringField()
    user_number = mongoengine.StringField()
    user_be_agreed = mongoengine.StringField()
    user_be_thanked = mongoengine.StringField()
    user_followees = mongoengine.StringField()
    user_followers = mongoengine.StringField()
    user_gender = mongoengine.StringField()
    user_url = mongoengine.StringField()
    answers = mongoengine.StringField()
    asks = mongoengine.StringField()
    posts = mongoengine.StringField()
    columns = mongoengine.StringField()
    pins = mongoengine.StringField()
    collections = mongoengine.StringField()
    collected= mongoengine.StringField()