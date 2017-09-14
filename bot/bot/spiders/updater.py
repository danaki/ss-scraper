# -*- coding: utf-8 -*-
from __future__ import division

import re

from datetime import datetime, timedelta
from time import sleep
from collections import defaultdict
from scrapy import Spider, Request
from pprint import pprint
from mongoengine import connect, Q

from .base import ItemSpider

from bot.items import Car, Flat


class UpdaterSpider(ItemSpider):
    name = "updater"

    def __init__(self, *args, **kwargs):
        super(UpdaterSpider, self).__init__(*args, **kwargs)

        connect(host='mongodb://localhost:27017/scrapy')

    def start_requests(self):
        for cls in [Car, Flat]:
            for item in cls.objects(Q(crawled__lt=datetime.now() - timedelta(hours=6)) & Q(open=True)):
                self.logger.info("Updating url {}".format(item.url))
                request = Request(item.url, callback=self.parse_item)

                request.meta['highlighted'] = item.highlighted
                request.meta['need_prerender'] = True

                yield request

