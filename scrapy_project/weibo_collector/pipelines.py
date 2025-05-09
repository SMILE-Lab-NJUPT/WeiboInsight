import re
import pymongo
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from datetime import datetime
import jieba
STOP_WORDS = set([
    "的", "了", "我", "你", "他", "她", "它", "们", "是", "有", "在", "也", "都",
    "不", "就", "吧", "吗", "呢", "啊", "哦", "嗯", "嘿", "哈", "啦", "咯", "啧",
    "唰", "哼", "吁", "唉", "呀", "おい", "この", "あの", "その", "どの", "ここ",
    "そこ", "あそこ", "どこ", "これ", "それ", "あれ", "どれ", "!", "\"", "#",
    "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<",
    "=", ">", "?", "@", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~", "、",
    "。", "〈", "〉", "《", "》", "「", "」", "『", "』", "【", "】", "〔", "〕",
    "〖", "〗", "〘", "〙", "〚", "〛", "〜", "〝", "〞", "〟", "–", "—", "‘", "’",
    "“", "”", "…", "❞", "❝", " specialty", " ", "　"
])
class DataCleaningPipeline:
    def process_item(self, item, spider):
        if 'text' in item and item['text']:
            text = re.sub(r'<[^>]+>', '', item['text'])
            text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', text)
            text = text.strip().lower()
            seg_list = jieba.cut(text, cut_all=False)
            processed_words = [word for word in seg_list if word not in STOP_WORDS and len(word.strip()) > 0]
            item['segmented_text'] = processed_words
            item['text'] = text
        else:
            item['segmented_text'] = []
            item['text'] = ""

        if 'date' in item and item['date']:
            raw_date_str = item['date']
            parsed_date = None
            try:
                if "今天" in raw_date_str:
                    time_str = raw_date_str.split(" ")[1]
                    parsed_date = datetime.strptime(f"{datetime.now().strftime('%Y-%m-%d')} {time_str}", '%Y-%m-%d %H:%M')
                elif "分钟前" in raw_date_str:
                    minutes_ago = int(re.findall(r'(\d+)分钟前', raw_date_str)[0])
                    parsed_date = datetime.now() - datetime.timedelta(minutes=minutes_ago)
                elif "小时前" in raw_date_str:
                    hours_ago = int(re.findall(r'(\d+)小时前', raw_date_str)[0])
                    parsed_date = datetime.now() - datetime.timedelta(hours=hours_ago)
                elif "月" in raw_date_str and "日" in raw_date_str and ":" in raw_date_str: 
                    current_year = datetime.now().year
                    parsed_date = datetime.strptime(f"{current_year}年{raw_date_str}", '%Y年%m月%d日 %H:%M')
                elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', raw_date_str):
                    parsed_date = datetime.strptime(raw_date_str, '%Y-%m-%d %H:%M:%S')
                elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', raw_date_str):
                    parsed_date = datetime.strptime(raw_date_str, '%Y-%m-%d %H:%M')
                item['date'] = parsed_date.isoformat() if parsed_date else raw_date_str 
            except Exception as e:
                spider.logger.warning(f"日期解析失败: {raw_date_str}, 错误: {e}")
                item['date'] = raw_date_str
        else:
            item['date'] = None

        return item

class WeiboImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if 'image_urls' in item:
            for image_url in item.get('image_urls', []):
                if image_url.startswith('//'):
                    image_url = 'http:' + image_url
                yield Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if image_paths:
            item['images'] = image_paths
        return item

class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        spider.logger.info("MongoDB connection opened.")

    def close_spider(self, spider):
        if self.client:
            self.client.close()
            spider.logger.info("MongoDB connection closed.")

    def process_item(self, item, spider):
        try:
            if 'post_url' in item and item['post_url']:
                self.db.posts.update_one(
                    {'post_url': item['post_url']},
                    {'$set': dict(item)},
                    upsert=True
                )
                spider.logger.debug(f"Upserted item to MongoDB with post_url: {item['post_url']}")
            else:
                self.db.posts.insert_one(dict(item))
                spider.logger.debug("Inserted item to MongoDB (no post_url).")
        except Exception as e:
            spider.logger.error(f"Error inserting item to MongoDB: {e}")
        return item