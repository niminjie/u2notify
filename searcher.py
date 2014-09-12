from pprint import pprint
from sendmail import *
import os
import datetime
import logging

LOG_FILENAME = os.path.abspath('.') + os.path.sep + "log.out"
logger = logging.getLogger()

class Searcher():
    def __init__(self, browser):
        self.browser = browser

    def get_promotion(self, torrent):
        text = []
        for img in torrent.find_elements_by_xpath("./td[2]/table/tbody/tr/td[1]/img"):
            text.append(img.get_attribute("alt"))

        if "FREE" in text:
            return "Free"
        elif "2X Free" in text:
            return "2X Free"
        elif "50%" in text:
            return "50%"
        elif "2X" in text:
            return "2X"
        elif "Promotion" in text:
            return "other"
        else:
            return "None"

    def find_torrents(self, items):
        first = False
        if len(items) < 1:
            first = True
        torrents = self.browser.find_elements_by_xpath("//table[@class='torrents']/tbody/tr[position()>1]")
        text = ''

        # print len(torrents)
        for torrent in torrents:
            item = {}
            item['title'] = torrent.find_element_by_xpath("./td[2]/table/tbody/tr/td[1]/a").get_attribute('title')
            item['link'] = torrent.find_element_by_xpath("./td[2]/table/tbody/tr/td[1]/a").get_attribute('href')
            item['type'] = torrent.find_element_by_xpath("./td[1]/a").text
            item['date'] = torrent.find_element_by_xpath("./td[4]/span").text
            item['size'] = torrent.find_element_by_xpath("./td[5]").text.replace('\n', '')
            item['promotion'] = self.get_promotion(torrent)
            try:
                item['seeders'] = torrent.find_element_by_xpath("./td[6]/b/a").text
            except:
                item['seeders'] = '0'
            try:
                item['leechers'] = torrent.find_element_by_xpath("./td[7]/b/a").text
            except:
                item['leechers'] = '0'

            item_names = [i['title'] for i in items]

            # if item['title'] not in item_names and (item['promotion'] in ['other', '2X Free', 'Free']):
            if item['title'] not in item_names:
                print item['link']
                print item['promotion']
                print item['title']
                print '-' * 50
                text += item['link'] + '\n'
                text += item['promotion'] + '\n'
                text += item['size'] + '\n'
                text += item['title'] + '\n'
                text += '=' * 50 + '\n' *2
                items.append(item)

        if text != '' and not first:
            send_mail('niminjiecide@gmail.com', 'U2 New Torrent ' + str(datetime.datetime.now()), text.encode('utf8'))
            send_mail('yytcjcy@gmail.com', 'U2 New Torrent ' + str(datetime.datetime.now()), text.encode('utf8'))

            print "Sending mail.."
            print "Text: "
            print text
            print '-' * 50
            print "Length of items: "
            print len(items)
            print '-' * 50
            print '*' * 50

        elif text == '':
            print "Not find new torrents on :" + str(datetime.datetime.now())
        print '=' * 50
