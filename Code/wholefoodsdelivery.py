import pandas as pd, numpy as np, json, time, urllib, json, os, codecs, re, datetime
from bs4 import BeautifulSoup as BS
from itertools import chain
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import smtplib
class wholefoods(object):
    def __init__(self, chromepath ='C://Program Files/chromedriver.exe', creds = 'C:/Users/yangy/Dropbox/Documents/credentials/amazon.json', emailcreds = 'C:/Users/yangy/Dropbox/Documents/credentials/gmail.json', logs = '../Logs/log.csv'):
        self.avail=False
        self.logpath = logs
        self.checktime = datetime.datetime.now()
        self.driver = webdriver.Chrome(chromepath)
        with open(creds, 'r') as f:
            creds = json.loads(f.read())
        self.un = creds.get('un')
        self.pw = creds.get('pw')
        with open(emailcreds, 'r') as f:
            creds = json.loads(f.read())
        self.email_un = creds.get('un')
        self.email_pw = creds.get('pw')
    def quit_driver(self):
        try:
            self.driver.quit()
        except:
            pass
    def restart_driver(self):
        try:
            self.quit_driver()
        except:
            pass
        self.__init__()
    def get_page(self, url):
        self.driver.get(url)
    def quit(self):
        try:
            self.driver.quit()
        except:
            pass
    def login_amazon(self):
        self.get_page('https://www.amazon.com/')
        time.sleep(2)
        try:
            self.driver.find_element_by_id('nav-signin-tooltip').click()
        except:
            try:
                url = BS(self.driver.find_element_by_id('nav-signin-tooltip').get_attribute('innerHTML')).find_all('a')[0].get('href')
                url = 'https://www.amazon.com/{}'.format(url)
            except:
                time.sleep(10)
                url = BS(self.driver.find_element_by_id('nav-flyout-ya-signin').get_attribute('innerHTML')).find_all('a')[0].get('href')
            self.get_page(url)
        self.driver.find_element_by_class_name('a-input-text').send_keys(self.un)
        self.driver.find_element_by_id('continue').click()
        self.driver.find_element_by_id('ap_password').send_keys(self.pw)
        self.driver.find_element_by_id('signInSubmit').click()
    def send_gmail(self, sendto, when = ''):
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        headers = '\r\n'.join(['from: ' + self.email_un,
                            'subject: WF availability',
                            'to: ' + sendto,
                            'mime-version: 1.0',
                            'content-type: text/html'])
        body = "Availability Changed! WF can now deliver {}".format(when)
        content = headers + '\r\n\r\n' + body
        session.sendmail(self.email_un, sendto, content)
        session.quit()
    def check_store_avail(self):
        self.get_page('https://www.amazon.com/')
        select = Select(self.driver.find_element_by_id('searchDropdownBox'))
        select.select_by_visible_text('Whole Foods Market')
        self.driver.find_element_by_id('twotabsearchtextbox').click()
        self.driver.find_element_by_class_name('nav-search-submit').click()
        time.sleep(5)
        try:
            try:
                sc = self.driver.find_element_by_class_name('naw-widget-emergency-banner-limited-availability-desktop-container').get_attribute('innerHTML').lower()
            except:
                sc = self.driver.find_element_by_class_name('naw-widget-emergency-banner-no-availability-desktop-container').get_attribute('innerHTML').lower()
        except:
            sc = ''

        if ('unavailable' in sc.lower())|('sold out' in sc.lower()):
            self.avail = False
            self.checktime = datetime.datetime.now()
        elif self.avail == True:
            self.avail = True
            self.checktime = datetime.datetime.now()
        else:
            self.avail = True
            self.checktime = datetime.datetime.now()
            try:
                when = BS(sc).find_all('span', {'class':'a-size-medium'})[-1].text.strip()
            except:
                when = ''
            self.send_gmail(self.email_un, when)
    def write_to_log(self):
        try:
            with codecs.open(self.logpath,'a', encoding = 'utf-8' ) as f:
                f.write(','.join([str(self.avail), str(self.checktime)])+'\n')
        except:
            with codecs.open(self.logpath,'w', encoding = 'utf-8') as f:
                f.write(','.join([str(self.avail), str(self.checktime)])+'\n')
    def keep_checking(self, timer = 60*30, maxcheck = 24*60*60*30):
        t0 = time.time()
        while True:
            try:
                time.sleep(timer)
                self.check_store_avail()                
                self.write_to_log()
                if time.time()-t0>maxcheck:
                    self.quit()
                    break
            except:
                pass
