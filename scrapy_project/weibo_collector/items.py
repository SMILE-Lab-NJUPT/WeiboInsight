import scrapy

class WeiboPostItem(scrapy.Item):
    text = scrapy.Field()         # 帖子文本内容
    author = scrapy.Field()       # 发布者昵称
    date = scrapy.Field()         # 发布时间
    metrics = scrapy.Field()      # 点赞/评论/转发数，字典形式
    image_urls = scrapy.Field()   # 图片下载 URL 列表
    images = scrapy.Field()       # ImagesPipeline 处理结果
    segmented_text = scrapy.Field() # 新增：分词后的文本内容 (列表)
    post_url = scrapy.Field()       # 新增：帖子原始链接，方便追溯