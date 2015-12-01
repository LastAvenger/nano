import re
import json
import requests
import dzstruct

class Discuz():
    url = ''
    s = ''
    logined = False
    dzconfig = ''    # post & reply param
        
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
        self.fid = fid_pattern.findall(response.text)
        if self.fid:
            for i in self.fid: i = lambda x: (x[1], x[0])
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
        action = 'bbs/forum.php?mod=post&action=newthread&fid=FID&extra=&topicsubmit=yes'.replace('FID', self.fid[fname])
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

    def reply(self, id, message):
        if not self.logined: 
            print('[post]', 'not logged in')
            return False

        action = '/bbs/forum.php?mod=post&action=reply&tid=TID&extra=&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1'.replace('TID', tid)
        fake = '/bbs/forum.php?mod=viewthread&tid=865411'
        fail_pattern = re.compile("errorhandle_fastpost\('(?u)(.+?)'")
        succ_pattern = re.compile('pid=([0-9]+)')

        arg['formhash'] = self.get_formhash(url + fake)
        arg['message'] = message.encode('gb2312')

        response = s.post(self.url + action, data = arg)
        fail_info = fail_pattern.search(response.text)
        succ_info = succ_pattern.search(response.text)

        if fail_info:
            print('[reply]', '{failed}', fail_info.group(1))
        elif succ_info:
            print('[reply]', '{successed} pid:', succ_info.group(1))
        else:
            print('[reply]', '{unknown error}')

    def get_post(self, tid):
        action = 'bbs/forum.php?mod=viewthread&action=printable&tid=TID'.replace('TID', tid)

        fail_pattern = re.compile('<div id="messagetext" class="alert_error">\n<p>(?u)(.+)</p>')
        post_pattern = re.compile(
          r'<b>作者: </b>(?u)(.+)&nbsp; &nbsp; <b>时间: </b>(.+)<br />\n<b>标题: </b>(?u)(.+)<br />((.|\n)*?)<hr noshade size="2" width="100%" color="(#808080|BORDERCOLOR)">')
        reply_pattern = re.compile(
          r'<b>作者: </b>(?u)(.+)&nbsp; &nbsp; <b>时间: </b>(.+)<br />\n(?u)((.|\n)*?)<hr noshade size="2" width="100%" color="(#808080|BORDERCOLOR)">')

        response = self.s.get(self.url + action)
        text = response.text.replace('\r', '')

        fail_info = fail_pattern.search(text)
        post_info = post_pattern.search(text)
        reply_info = reply_pattern.findall(text)

        if post_info:
            print('[get_post]', '{successed}')

            post = dzstruct.Post()
            post.tid = tid
            post.author = post_info.group(1)
            post.time = post_info.group(2)
            post.subject = post_info.group(3)
            post.message = post_info.group(4)
            post.num_replies = len(reply_info)

            if reply_info:
                for i in reply_info:
                    post.replies.append(dzstruct.Reply(i[0], i[1], i[2]))
            post.display(display_relpy = True, pure = True)
        elif fail_info:
            print('[get_post]', '{failed}', fail_info.group(1))
        else:
            print('[get_post]', '{unknown error}')
        return None
        
