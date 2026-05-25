import scrapy
import logging

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

    def parse(self, response):
        # استخراج الفئة من URL
        try:
            category = response.url.split('/')[3]
        except IndexError:
            logger.warning(f"⚠️ تعذر استخراج الفئة من: {response.url}")
            return

        # الحصول على الروابط الموجودة من الـ pipeline
        existing_links = set()
        if hasattr(self, 'pipeline') and hasattr(self.pipeline, 'existing_links'):
            existing_links = self.pipeline.existing_links.get(category, set())

        # استخراج عناصر الصفحة
        post_divs = response.css('#postList .postDiv')
        page_links = set()
        new_found = False

        for post in post_divs:
            anchor = post.css('a')
            if not anchor:
                continue

            img_tag = anchor.css('img')
            if not img_tag:
                continue

            # استخراج الاسم
            name = img_tag.attrib.get('alt', '').strip()
            if not name:
                name = anchor.css('.h1::text').get('').strip()

            # استخراج الصورة (data-src أولاً ثم src)
            img = img_tag.attrib.get('data-src', '') or img_tag.attrib.get('src', '')

            # استخراج الرابط
            link = anchor.attrib.get('href', '')

            if not name or not img or not link:
                continue

            if not img.startswith('http'):
                logger.warning(f"⚠️ img غير صالح (لا يبدأ بـ http): {img}")
                continue

            page_links.add(link)

            # إذا كان الرابط موجوداً مسبقاً، تجاوزه
            if link in existing_links:
                continue

            new_found = True
            yield {
                'name': name,
                'img': img,
                'link': link,
                'category': category,
            }

        # منطق الإيقاف المبكر: إذا كانت كل روابط الصفحة موجودة مسبقاً، لا تتابع
        if page_links and all(link in existing_links for link in page_links):
            logger.info(f"⏹️ الإيقاف المبكر: {category} @ {response.url} — كل الروابط موجودة")
            return

        # تتبع الصفحة التالية
        next_page = response.css('.pagination a.page-link::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
