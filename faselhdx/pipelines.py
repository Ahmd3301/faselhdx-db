import json
import os
import logging

logger = logging.getLogger(__name__)


class JsonWriterPipeline:
    def __init__(self):
        self.categories = ['movies', 'hindi', 'asian-movies', 'anime-movies',
                           'series', 'asian-series', 'tvshows', 'anime']
        self.old_items = {}
        self.new_items = {}
        self.existing_links = {}

    def open_spider(self, spider):
        for category in self.categories:
            filename = f"{category}.json"
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        self.old_items[category] = data
                        self.existing_links[category] = {item['link'] for item in data if 'link' in item}
                        logger.info(f"📂 {filename}: {len(data)} عناصر موجودة")
                    else:
                        logger.warning(f"⚠️ {filename}: ليس مصفوفة، يبدأ من جديد")
                        self.old_items[category] = []
                        self.existing_links[category] = set()
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"⚠️ {filename} تالف أو غير قابل للقراءة ({e})، يبدأ من جديد")
                    self.old_items[category] = []
                    self.existing_links[category] = set()
            else:
                self.old_items[category] = []
                self.existing_links[category] = set()
            self.new_items[category] = []

        spider.pipeline = self

    def process_item(self, item, spider):
        category = item.get('category')
        if not category:
            logger.warning(f"⚠️ عنصر بدون category: {item}")
            return item

        link = item.get('link', '')
        if link and link not in self.existing_links[category]:
            self.new_items[category].append(dict(item))
            self.existing_links[category].add(link)

        return item

    def close_spider(self, spider):
        for category in self.categories:
            final_list = self.new_items[category] + self.old_items[category]

            # احذف حقل category من كل عنصر
            for item in final_list:
                item.pop('category', None)

            filename = f"{category}.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(final_list, f, ensure_ascii=False, indent=2)
                logger.info(f"✅ {filename}: {len(self.new_items[category])} جديد + {len(self.old_items[category])} قديم")
            except (IOError, OSError) as e:
                logger.error(f"❌ خطأ في كتابة {filename}: {e}")
                tmp_filename = f"{filename}.tmp"
                try:
                    with open(tmp_filename, 'w', encoding='utf-8') as f:
                        json.dump(final_list, f, ensure_ascii=False, indent=2)
                    logger.info(f"✅ كُتب الملف المؤقت: {tmp_filename}")
                except Exception as e2:
                    logger.error(f"❌ فشل كتابة الملف المؤقت أيضاً: {e2}")
