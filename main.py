import sys

from main_ui import Ui_MainWindow
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtTest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import requests
from bs4 import BeautifulSoup
import webbrowser

import json

import time

###設定區###

_zg_get_problem_url="https://zerojudge.tw/ShowProblem?problemid="

_zg_submit_url="https://zerojudge.tw/Solution.api"

_zg_result_url="https://zerojudge.tw/Submissions?account="

_zg_judgement_url="https://zerojudge.tw/Solution.json?data=ServerOutputs&solutionid="

_problem_id_1ist=["a001","a004","a005","a006"]

_username=""

_cookie=""

###設定區結束###

def setup():
    _problem_id_1ist[0]=input('輸入第一題題號(EX. a001):')
    _problem_id_1ist[1]=input('輸入第二題題號(EX. a001):')
    _problem_id_1ist[2]=input('輸入第三題題號(EX. a001):')
    _problem_id_1ist[3]=input('輸入第四題題號(EX. a001):')
    print('請在稍後彈出的瀏覽器登入您的zerojudge帳號')
    time.sleep(1)
    login()

def login():
    opts = Options()
    opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0")
    try:
        browser = webdriver.Chrome("./chromedriver.exe",options=opts)
        print("Windows")
    except:
        try:
            browser = webdriver.Firefox(executable_path="./geckodriver")#",chrome_options=opts)
            print("Linux")
        except:
            browser = webdriver.Chrome("./chromedriver_mac",chrome_options=opts)
            print("Mac")
    browser.get("https://zerojudge.tw/Login")
    while not browser.current_url in ["https://zerojudge.tw/#", "https://zerojudge.tw/"]:
        stat='wait'
    browser.get("https://zerojudge.tw/UserStatistic")
    global _cookie
    _cookie = browser.get_cookies()[0]['value']
    global _username
    _username = browser.find_elements_by_tag_name('a')[14].get_attribute('title')
    browser.close()

def fn_pop_problem(__problem_id):
    webbrowser.open_new(_zg_get_problem_url+__problem_id)

def fn_submit_problem(__problem_id,__code):
    __header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0'
    ,'Accept': '*/*'
    ,'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3'
    ,'Accept-Encoding': 'gzip, deflate'
    ,'Referer': 'https://zerojudge.tw/ShowProblem?problemid=a001'
    ,'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    ,'X-Requested-With': 'XMLHttpRequest'
    ,'Connection': 'close'
    ,'Cookie': 'JSESSIONID='+_cookie
    }
    __data={'action':'SubmitCode','language':'CPP','code':__code,'contestid':'0','problemid':__problem_id}
    requests.post(_zg_submit_url,headers=__header,cookies={'JSESSIONID':_cookie},data=__data)

def fn_get_result(__problem_id):
    __result=requests.get(_zg_result_url+_username,cookies={'JSESSIONID':_cookie})
    __soup = BeautifulSoup(__result.text, "lxml")
    __judges=__soup.find_all(width="38%")
    __judge_num=0
    for i in __judges:
        if(i.text.find(__problem_id)>=0):
            break
        __judge_num+=1
    __judge_id=__soup.find_all(id="solutionid")[__judge_num*3].text
    __result=requests.get(_zg_judgement_url+__judge_id,cookies={'JSESSIONID':_cookie})
    __out=str()
    __num=int(1)
    for i in json.loads(__result.text):    
        __out=__out+'第'+str(__num)+'組測資('+str(i['score'])+'分)     '+str(i['judgement'])+' '+str(i['summary'])+' '+str(i['hint'])+'\n'
        __num+=1
    return __out

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("APCS實作題")

        #按鈕->看題目
        self.view_problem_1.clicked.connect(self.fn_view_problem_1)
        self.view_problem_2.clicked.connect(self.fn_view_problem_2)
        self.view_problem_3.clicked.connect(self.fn_view_problem_3)
        self.view_problem_4.clicked.connect(self.fn_view_problem_4)
        
        #按鈕->選檔案
        self.choose_file_1.clicked.connect(self.fn_choose_file_1)
        self.choose_file_2.clicked.connect(self.fn_choose_file_2)
        self.choose_file_3.clicked.connect(self.fn_choose_file_3)
        self.choose_file_4.clicked.connect(self.fn_choose_file_4)

    def fn_view_problem_1(self):
        fn_pop_problem(_problem_id_1ist[0])
    def fn_view_problem_2(self):
        fn_pop_problem(_problem_id_1ist[1])
    def fn_view_problem_3(self):
        fn_pop_problem(_problem_id_1ist[2])
    def fn_view_problem_4(self):
        fn_pop_problem(_problem_id_1ist[3])

    def fn_choose_file_1(self):
        _file_1 = QFileDialog.getOpenFileName(self,"開啟檔案","/","C++ files(*.cpp)")
        self.file_dir_1.setPlainText(_file_1[0].split("/")[-1])
        try:
            self.view_program_1.setPlainText(open(_file_1[0], mode='r').read())
            fn_submit_problem(_problem_id_1ist[0],open(_file_1[0], mode='r').read())
            self.result_1.setPlainText('等待評分結果...')
            for i in range(0,30,1):
                QtTest.QTest.qWait(2000)
                _recv=fn_get_result(_problem_id_1ist[0])
                if(_recv!=''):
                    self.result_1.setPlainText(_recv)
        except:
            print('upload file error')
    def fn_choose_file_2(self):
        _file_2 = QFileDialog.getOpenFileName(self,"開啟檔案","/","C++ files(*.cpp)")
        self.file_dir_2.setPlainText(_file_2[0].split("/")[-1])
        try:
            self.view_program_2.setPlainText(open(_file_2[0], mode='r').read())
            fn_submit_problem(_problem_id_1ist[1],open(_file_2[0], mode='r').read())
            self.result_2.setPlainText('等待評分結果...')
            for i in range(0,30,1):
                QtTest.QTest.qWait(2000)
                _recv=fn_get_result(_problem_id_1ist[1])
                if(_recv!=''):
                    self.result_2.setPlainText(_recv)
        except:
            print('upload file error')    
    def fn_choose_file_3(self):
        _file_3 = QFileDialog.getOpenFileName(self,"開啟檔案","/","C++ files(*.cpp)")
        self.file_dir_3.setPlainText(_file_3[0].split("/")[-1])
        try:
            self.view_program_3.setPlainText(open(_file_3[0], mode='r').read())
            fn_submit_problem(_problem_id_1ist[2],open(_file_3[0], mode='r').read())
            self.result_3.setPlainText('等待評分結果...')
            for i in range(0,30,1):
                QtTest.QTest.qWait(2000)
                _recv=fn_get_result(_problem_id_1ist[2])
                if(_recv!=''):
                    self.result_3.setPlainText(_recv)
        except:
            print('upload file error')  
    def fn_choose_file_4(self):
        _file_4 = QFileDialog.getOpenFileName(self,"開啟檔案","/","C++ files(*.cpp)")
        self.file_dir_4.setPlainText(_file_4[0].split("/")[-1])
        try:
            self.view_program_4.setPlainText(open(_file_4[0], mode='r').read())
            fn_submit_problem(_problem_id_1ist[3],open(_file_4[0], mode='r').read())
            self.result_4.setPlainText('等待評分結果...')
            for i in range(0,30,1):
                QtTest.QTest.qWait(2000)
                _recv=fn_get_result(_problem_id_1ist[3])
                if(_recv!=''):
                    self.result_4.setPlainText(_recv)
        except:
            print('upload file error')  

if __name__ == "__main__":
    setup()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
