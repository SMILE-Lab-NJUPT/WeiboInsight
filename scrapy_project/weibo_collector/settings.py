BOT_NAME = 'weibo_collector'

SPIDER_MODULES = ['weibo_collector.spiders']
NEWSPIDER_MODULE = 'weibo_collector.spiders'

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36" # 可以设置一个默认的
USER_AGENT_LIST = [ 
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

ROBOTSTXT_OBEY = False 
CONCURRENT_REQUESTS = 8 
DOWNLOAD_DELAY = 3 
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 8
COOKIES_ENABLED = False 
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
  'Connection': 'keep-alive',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'none',
  'Sec-Fetch-User': '?1',
  'Upgrade-Insecure-Requests': '1',
}
DOWNLOADER_MIDDLEWARES = {
    'weibo_collector.middlewares.UAMiddleware': 400,
    'scrapy.downloadermiddlewares.offsite.OffsiteMiddleware': None,
}
ITEM_PIPELINES = {
   'weibo_collector.pipelines.DataCleaningPipeline': 300, 
   'weibo_collector.pipelines.WeiboImagesPipeline': 1,
   'weibo_collector.pipelines.MongoPipeline': 800,
}
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False,
    "args": [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled"
    ],
    "slow_mo": 500
}
PLAYWRIGHT_DEFAULT_CONTEXT_ARGS = {
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36", # 确保这个User-Agent与您导出Cookie的浏览器一致
    "locale": "zh-CN",
    "timezone_id": "Asia/Shanghai",
}
MONGO_URI = 'mongodb://localhost:27017'
MONGO_DATABASE = 'weibo_data'

PROXY_LIST = [
    # 'http://user:pass@host1:port',
    # 'http://user:pass@host2:port',
    # 'http://127.0.0.1:7890', # 本地代理示例 (例如 Clash, V2RayN)
    # 以下为示例公共代理，非常不稳定，不建议生产使用
    # 'http://162.214.165.203:80',
    # 'http://5.161.103.41:88',
]
LOG_LEVEL = 'INFO'