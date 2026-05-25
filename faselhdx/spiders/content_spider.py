import scrapy
import logging
import json
import os

logger = logging.getLogger(__name__)


class FaselhdxSpider(scrapy.Spider):
    name = 'faselhdx'

    start_urls = [
        'https://web52312x.faselhdx.bid/movies/page/1',
        'https://web52312x.faselhdx.bid/hindi/page/1',
        'https://web52312x.faselhdx.bid/asian-movies/page/1',
        'https://web52312x.faselhdx.bid/anime-movies/page/1',
        'https://web52312x.faselhdx.bid/series/page/1',
        'https://web52312x.faselhdx.bid/asian-series/page/1',
        'https://web52312x.faselhdx.bid/tvshows/page/1',
        'https://web52312x.faselhdx.bid/anime/page/1',
    ]

    custom_settings = {
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [403, 429, 500, 502, 503, 504],
        'DOWNLOAD_TIMEOUT': 30,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.existing_links = {}
        categories = ['movies', 'hindi', 'asian-movies', 'anime-movies',
                      'series', 'asian-series', 'tvshows', 'anime']
        for cat in categories:
            filename = f"{cat}.json"
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.existing_links[cat] = {
                        item['link'] for item in data if 'link' in item
                    }
                    logger.info(f"📂 {cat}: {len(self.existing_links[cat])} رابط موجود")
                except Exception as e:
                    logger.warning(f"⚠️ تعذر قراءة {filename}: {e}")
                    self.existing_links[cat] = set()
            else:
                self.existing_links[cat] = set()

    def parse(self, response):
        try:
            category = response.url.split('/')[3]
        except IndexError:
            logger.warning(f"⚠️ تعذر استخراج الفئة من: {response.url}")
            return

        existing_links = self.existing_links.get(category, set())

        post_divs = response.css('#postList .postDiv')
        page_links = set()

        for post in post_divs:
            anchor = post.css('a')
            if not anchor:
                continue

            img_tag = anchor.css('img')
            if not img_tag:
                continue

            name = img_tag.attrib.get('alt', '').strip()
            if not name:
                name = anchor.css('.h1::text').get('').strip()

            img = img_tag.attrib.get('data-src', '') or img_tag.attrib.get('src', '')
            link = anchor.attrib.get('href', '')

            if not name or not img or not link:
                continue

            if not img.startswith('http'):
                logger.warning(f"⚠️ img غير صالح: {img}")
                continue

            page_links.add(link)

            if link in existing_links:
                continue

            yield {
                'name': name,
                'img': img,
                'link': link,
                'category': category,
            }

        # إيقاف مبكر
        if page_links and all(link in existing_links for link in page_links):
            logger.info(f"⏹️ إيقاف مبكر: {category} @ {response.url}")
            return

        next_page = response.css('.pagination a.page-link::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
