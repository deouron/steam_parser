# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


import json
from itemadapter import ItemAdapter


class SpiderSteamPipeline:
    def open_spider(self, spider):
        self.file = open('items.json', 'w+')

    def close_spider(self, spider):  # что делать при окончании работы паука (закрываем файлик)
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item
