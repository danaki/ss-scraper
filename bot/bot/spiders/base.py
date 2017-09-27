# -*- coding: utf-8 -*-
import re
import time
import yaml
import os

from mongoengine import *

import unicodedata as ud

from pprint import pprint
from collections import OrderedDict
from datetime import datetime
from scrapy import Spider, Request
from dictdiffer import dot_lookup
from bot.items import *


class ItemSpider(Spider):
    allowed_domains = ["ss.com"]

    def __init__(self, *args, **kwargs):
        super(ItemSpider, self).__init__(*args, **kwargs)

        self.translations = self._y2d(yaml.load(open(os.path.dirname(os.path.realpath(__file__)) + "/translations.yml", "r")))

    def parse_item(self, response):
        title = response.xpath('//table[@id="page_main"]//h2')
        action = self._trabbr('ACTIONS', re.sub("[ /]+", '', title.xpath('text()').extract()[-1]))
        properties = self._tokv(response.xpath('//table[@class="options_list"]//tr/td/table'))
        contacts = self._tokv(response.xpath('//table[@class="contacts_table"]'))

        # yet another check for Selling
        if not action in ['sell', 'hand_over']:
            return None

        if re.search(r'ss\.com/msg/lv/transport/cars/', response.url):
            extra = self._tokv_boolean(response.xpath('//td[@class="auto_c_column"]'))

            (kind, brand, model) = title.xpath('a/text()').extract()

            kv = self._flatten(properties, contacts, extra)

            mileage = self._toint(kv.pop('mileage')) if 'mileage' in kv else None

            production_year = kv.pop('production_year')
            production_month = None
            if " " in production_year:
                (production_year, production_month) = re.split(" ", production_year)

            (engine_volume, engine_fuel) = re.split(" ", kv.pop('engine'))

            (inspection_month, inspection_year) = re.split("[ \.]+", kv.pop('inspection_date'))
            (inspection_month, inspection_year) = (None, None) if inspection_month == 'Bez' else (int(inspection_year), int(inspection_month))

            gearbox = re.split("[ \.]+", kv.pop('gearbox'))[0]
            body_type = kv.pop('body_type')

            # remove metālika
            color = re.sub(r" \xa0.*$", "", kv.pop('color')).strip() if 'color' in kv else None

            item = CarItem(
                brand=brand,
                model=model,
                mileage=mileage,
                production_year=int(production_year),
                production_month=self._trmonth(production_month),
                engine_volume=float(engine_volume),
                engine_fuel=self._trabbr('FUEL_TYPES', engine_fuel),
                inspection_month=inspection_month,
                inspection_year=inspection_year,
                gearbox=self._trabbr('GEARBOXES', gearbox),
                color=self._trabbr('COLORS', color),
                body_type=self._trabbr('BODY_TYPES', body_type),
                **kv
            )
        elif re.search(r'ss\.com/msg/lv/real-estate/flats/', response.url):
            (_, city) = properties.popitem(False)
            (_, district) = properties.popitem(False)

            kv = self._flatten(properties, contacts)

            parts = kv.pop('floor').split("/")
            lift = True if len(parts) >= 3 and parts[2] == "lifts" else None
            floors_total = self._toint(parts[1]) if len(parts) >= 2 else None
            floor = self._toint(parts[0])

            rooms = kv.pop('rooms')
            rooms = None if rooms == 'Citi' else int(rooms)

            # city1 = kv.pop('city1') if 'city1' in kv.keys() else None
            # city2 = kv.pop('city2') if 'city2' in kv.keys() else None

            # district1 = kv.pop('district1') if 'district1' in kv.keys() else None
            # district2 = kv.pop('district2') if 'district2' in kv.keys() else None

            street = re.sub(r"\[.*", "", kv.pop('street')).rstrip()

            building_type = kv.pop('building_type')
            conveniences = kv.pop('conveniences')
            area = self._tofloat(kv.pop('area'))

            item = FlatItem(
                area=area,
                city=city,
                district=district,
                street=street,
                lift=lift,
                floor=floor,
                floors_total=floors_total,
                rooms=rooms,
                building_type=self._trabbr('BUILDING_TYPES', building_type),
                conveniences=self._trabbr('CONVENIENCES', conveniences),
                **kv
            )

        else:
            return None

        is_open = not bool(response.xpath('//table[@class="contacts_table"]//img[contains(@src, "/img/a_lv.gif")]').extract_first())
        text = self._item_text(response)
        (price, price_period) = self._item_price(response)

        item.update(dict(
            open=is_open,
            created=self._item_created(response),
            highlighted=response.meta.get('highlighted', None),
            price=price,
            price_period=self._trabbr('PRICE_PERIODS', price_period, default=None),
            views=self._item_views(response),
            url=response.url,
            text_rus_ratio=self._rus_ratio(text),
            text_length=len(text),
        ))

        return item

    def _flatten(self, *args):
        rval = {}
        for d1 in args:
            for k1, v1 in d1.iteritems():
                if k1 in self.translations.keys():
                    # self.categories[k1]
                    if isinstance(v1, dict):
                        for k2, v2 in v1.iteritems():
                            rval[self.translations[k1][k2]['abbr']] = v2
                    else:
                        rval[self.translations[k1]['abbr']] = v1

        return rval

    def _rus_ratio(self, unistr):
        _cache = {}
        def _is_latin(uchr):
            if not uchr in _cache.keys():
                _cache[uchr] = 'LATIN' in ud.name(uchr)
            return _cache[uchr]

        a = [_is_latin(uchr) for uchr in unistr if uchr.isalpha()]

        lat = a.count(True)
        rus = a.count(False)
        total = rus + lat

        return rus / total if total > 0 else None

    def _tofloat(self, v):
        return float(re.sub(r"[^0-9\s\.].*$", "", v).replace(' ', ""))

    def _toint(self, v):
        return int(self._tofloat(v))

    def _tokv(self, table):
        d = OrderedDict()
        trs = table.xpath('.//tr')
        for tr in trs:
            tds = tr.xpath('td').xpath('normalize-space(.)').extract()
            if len(tds) >= 2:
                k = tds[0].rstrip(':').strip()
                v = tds[1].strip()
                d[k] = v

        return d

    def _tokv_boolean(self, table):
        extra = {}

        for td in table:
            for el in td.xpath('*'):
                tag = el.xpath('name()').extract_first()
                t = el.xpath('text()')
                text = t.extract_first() if t else ''
                if tag == 'div':
                    cat = text
                    if not cat in extra:
                        extra[cat] = {}
                elif tag == 'b':
                    extra[cat][text] = True

        return extra

    def _y2d(self, v0):
        def nd(v):
            abbr = re.sub(r"[^a-z0-9]", "_", v.lower())
            abbr = re.sub(r"_+", "_", abbr)
            return dict(english=v, abbr=abbr)

        d = {}
        for k1, v1 in v0.iteritems():
            if isinstance(v1, dict):
                d[k1] = {}
                for k2, v2 in v1.iteritems():
                    d[k1][k2] = nd(v2)
            else:
                d[k1] = nd(v1)

        return d

    def _trabbr(self, *path, **kwargs):
        try:
            return dot_lookup(self.translations, list(path) + ['abbr'])
        except KeyError:
            return kwargs['default'] if 'default' in kwargs else path[-1]

    def _trmonth(self, month):
        import calendar
        d = dict((v,k) for k,v in enumerate(calendar.month_name))
        return self._trabbr('MONTHS', month)

    def _item_price(self, response):
        s = response.xpath('//*[@class="ads_price"]/text()').extract_first()
        m = re.match(ur'^([0-9 ]+) \u20ac?(?:\/?([^ ]+)?)', s)

        return (self._toint(m.group(1)), m.group(2)) if m else (None, None)

    def _item_views(self, response):
        return self._toint(response.xpath('//*[@id="show_cnt_stat"]/text()').extract_first())

    def _item_created(self, response):
        created_str = response.xpath('//td[@class="msg_footer" and @align="right" and starts-with(text(), "Datums:")]/text()').extract_first().split("Datums: ", 1)[1]
        return datetime.fromtimestamp(time.mktime(time.strptime(created_str, "%d.%m.%Y %H:%M")))

    def _item_text(self, response):
        return " ".join([line.strip() for line in response.xpath('//div[@id="msg_div_msg"]/div/following-sibling::table/preceding-sibling::text()').extract()]).strip()


