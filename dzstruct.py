# -*- encoding: UTF-8 -*-

import json

class Post():
    pid = ''
    uid = ''
    author = ''
    time = ''
    title = ''
    message = ''

    def __init__(self, pid, uid, author, time, message, title = ''): 
        self.uid = uid
        self.pid = pid
        self.author = author
        self.time = time
        self.title = title
        self.message = message

class Thread():
    tid = ''
    fid = ''
    title = ''
    nposts = 0
    posts = []

    def __init__(self, tid, fid, title, nreplies): 
        self.tid = tid;
        self.fid = fid;
        self.title = title
        self.nposts = nreplies;

    def to_text(self):
        print('TID:', self.tid, 'FID:', self.fid, '作者:', self.posts[0].author, '发表时间:', self.posts[0].time)
        print('标题:', self.title)
        print('回复数:', self.nposts)
        print('---------- Message ----------')
        print(self.posts[0].message)

        for p in self.posts[1:]:
            print('-----------------------------')
            print(p.author, '发表于', p.time)
            print(p.message)

        print('----------   End   ----------')

    def to_json(self):
        thdict = {  'tid': self.tid,
                    'fid': self.fid,
                    'title': self.title,
                    'npost': self.nposts,
                    'posts': {}
                    }
        i = 0
        for p in self.posts:
            podict = {  'pid': p.pid,
                        'uid': p.uid,
                        'author': p.author,
                        'time': p.time,
                        'title': p.title,
                        'message': p.message
                        }
            thdict['posts'][i] = podict
            i = i + 1
        thjson = json.dumps(thdict, sort_keys = True,
                            indent = 4,
                            separators = (',', ': '),
                            ensure_ascii = False
                            )
        return thjson
