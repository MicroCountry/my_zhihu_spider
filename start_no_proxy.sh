#!/bin/bash
nohup python -u spider.py db no> spider_no_proxy.log 2>&1 &
