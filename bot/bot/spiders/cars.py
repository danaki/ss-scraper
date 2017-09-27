# -*- coding: utf-8 -*-
from __future__ import division

import re
import datetime

from scrapy import Spider, Request
from pprint import pprint

from .base import ItemListSpider


class CarsSpider(ItemListSpider):
    name = "cars"
    start_urls = (
        'https://www.ss.com/lv/transport/cars/',
    )

    def parse(self, response):
        # brands
        for url in response.xpath('//table[@id="page_main"]//table[not(@id="filter_tbl")]//td[@width="75%"]//a[@class="a_category"]/@href').extract():
            yield Request(response.urljoin(url), callback=self.parse_models)

    def parse_models(self, response):
        for url in response.xpath('//table[@id="page_main"]//a[@class="a_category" or @class="a1"]/@href').extract():
            if re.search(r'/transport/cars/.+/(?!exchange).*$', url):
                yield Request(response.urljoin(url).rstrip('/') + "/sell/", callback=self.parse_list)

