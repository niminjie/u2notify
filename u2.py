import pickle
from selenium import webdriver
from filt import PromotionFilter
import time
import os
import logging
import datetime
import sys
from PIL import Image
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
from selenium import webdriver
from searcher import Searcher
from sendmail import *

refresh_time = 10

logger = logging.getLogger("default")
LOG_FILENAME = os.path.abspath('.') + os.path.sep + "debug.log"
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(funcName)s %(message)s', '%a, %d %b %Y %H:%M:%S',)  
file_handler = logging.FileHandler(LOG_FILENAME)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler(sys.stderr)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)
# logger.removeHandler(stream_handler)

class U2Broswer():
    def __init__(self, browser_name):
        ''' Initial Firefox webbrowser '''
        logger.info("Initial web driver")
        self.driver = webdriver.Firefox()
        self.login_url = 'http://u2.dmhy.org/portalbc.php'
        self.torrent_url = 'http://u2.dmhy.org/torrents.php'
        try:
            self.cookies = pickle.load(open('cookies.pkl', 'rb'))
        except:
            logger.error("Read cookies failed")
            self.cookies = None

    def go2torrentpage(self):
            self.driver.get(self.torrent_url)

    def login(self, username, password):
        # Navigate to login page and save captcha image
        self.driver.get(self.login_url)
        self.driver.save_screenshot('screenshot.png')
        self.crop_image()
        self.open_image()

        # Input captcha from user
        captcha = raw_input("Please input the captcha: ").strip()
        # print "The captcha is %s." % captcha
        logger.info("Logining....")

        username_box = self.driver.find_element_by_xpath("//*[@id='input-login-email']")
        password_box = self.driver.find_element_by_xpath("//*[@id='form-login']/input[3]")
        captcha_box = self.driver.find_element_by_xpath("/html/body/form/input[4]")

        # Fill in login information
        username_box.send_keys(username)
        password_box.send_keys(password)
        captcha_box.send_keys(captcha)

        btn_login = self.driver.find_element_by_xpath("//*[@id='form-login']/input[7]")
        btn_login.click()

        # Save cookies
        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open('cookies.pkl', 'wb'))
        logger.info("Login successfully!!")

    def start_capture(self):
        logger.info('Start capturing torrent')
        searcher = Searcher(self.driver)
        # items = {}
        while(True):
            try:
                last = pickle.load(open('torrents.pkl', 'rb'))
            except:
                last = {}
                logger.error("Can't find previous torrent list!")

            # Watch specific fields to watch
            watch_fields = ['promotion']

            # Current web page
            current = searcher.scratch_refresh_torrents()

            # New and updated torrents compare with last time list
            new_torrents = searcher.get_new_torrents(last, current)
            updated_torrents = searcher.get_updated_torrents(last, current, watch_fields)

            # Add new and updated to last time list
            self.combine(last, new_torrents, updated_torrents)

            filt = PromotionFilter(["2X Free", "Free", "other"])

            text_new = filt.generate_text(new_torrents)
            text_updated = filt.generate_text(updated_torrents)

            logger.debug("Text new: " + text_new)
            logger.debug("Text updated: " + text_updated)

            # Send mail
            # receiver = ['niminjiecide@gmail.com', 'yytcjcy@gmail.com']
            receiver = ['niminjiecide@gmail.com']
            if text_new:
                logger.info("Send mail to :" + str(receiver))
                send_mail(receiver, 'DEMO U2 New Torrent ' + str(datetime.datetime.now()), text_new.encode('utf8'))
            if text_updated:
                logger.info("Send mail to :" + str(receiver))
                send_mail(receiver, 'DEMO U2 Updated Torrent ' + str(datetime.datetime.now()), text_updated.encode('utf8'))

            pickle.dump(last, open('torrents.pkl', 'wb'))
            # Just a minute
            time.sleep(refresh_time)
            self.driver.refresh()

    def combine(self, last, new, updated):
        for title, info in new.items():
            last[title] = info

        for title, info in updated.items():
            last[title] = info

    def crop_image(self):
        im = Image.open('screenshot.png')
        im.crop((7, 675, 115, 715)).save("captcha.png", "png")
        os.remove('screenshot.png')

    def open_image(self):
        im = Image.open('captcha.png')
        im.show()

    def quit(self):
        logger.info("Quiting browser")
        self.driver.quit()

    def set_cookies(self, cookies):
        logger.debug("Cookies: " + str(cookies))
        self.cookies = cookies
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def get_cookies(self):
        return self.cookies

if __name__ == "__main__":
    browser = U2Broswer("firefox")

    if browser.cookies == None:
        # Login manually
        browser.login('niminjiecide@gmail.com', '19900826')
    else:
        logger.info('Login without password...')
        # Set domain
        browser.go2torrentpage()
        # Set cookies
        browser.set_cookies(browser.cookies)

    # Navi to torrent page
    browser.go2torrentpage()

    # Cookies invalid
    if browser.driver.current_url == browser.login_url:
        browser.login('niminjiecide@gmail.com', '19900826')
        browser.go2torrentpage()

    # Start to capture new torrent
    browser.start_capture()
