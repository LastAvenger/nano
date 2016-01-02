#!/usr/bin/python
# -*- encoding: UTF-8 -*-

import sys
import getopt
import json
import discuz


def usage():
    print('''\
nano is a bot used to catch&post Discuz BBS message

Usage: nano.py [option] ...
options:
    -f, --fid       get and display content of thread specified by fid
    -o, --output    save output to file
    -f, --help      show this help message and exit

Acting on Discuz! X3.2
Create by Yuexuan Gu <lastavengers@outlook.com>''')


def main():
    config = './config.json'
    url = 'http://hometown.scau.edu.cn/'

    print('[nano]', 'url:', url)
    print('[nano]', 'config file:', config)
    try:
        with open(config) as f:
            usr = json.loads(f.read())
    except Exception as err:
        print('[nano]', '{err}', err)

    thread = None
    try:
        opts, _ = getopt.getopt(sys.argv[1:], 'f:o:h', ['fid=', 'output=','help'])
        for o, a in opts:
            if o in ('-f', '--fid'):
                hmt = discuz.Discuz(url)
                hmt.login(usr)
                thread = hmt.get_thread(a)
            elif o in ('-h', '--help'):
                usage()
            elif o in ('-o', '--output'):
                if thread:
                    try:
                        with open(a, 'w') as f:
                            f.write(thread.to_json())
                    except:
                        raise
                    print('[nano]', 'save output to', a)
                else:
                    raise Exception('options -f is required before -o')
        if not opts:
            usage()
    except Exception as err:
        print('[nano]', '{err}', err)
        sys.exit(-1)


if __name__ == '__main__':
    main()
