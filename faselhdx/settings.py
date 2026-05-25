BOT_NAME = 'faselhdx'
SPIDER_MODULES = ['faselhdx.spiders']
NEWSPIDER_MODULE = 'faselhdx.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

ROBOTSTXT_OBEY = False
TELNETCONSOLE_ENABLED = False
LOG_LEVEL = 'INFO'

ITEM_PIPELINES = {
    'faselhdx.pipelines.JsonWriterPipeline': 1,
}
