import re
import json
import requests

from dzstruct import Post
from dzstruct import Thread
from bs4 import BeautifulSoup

class Discuz():
    s = ''
    url = ''
    fid = {}        # 版块名称 和 ID 的映射
    dzconfig = ''   # post & reply param
    logined = False
        
    def __init__(self, url):
        self.url = url
        self.s = requests.session()
        self.logined = False

        f= open('./dzconfig.json')
        self.dzconfig = json.loads(f.read())
        f.close()


    def get_fid(self):
        fid_pattern = re.compile(r'<dt><a href="forum\.php\?mod=forumdisplay&fid=([0-9]+)">(?u)(.+)</a>')
        response = self.s.get(self.url + 'bbs/')
        t = fid_pattern.findall(response.text)
        if t:
            self.fid = dict((fname, fid) for fid, fname in t)
            print('[get_fid]', '{successed}')
        else:
            print('[get_fid]', '{unknown error}')


    def get_formhash(self, url):
        formhash_pattern = re.compile('formhash=([0-9a-zA-Z]+)')
        response = self.s.get(url)
        formhash_info = formhash_pattern.search(response.text) 
        if formhash_info:
            return formhash_info.group(1)
        else:
            return None


    def login(self, usr):
        action = 'bbs/member.php?mod=logging&action=login&loginsubmit=yes'
        succ_pattern = re.compile(r"\('succeedlocation'\)\.innerHTML = '(?u)(.+)，现在将转入登录前页面';")
        fail_pattern = re.compile(r'<div id="messagetext" class="alert_error">\n<p>(?u)(.+)</p>')

        arg = self.dzconfig['login']
        arg['username'] = usr['username'].encode('gb2312')
        arg['password'] = usr['password'].encode('gb2312')

        response = self.s.post(self.url + action, data = arg)
        succ_info = succ_pattern.search(response.text)
        fail_info = fail_pattern.search(response.text)

        if succ_info:
            print('[login]','{successed}', succ_info.group(1))
            self.get_fid()
            print(self.fid)
            self.logined = True
        elif fail_info:
            print('[login]', '{failed}', fail_info.group(1))
            self.logined = False
        else:
            print('[login]', '{unknown error}')
            self.logined = False
        return self.logined

    def post(self, fname, subject, message):
        if not self.logined: 
            print('[post]', 'not logged in')
            return False

        tid = None
        fail_pattern = re.compile('<div id="messagetext" class="alert_error">\n<p>(?u)(.+)</p>')
        succ_pattern = re.compile('tid=([0-9]+)')
        action = 'bbs/forum.php?mod=post&action=newthread&fid=FID&topicsubmit=yes'.replace('FID', self.fid[fname])
        fake = 'bbs/forum.php?mod=post&action=newthread&fid=FID'.replace('FID', self.fid[fname])

        arg = self.dzconfig['post']
        arg['formhash'] = self.get_formhash(self.url + fake)
        arg['message'] = message.encode('gb2312')
        arg['subject'] = subject.encode('gb2312')

        print('[post]', 'fname:', fname, 'subject:', subject)
        print('[post]', 'message:', message)

        response = self.s.post(self.url + action, data = arg)
        fail_info = fail_pattern.search(response.text)
        succ_info = succ_pattern.search(response.url)

        if fail_info:
            print('[post]', '{failed}', fail_info.group(1))
        elif succ_info:
            tid = succ_info.group(1)
            print('[post]', '{successed} tid:', succ_info.group(1))
        else:
            print('[post]', '{unknown error}')
        return tid


    def reply(self, tid, message):
        if not self.logined: 
            print('[post]', 'not logged in')
            return False

        action = '/bbs/forum.php?mod=post&action=reply&tid=TID&replysubmit=yes'.replace('TID', tid)
        fake = '/bbs/forum.php?mod=viewthread&tid=865411'
        fail_pattern = re.compile("errorhandle_fastpost\('(?u)(.+?)'")
        succ_pattern = re.compile('pid=([0-9]+)')
        # TODO 这里并不能匹配到最后一次发表的 PID

        arg = self.dzconfig['post']
        arg['formhash'] = self.get_formhash(self.url + fake)
        arg['message'] = message.encode('gb2312')

        response = self.s.post(self.url + action, data = arg)
        fail_info = fail_pattern.search(response.text)
        succ_info = succ_pattern.search(response.text)

        if fail_info:
            print('[reply]', '{failed}', fail_info.group(1))
        elif succ_info:
            print('[reply]', '{successed} pid:', succ_info.group(1))
        else:
            print('[reply]', '{unknown error}')


    def get_post(self, thread, page):
        action = 'bbs/forum.php?mod=viewthread&tid=TID&page=PAGE'.replace('TID', thread.tid).replace('PAGE', str(page))

        response = self.s.get(self.url + action)
        html = BeautifulSoup(response.text, 'html.parser')

        fail_info = html.find(id = 'messagetext', class_ = 'alert_error')
        posts = html.find_all('div', id = re.compile(r'post_[0-9]+'))

        idx = len(thread.posts)

        if posts:
            for post in posts:
                idx = idx + 1

                author = post.find('a', class_='xw1')
                if author:
                    author = author.get_text()
                    uid = re.search(r'uid=([0-9]+)', post.find('a', class_='xw1')['href']).group(1)
                else:
                    author = 'anonymous'
                    uid = '0'

                pid = re.search(r'post_([0-9]+)', post['id']).group(1)

                time = post.find('em', id = re.compile(r'authorposton[0-9]+'))
                if time.span:
                    # <em id="authorposton6700972">发表于 <span title="2015-12-17 11:31:03">1 小时前</span></em>
                    time = time.span['title']
                else:
                    # <em id="authorposton6619277">发表于 2015-9-21 08:47:50</em>
                    time = time.string[4:]

                lock_info = post.find('div', class_ = 'locked')
                if (lock_info):
                    print('[get_post]', '{warning}', 'page:', page, 'idx:', idx, 'post locked')
                    message = '作者被禁止或删除 内容自动屏蔽'
                else:
                    post.find('div', class_ = 'a_pr').decompose()   # 删除 分享栏
                    message = post.find('td', id = re.compile(r'postmessage_[0-9]+')).get_text()
                    # print(idx, end = ' ')

                thread.posts.append(Post(pid, uid, author, time, message))

            # print('')
            print('[get_post]', '{successed}', 'page:', page, 'posts_num:', len(posts))
            return True
        elif fail_info:
            print('[get_post]', '{failed}', 'page:', page, fail_info.p.get_text())
        else:
            print('[get_post]', '{unknown error}', 'page:', page)

        return False


    def get_thread(self, tid):
        action = 'bbs/forum.php?mod=viewthread&tid=TID'.replace('TID', tid)

        response = self.s.get(self.url + action)
        html = BeautifulSoup(response.text, 'html.parser')
        # html = BeautifulSoup(open('./test.html').read(), 'html.parser')

        fail_info = html.find(id = 'messagetext', class_ = 'alert_error')
        if fail_info:
            print('[get_thread]', '{failed}', fail_info.p.get_text())
            return None

        title = html.find('span', id = 'thread_subject').string
        f_tag = html.find('a', href = re.compile(r'^forum.php\?mod=forumdisplay&fid=[0-9]+'))
        fid = re.search(r'fid=([0-9]+)', f_tag['href']).group(1)
        npages = int(html.find('span', title = re.compile('共 [0-9]+ 页'))['title'][2:-2])

        thread = Thread(tid, fid, title, 0)
        for p in range(1, npages):
            if not self.get_post(thread, p):
                print('[get_thread]', '{aborted}')
                return None

        thread.nposts = len(thread.posts) - 1;

        print('[get_thread]', '{successed}', 'title:', thread.title, 'reply_num:', thread.nposts)

        thread.disp()

        return thread
        