class ItemListSpider(ItemSpider):
    def __init__(self, *args, **kwargs):
        super(ItemListSpider, self).__init__(*args, **kwargs)

        connect(host='mongodb://localhost:27017/scrapy')

    def parse_list(self, response):
        model = None
        if re.search(r'ss\.com/lv/transport/cars/', response.url):
            model = Car
        elif re.search(r'ss\.com/lv/real-estate/flats/', response.url):
            model = Flat

        if model:
            trs = response.xpath('//form[@id="filter_frm"]/table[not(@id="filter_tbl")]/tr[starts-with(@id, "tr_") and not(starts-with(@id, "tr_bnr_"))]')

            urls = set()
            for tr in trs:
                last_td = tr.xpath('td[last()]')
                has_euro = u"\u20ac" in last_td.xpath('text()').extract_first()

                # /sell sometimes buggy? additional check for Selling classified
                if has_euro:
                    urls.update([response.urljoin(tr.xpath('td/a/@href').extract_first())])

            dburls = set([c.url for c in model.objects(url__in=urls)])
            diff = urls - dburls

            for url in diff:
                request = Request(response.urljoin(url), callback=self.parse_item)

                request.meta['highlighted'] = not last_td.xpath('b').extract_first() is None

                # items require javascript in order to collect views
                request.meta['need_prerender'] = True

                yield request
            else:
                self.logger.info("No new items found on list page {}".format(response.url))

            # next page if only this page contains new items
            if len(diff) > 0:
                next_page_url = response.xpath('(//div/a[@rel="next"]/@href)[last()]').extract_first()
                if not next_page_url is None and not (next_page_url.endswith("/") or next_page_url.endswith("/page1.html")):
                    yield Request(response.urljoin(next_page_url), callback=self.parse_list)
