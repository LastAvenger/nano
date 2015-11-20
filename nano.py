#!/usr/bin/python
# -*- encoding: UTF-8 -*-

import json
import discuz

url = 'http://hometown.scau.edu.cn/'

def main():
    f = open('./config.json')
    usr = json.loads(f.read())
    f.close()

    hmt = discuz.Discuz(url)
    hmt.login(usr)
    tid = hmt.post('论坛测试区', '又来测试了', '这是正文')
    hmt.get_post(tid)

if __name__ == '__main__':
    main()
