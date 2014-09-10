import pickle
from selenium import webdriver
import time
import os
from PIL import Image
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
from selenium import webdriver
from searcher import Searcher

class U2Broswer():
    def __init__(self, browser_name):
        ''' Initial Firefox webbrowser '''
        self.driver = webdriver.Firefox()
        self.login_url = 'http://u2.dmhy.org/portalbc.php'
        self.torrent_url = 'http://u2.dmhy.org/torrents.php'
        try:
            self.cookies = pickle.load(open('cookies.pkl', 'rb'))
        except:
            print "Read cookies failed"
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
        print "Logining...."

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
        print "Login successfully!!"

    def find_torrent(self):
        print '=' * 100
        print 'Start capturing torrent'
        searcher = Searcher(self.driver)
        items = []

        while(True):
            searcher.find_torrents(items)
            time.sleep(10)
            self.driver.refresh()

    def crop_image(self):
        im = Image.open('screenshot.png')
        im.crop((7, 675, 115, 715)).save("captcha.png", "png")
        os.remove('screenshot.png')

    def open_image(self):
        im = Image.open('captcha.png')
        im.show()

    def enter_torrent_menu(self):
        time.sleep(2)
        print "Entering torrent menu..."
        torrent_menu = self.driver.find_element_by_xpath("/html/body/table[2]/tbody/tr/td/table/tbody/tr/td/div/ul/li[3]/a")
        torrent_menu.click()

    def quit(self):
        print "Quiting browser"
        self.driver.quit()

    def set_cookies(self, cookies):
        self.cookies = cookies
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def get_cookies(self):
        return self.cookies

if __name__ == "__main__":
    browser = U2Broswer("firefox")

    if browser.cookies == None:
        # Request login manually
        browser.login('niminjiecide@gmail.com', '19900826')
    else:
        print ' Login without password'
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

    browser.find_torrent()
