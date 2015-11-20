import re
import requests

class Discuz():
    fid = {
            "海洋馆": "7",
            "IT数码": "10",
            "论坛测试区": "41",
            "论坛站务": "39"
            }

    def __init__(self, url):
        self.url = url
        self.s = requests.session()
        self.logined = False

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
        succ_pattern = re.compile(r"\('succeedlocation'\).innerHTML = '(?u)(.+)，现在将转入登录前页面';")
        fail_pattern = re.compile(r'<div id="messagetext" class="alert_error">\n<p>(?u)(.+)</p>')

        response = self.s.post(self.url + action, data = usr)
        succ_info = succ_pattern.search(response.text)
        fail_info = fail_pattern.search(response.text)

        if succ_info:
            print('[login]','{successed}', succ_info.group(1))
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
        arg = {
                "allownoticeauthor": "0",
                "checkbox": "0",
                "creditlimit": "",
                "cronpublishdate": "",
                "formhash": self.get_formhash(self.url + fake),
                "message": message.encode('gb2312'),
                "newalbum": "",
                "posttime": "",
                "price": "",
                "readperm": "",
                "replycredit_extcredits": "0",
                "replycredit_membertimes": "1",
                "replycredit_random": "100",
                "replycredit_times": "1",
                "replylimit": "",
                "rewardfloor": "",
                "rushreplyfrom": "",
                "rushreplyto": "",
                "save": "",
                "stopfloor": "",
                "subject": subject.encode('gb2312'),
                "tags": "",
                "uploadalbum": "117",
                "usesig": "1",
                "wysiwyg" : "0"
                }

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

        arg = {
                'message': msg.encode('gb2312'),
                'formhash': self.get_formhash(url + fake)
                }

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
        subject_pattern = re.compile('<b>标题: </b>(.+?)<b>')
        # message_pattern = re.compile(r'(<hr noshade size="2" width="100%" color="#808080">)((.|\n)*?)\1')

        response = self.s.get(self.url + action)
        title = subject_pattern.search(response.text)
        # message = message_pattern.search(response.text)

        print('[get_post]', 'tid:', tid)
        print('[get_post]', 'subject:', title.group(1))
        # print('[get_post]', 'message', message.group(2))

