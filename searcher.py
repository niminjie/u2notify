from pprint import pprint
from sendmail import *
import os
import sys
import datetime
import logging
import cPickle as pickle
import traceback

logger = logging.getLogger("default")

web_xpath = {
        'torrents' : "//table[@class='torrents']/tbody/tr[position()>1]",
        'link'     : "./td[2]/table/tbody/tr/td[1]/a",
        'title'    : "./td[2]/table/tbody/tr/td[1]/a",
        'type'     : "./td[1]/a",
        'size'     : "./td[5]",
        'imgs'     : "./td[2]/table/tbody/tr/td[1]/img",
        'date'     : "./td[4]/span",
        'seeders'  : "./td[6]/b/a",
        'leechers' : "./td[7]/b/a"
        }

class Searcher():
    def __init__(self, browser):
        self.browser = browser

    def _get_promotion(self, torrent):
        text = []
        for img in torrent.find_elements_by_xpath(web_xpath['imgs']):
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

    def _comparison(self, last, current, compare_fields):
        updated_list = {}
        for title, info in current.items():
            if title in last:
                logger.debug("Comparing: " + title)
                for key in compare_fields:
                    if last[title][key] == info[key]:
                        continue
                    else:
                        updated_list[title] = info
        print "*" * 50
        print updated_list
        print "*" * 50
        return updated_list

    def _xpath_catch(self, torrent, items, title):
        items.setdefault(title, {})
        items[title]['updated'] = False
        items[title]['link'] = torrent.find_element_by_xpath(web_xpath['link']).get_attribute('href')
        items[title]['type'] = torrent.find_element_by_xpath(web_xpath['type']).text
        items[title]['date'] = torrent.find_element_by_xpath(web_xpath['date']).text
        items[title]['size'] = torrent.find_element_by_xpath(web_xpath['size']).text.replace('\n', '')

        current_promotion = self._get_promotion(torrent)
        items[title].setdefault('promotion', '')
        if items[title]['promotion'] == '':
            items[title]['promotion'] = current_promotion
        elif items[title]['promotion'] != current_promotion:
            items[title]['updated'] = True
            items[title]['promotion'] = current_promotion

        try:
            items[title]['seeders'] = torrent.find_element_by_xpath("./td[6]/b/a").text
        except:
            items[title]['seeders'] = '0'
        try:
            items[title]['leechers'] = torrent.find_element_by_xpath("./td[7]/b/a").text
        except:
            items[title]['leechers'] = '0'

    def scratch_refresh_torrents(self):
        current = {}
        try:
            torrents = self.browser.find_elements_by_xpath(web_xpath['torrents'])
            text = ''
            # print len(torrents)
            for torrent in torrents:
                title = torrent.find_element_by_xpath(web_xpath['title']).get_attribute('title')
                self._xpath_catch(torrent, current, title)
                logger.debug('link:' + current[title]['link'])
                logger.debug('type:' + current[title]['type'])
                logger.debug('date:' + current[title]['date'])
                logger.debug('size:' + current[title]['size'])
                logger.debug('promotion:' + current[title]['promotion'])
            logger.debug("=" * 50)
            logger.debug(str(current))
            logger.debug("=" * 50)
        except Exception as e:
            logger.warn("Exception, find next time")
            logger.error(traceback.format_exc())
            logger.error(e)
        return current

    def get_new_torrents(self, last, current):
        new = {}
        for title, info in current.items():
            if title not in last:
                new[title] = info
        logger.debug("New torrent: " + str(new))
        return new

    def get_updated_torrents(self, last, current, watch_fields):
        updated = {}

        for title, info in current.items():
            if title in last:
                for field in watch_fields:
                    if info[field] != last[title][field]:
                        updated[title] = info
                        continue
        logger.debug("Updated torrent: " + str(updated))
        return updated

    def find_torrents(self, items):
        first = False
        if len(items) < 1:
            first = True
        try:
            torrents = self.browser.find_elements_by_xpath(web_xpath['torrents'])
            text = ''
            # print len(torrents)
            for torrent in torrents:
                title = torrent.find_element_by_xpath(web_xpath['title']).get_attribute('title')
                self._xpath_catch(torrent, items, title)

                # New item or promotion updated
                if title not in items.keys() or items[title]['updated']:
                    if not items[title]['updated']:
                        # New item
                        logger.info("Find new item " + title)
                    else:
                        # Promotion updated
                        logger.info("Updated item: " + title)
                    logger.debug('link:' + items[title]['link'])
                    logger.debug('type:' + items[title]['type'])
                    logger.debug('date:' + items[title]['date'])
                    logger.debug('size:' + items[title]['size'])
                    logger.debug('promotion:' + items[title]['promotion'])

                    text += items[title]['link'] + '\n'
                    text += items[title]['promotion'] + '\n'
                    text += items[title]['size'] + '\n'
                    if items[title]['updated']:
                        text += "Updated" + title + '\n'
                    else:
                        text += title + '\n'
                    text += '=' * 50 + '\n' *2
                    # items.append(item)

            logger.debug("=" * 50)
            logger.debug(str(items))
            logger.debug("=" * 50)
            if text != '' and not first:
                # receiver = ['niminjiecide@gmail.com', 'yytcjcy@gmail.com']
                receiver = ['niminjiecide@gmail.com']
                send_mail(receiver, 'U2 New Torrent ' + str(datetime.datetime.now()), text.encode('utf8'))
                logger.info("Send mail...")
                logger.debug("Text: " + text)
        except Exception as e:
            logger.warn("Exception, find next time")
            logger.error(traceback.format_exc())
            logger.error(e)
