#~/usr/bin/python
# -*- encoding: UTF-8 -*-

import re
import json
import urllib
import requests;

url = 'http://hometown.scau.edu.cn/bbs/'

def login():
    login_arg = 'member.php?mod=logging&action=login&loginsubmit=yes'

    f = open('./config.json', 'r')
    account = json.loads(f.read())
    account['username'] = account['username'].encode('gb2312')
    f.close()

    s = requests.session()
    s.post(url + login_arg, data = account)
    r = s.get('http://hometown.scau.edu.cn/bbs/forum.php')

    m = re.search('(?<=<strong class="vwmy">).*', r.text)
    uid = re.search('(?<=uid\=)\d+', m.group(0)).group(0)
    username =re.search('(?<=>).*?(?=<)', m.group(0)).group(0)

    print('[uid]:', uid)
    print('[username]:', username)
    
    return s

def main():
    s = login()

if __name__ == '__main__':
    main()
