import scrapy
from urllib.parse import urlencode
from urllib.parse import urljoin
import re
import requests
from bs4 import BeautifulSoup
from spider_steam.items import SpiderSteamItem


queries = ['minecraft', 'cities']
API = ''


# def get_url(url):
#     payload = {'api_key': API, 'url': url, 'country_code': 'us'}
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
            if cur_game in games:
                continue
            games.add(cur_game)
    return games


class SteamproductspiderSpider(scrapy.Spider):
    name = 'SteamProductSpider'
    allowed_domains = ['store.steampowered.com']
    URL = 'https://store.steampowered.com/search/?'
    items = None
    # start_urls = ['https://store.steampowered.com/app/255710/Cities_Skylines/']

    def start_requests(self):
        self.items = SpiderSteamItem()
        for query in queries:
            url = 'https://store.steampowered.com/search/?' + urlencode({'term': query, 'ignore_preferences': 1})
            self.URL = str(url)
            yield scrapy.Request(url=url, callback=self.parse_keyword_response, dont_filter=True)

    def parse_keyword_response(self, response):
        games = find_all_links(self.URL)
        for game in games:
            yield scrapy.Request(url=game, callback=self.parse, dont_filter=True)

    def parse(self, response):
        name = response.xpath('//div[@id="appHubAppName"]/text()').extract()
        category = response.xpath('//div[@class="blockbg"]/a/text()').extract()
        review_cnt = response.xpath('//div[@itemprop="aggregateRating"]/div[@class="summary column"]/span[@class="responsive_hidden"]/text()').extract()
        total_review = response.xpath('//div[@itemprop="aggregateRating"]/div[@class="summary column"]/span[@class="game_review_summary positive"]/text()').extract()
        release_date = response.xpath('//div[@class="release_date"]/div[@class="date"]/text()').extract()
        developer = response.xpath('//div[@class="dev_row"]/div[@id="developers_list"]/a/text()').extract()
        tags = response.xpath('//div[@class="glance_tags popular_tags"]/a/text()').extract()
        # platforms = response.xpath('//div[@class="glance_tags popular_tags"]/a/text()').extract()
        self.items['game_name'] = ''.join(name).strip()
        self.items['game_category'] = '/'.join(map(lambda x: x.strip(), category[1:])).strip()
        self.items['game_review_cnt'] = ''.join(re.sub(r'\D', '', str(review_cnt))).strip()
        self.items['game_total_review'] = ''.join(total_review).strip()
        self.items['game_release_date'] = ''.join(release_date).strip()
        self.items['game_developer'] = ','.join(map(lambda x: x.strip(), developer)).strip()
        self.items['game_tags'] = ', '.join(map(lambda x: x.strip(), tags)).strip()
        # items['game_platforms'] = ', '.join(map(lambda x: x.strip(), platforms)).strip()
        yield self.items
