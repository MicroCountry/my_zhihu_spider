#!/bin/bash
nohup python -u spider.py db proxy> spider_proxy.log 2>&1 &
