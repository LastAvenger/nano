#!/usr/bin/python
# -*- encoding: UTF-8 -*-

import re
import json
import urllib
import requests;

url = 'http://hometown.scau.edu.cn/'

fid = {
        "海洋馆": "7",
        "IT数码": "10",
        "论坛测试区": "41",
        "论坛站务": "39"
        }

s = requests.session()

def get_formhash(session, url):
    formhash_pattern = re.compile('formhash=([0-9a-zA-Z]+)')
    response = session.get(url)
    formhash_info = formhash_pattern.search(response.text) 
    if formhash_info:
        return formhash_info.group(1)
    else:
        return None

def login():
    login_action = 'bbs/member.php?mod=logging&action=login&loginsubmit=yes'
    login_succ_pattern = re.compile("\('succeedlocation'\).innerHTML = '(?u)(.+)，现在将转入登录前页面';")
    login_fail_pattern = re.compile('<div id="messagetext" class="alert_error">\n<p>(?u)(.+)</p>')

    f = open('./config.json', 'r')
    account = json.loads(f.read())
    f.close()
    account['username'] = account['username'].encode('gb2312')

    login_response = s.post(url + login_action, data = account)
    login_succ_info = login_succ_pattern.search(login_response.text)
    login_fail_info = login_fail_pattern.search(login_response.text)

    if login_succ_info:
        print('[login]','successed', login_succ_info.group(1))
    elif login_fail_info:
        print('[login]', 'failed', login_fail_info.group(1))
    else:
        print('[login]', 'unknown error')
    

def post(fid, title, content):
    print('[post]', 'fid:', fid, 'title:', title)
    print('[post]', 'content:', content)

    post_fail_pattern = re.compile('<div id="messagetext" class="alert_error">\n<p>(?u)(.+)</p>')
    post_succes_pattern = re.compile('tid=([0-9]+)')

    post_action = 'bbs/forum.php?mod=post&action=newthread&fid=FID&extra=&topicsubmit=yes'.replace('FID', fid)
    post_fake = 'bbs/forum.php?mod=post&action=newthread&fid=FID'.replace('FID', fid)

    f = open('./newpost.json', 'r')
    post_cotent = json.loads(f.read())
    f.close()

    post_cotent['subject'] = title.encode('gb2312')
    post_cotent['message'] = content.encode('gb2312')
    post_cotent['formhash'] = get_formhash(s, url + post_fake)

    post_response = s.post(url + post_action, data = post_cotent)
    post_fail_info = post_fail_pattern.search(post_response.text)
    post_succ_info = post_succes_pattern.search(post_response.url)

    if post_fail_info:
        print('[post]', 'failed', post_fail_info.group(1))
    elif post_succ_info:
        print('[post]', 'successed tid:', post_succ_info.group(1))
    else:
        print('[post]', 'unknown error')

def relply(tid, msg):
    relply_action = '/bbs/forum.php?mod=post&action=reply&tid=TID&extra=&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1'.replace('TID', tid)
    reply_fake = '/bbs/forum.php?mod=viewthread&tid=865411'
    reply_fail_pattern = re.compile("errorhandle_fastpost\('(?u)(.+?)'")
    reply_succ_pattern = re.compile('pid=([0-9]+)')

    reply_content = {
            'message': msg.encode('gb2312'),
            'formhash': get_formhash(s, url + reply_fake)
            }

    reply_response = s.post(url + relply_action, data = reply_content)
    reply_fail_info = reply_fail_pattern.search(reply_response.text)
    reply_succ_info = reply_succ_pattern.search(reply_response.text)

    if reply_fail_info:
        print('[reply]', 'failed', reply_fail_info.group(1))
    elif reply_succ_info:
        print('[reply]', 'successed pid:', reply_succ_info.group(1))
    else:
        print('[reply]', 'unknown error')

def main():
    login()
    # post(fid['论坛测试区'], '测试', '测试一下，稍后删除')
    relply('865562', '回复测试测试测试')

if __name__ == '__main__':
    main()
