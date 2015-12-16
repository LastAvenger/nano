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

    def disp(self):
        print('TID:', self.tid, 'FID', self.fid, 'Author:', self.posts[0].author, 'Time:', self.posts[0].time)
        print('Title:', self.title)
        print('Replies number:', self.nposts)
        print('---------- Message ----------')
        print(self.posts[0].message)

        for p in self.posts[1:]:
            print('-----------------------------')
            print(p.author, '发表于', p.time)
            print(p.message)

        print('----------   End   ----------')
