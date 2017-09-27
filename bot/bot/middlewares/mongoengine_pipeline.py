# coding:utf-8
import datetime
import logging

from collections import defaultdict
from dictdiffer import diff
from mongoengine import connect, Q

from scrapy.exporters import BaseItemExporter

logger = logging.getLogger(__name__)

def not_set(string):
    """ Check if a string is None or ''

    :returns: bool - True if the string is empty
    """
    if string is None:
        return True
    elif string == '':
        return True
    return False


class MongoenginePipeline(BaseItemExporter):
    """ MongoDB pipeline class """
    # Default options
    config = {
    }

    # Item buffer
    current_item = 0
    item_buffer = []

    def load_spider(self, spider):
        self.crawler = spider.crawler
        self.settings = spider.settings

    def open_spider(self, spider):
        self.load_spider(spider)

        # Configure the connection
        self.configure()

        connection = connect(host=self.config['uri'])

        logger.info(u'Connected to MongoDB {0}'.format(self.config['uri']))

    def configure(self):
        """ Configure the MongoDB connection """

        # Set all regular options
        options = [
            ('uri', 'MONGOENGINE_URI')
        ]

        for key, setting in options:
            if not not_set(self.settings[setting]):
                self.config[key] = self.settings[setting]

    def process_item(self, item, spider):
        """ Process the item and add it to MongoDB

        :type item: Item object
        :param item: The item to put into MongoDB
        :type spider: BaseSpider object
        :param spider: The spider running the queries
        :returns: Item object
        """
        return self.insert_item(item, spider)

    def close_spider(self, spider):
        """ Method called when the spider is closed

        :type spider: BaseSpider object
        :param spider: The spider running the queries
        :returns: None
        """
        if self.item_buffer:
            self.insert_item(self.item_buffer, spider)

    def insert_item(self, item, spider):
        """ Process the item and add it to MongoDB

        :type item: (Item object) or [(Item object)]
        :param item: The item(s) to put into MongoDB
        :type spider: BaseSpider object
        :param spider: The spider running the queries
        :returns: Item object
        """

        cls = item.__class__.mongoengine_model
        meta = cls._meta
        prev = cls.objects(Q(url=item['url']) & Q(open=True)).first()

        if prev:
            inst = item.instance
            item_d = inst.to_mongo()
            prev_d = prev.to_mongo()

            for k in item_d.keys():
                if k.startswith('_'):
                    del item_d[k]

            for k in prev_d.keys():
                if k.startswith('_'):
                    del prev_d[k]

            inst._changes = prev._changes

            diffs = defaultdict(dict)
            for command, k, v in diff(prev_d, item_d):
                diffs[command]['.'.join(str(k1) for k1 in k) if isinstance(k, list) else k] = v

            inst._changes.append(diffs)
            inst.id = prev.id
        elif not item['open']:
            # don't save closed items
            return None

        i = item.save()

        logger.info(u'Stored item(s) in MongoDB {0}/{1} {2}'.format(
            meta.get("db_alias", '[default]'), meta.get('collection'), 'UPDATE' if prev else 'INSERT'))

        return i
