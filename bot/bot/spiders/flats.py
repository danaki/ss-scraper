# -*- coding: utf-8 -*-
from __future__ import division

import re
import datetime

from scrapy import Spider, Request

from .base import ItemListSpider

class FlatsSpider(ItemListSpider):
    name = "flats"
    start_urls = (
        'https://www.ss.com/lv/real-estate/flats/',
    )

    def parse(self, response):
        # cities
        for url in response.xpath('//table[@id="page_main"]//table[not(@id="filter_tbl")]//a[@class="a_category"]/@href').extract():
            if re.search(r'/real-estate/flats/(?!other|flats-abroad-latvia).*$', url):
                for action in ['sell', 'hand_over']:
                    yield Request(response.urljoin(url).rstrip('/') + "/all/" + action + "/", callback=self.parse_list)
