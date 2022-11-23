# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SpiderSteamItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    game_name = scrapy.Field()
    game_category = scrapy.Field()
    game_review_cnt = scrapy.Field()
    game_total_review = scrapy.Field()
    game_release_date = scrapy.Field()
    game_developer = scrapy.Field()
    game_tags = scrapy.Field()
    game_price = scrapy.Field()
    game_platforms = scrapy.Field()
