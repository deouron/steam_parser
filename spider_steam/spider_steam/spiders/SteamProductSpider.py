import scrapy
from urllib.parse import urlencode
from urllib.parse import urljoin
import re
import requests
from bs4 import BeautifulSoup
from scrapy.exceptions import CloseSpider
from spider_steam.items import SpiderSteamItem


# API = ''
#
#
# def get_url(url):
#     payload = {'api_key': API, 'url': url}
#     proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
#     return proxy_url


def find_all_links(URL):
    r = requests.get(URL)
    page = r.content.decode("utf-8")
    soup = BeautifulSoup(page, 'html.parser')
    root = soup.find('div', {'id': 'search_resultsRows'})
    games = set()
    for game in root.find_all('a'):
        if game.get('href') is not None:
            cur_game = game.get('href')
            if cur_game in games or cur_game == '' or 'app' not in cur_game or 'agecheck' in cur_game:
                continue
            games.add(cur_game)
    return games


def do_start_urls():
    start_urls = []
    queries = ['cities', 'racing', 'cyber']
    for query in queries:
        for i in range(1, 3):
            url = 'https://store.steampowered.com/search/?term=' + str(query) + '&ignore_preferences=1&page=' + str(i)
            games = find_all_links(url)
            for game in games:
                start_urls.append(game)
    return start_urls


class SteamproductspiderSpider(scrapy.Spider):
    name = 'SteamProductSpider'
    allowed_domains = ['store.steampowered.com']
    start_urls = do_start_urls()

    def parse(self, response):
        # print("URLS:", *self.start_urls)
        items = SpiderSteamItem()
        name = response.xpath('//div[@id="appHubAppName"][@class="apphub_AppName"]/text()').extract()
        category = response.xpath('//div[@class="blockbg"]/a/text()').extract()
        review_cnt = response.xpath(
            '//div[@itemprop="aggregateRating"]/div[@class="summary column"]/span[@class="responsive_hidden"]/text()').extract()
        total_review = response.xpath(
            '//div[@itemprop="aggregateRating"]/div[@class="summary column"]/span[@class="game_review_summary positive"]/text()').extract()
        release_date = response.xpath('//div[@class="release_date"]/div[@class="date"]/text()').extract()
        developer = response.xpath('//div[@class="dev_row"]/div[@id="developers_list"]/a/text()').extract()
        tags = response.xpath('//div[@class="glance_tags popular_tags"]/a/text()').extract()
        price = response.xpath('//div[@class="discount_final_price"]/text()').extract()
        if len(price) == 0:
            price = response.xpath('//div[@class="game_purchase_price price"]/text()').extract()
        platforms = response.xpath('//div[@class="sysreq_tabs"]/div/text()').extract()

        items['game_name'] = ''.join(name).strip()
        items['game_category'] = '/'.join(map(lambda x: x.strip(), category[1:])).strip()
        items['game_review_cnt'] = ''.join(re.sub(r'\D', '', str(review_cnt))).strip()
        items['game_total_review'] = ''.join(total_review).strip()
        items['game_release_date'] = ''.join(release_date).strip()
        items['game_developer'] = ','.join(map(lambda x: x.strip(), developer)).strip()
        items['game_tags'] = ', '.join(map(lambda x: x.strip(), tags)).strip()
        try:
            items['game_price'] = ''.join(re.sub(r"[\u0443\u0431\r\n\t]", '', price[0])).strip()
        except Exception:
            try:
                items['game_price'] = ''.join(price[0]).strip()
            except Exception:
                items['game_price'] = ''.join(price).strip()
        items['game_platforms'] = ', '.join(map(lambda x: x.strip(), platforms)).strip()
        # print('ITEMS:', items.values())

        year = '2000'
        if len(items['game_release_date']) > 0:
            try:
                year = items['game_release_date'].split()[-1]
            except Exception:
                pass
        if len(name) != 0 and len(name[0]) != 0 and year >= '2000':
            yield items
