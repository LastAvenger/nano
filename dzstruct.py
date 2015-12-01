import re

class Reply():
    author = ''
    time = ''
    message = ''
    uid = ''

    def __init__(self, author, time, message, uid = ''): 
        self.author = author
        self.time = time
        self.message = message
        self.uid = uid

class Post():
    tid = ''
    author = ''
    time = ''
    subject = ''
    message = ''
    replies = []
    num_replies = 0

    def __init__(self): 
        pass

    def display(self, display_relpy = False, pure = False):
        print('TID:', self.tid, 'Author:', self.author, 'Time:', self.time)
        print('Subject:', self.subject)
        print('Replies number:', self.num_replies)
        print('---------- Message ----------')
        if pure:
            dr = re.compile(r'<[^>]+>', re.S)
            print(dr.sub('', self.message))
        else:
            print(self.message)

        if display_relpy:
            for r in self.replies:
                print('-----------------------------')
                print(r.author, 'reply at', r.time)
                if pure:
                    print(dr.sub('', r.message))
                else:
                    print(r.message)

        print('----------   End   ----------')
