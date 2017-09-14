import re
import logging

logger = logging.getLogger(__name__)

class PrerenderMiddleware(object):
    def __init__(self, settings):
        self.prerender_base_url = settings.get('PRERENDER_BASE_URL')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        if request.url.startswith(self.prerender_base_url):
            return None

        if request.meta.get('need_prerender', False):
            # if not re.match(r'.*://[^/]+/msg/', request.url):
            #     logging.debug("Proceed WITHOUT Preparse: " + request.url)
            #     return None

            # Only msg pages require javascript engine
            logger.debug("Proceed WITH Preparse: " + request.url)

            request.meta['original_url'] = request.url
            url = self.prerender_base_url + request.url

            return request.replace(url=url)

    def process_response(self, request, response, spider):
        url = request.meta.get('original_url')
        return response.replace(url=url) if url else response
