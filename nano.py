#!/usr/bin/python
# -*- encoding: UTF-8 -*-

import re
import json
import urllib
import requests;

url = 'http://hometown.scau.edu.cn/'
action_login = 'bbs/member.php?mod=logging&action=login&loginsubmit=yes'
formhash = ''

fid = {
        "海洋馆": "7",
        "IT数码": "10",
        "论坛测试区": "41",
        "论坛站务": "39"
        }

s = requests.session()

def login():
    global s

    login_succ_pattern = re.compile("\('succeedlocation'\).innerHTML = '(?u)(.+)，现在将转入登录前页面';")
    login_fail_pattern = re.compile('<div id="messagetext" class="alert_error">\n<p>(?u)(.+)</p>')

    f = open('./config.json', 'r')
    account = json.loads(f.read())
    f.close()
    account['username'] = account['username'].encode('gb2312')

    login_response = s.post(url + action_login, data = account)
    login_succ_info = login_succ_pattern.search(login_response.text)
    login_fail_info = login_fail_pattern.search(login_response.text)

    if login_succ_info:
        print('[login]','successed', login_succ_info.group(1))
    elif login_fail_info:
        print('[login]', 'Failed', login_fail_info.group(1))

    

    # m = re.search('(?<=<strong class="vwmy">).*', r.text)
    # formhash = re.search('(?<=', r.text).group(0)
    # uid = re.search('(?<=uid\=)\d+', m.group(0)).group(0)
    # username =re.search('(?<=>).*?(?=<)', m.group(0)).group(0)

    # print('[uid]:', uid)
    # print('[username]:', username)
    # print('[formhash]:', formhash)


def post(fid, title, content):
    print('[post]', 'fid:', fid)
    print('[post]', 'title:', title)
    print('[post]', 'content:', content)

    global s
    post_formhash_pattern = re.compile('formhash=([0-9a-zA-Z]+)')
    post_fail_pattern = re.compile('<div id="messagetext" class="alert_error">\n<p>(?u)(.+)</p>')

    post_action = 'bbs/forum.php?mod=post&action=newthread&fid=FID&extra=&topicsubmit=yes'.replace('TID', fid)
    post_fake = 'bbs/forum.php?mod=post&action=newthread&fid=FID'.replace('TID', fid)

    post_fake_response = s.get(url + post_fake)
    post_formhash = post_formhash_pattern.search(post_fake_response.text).group(1)

    f = open('./newpost.json', 'r')
    post_cotent = json.loads(f.read())
    f.close()

    post_cotent['subject'] = title.encode('gb2312')
    post_cotent['message'] = content.encode('gb2312')
    post_cotent['formhash'] = post_formhash

    post_response = s.post(url + post_action, data = post_cotent)
    post_fail_info = post_fail_pattern.search(post_response.text)
    if post_fail_info:
        print('[post]', 'failed', post_fail_info.group(1))
    else:
        print('[post]', 'successed', post_response.url)

def main():
    login()
    post(fid['海洋馆'], '测试', '测试一下，稍后删除')

if __name__ == '__main__':
    main()
