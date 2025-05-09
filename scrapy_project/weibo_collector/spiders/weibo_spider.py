import scrapy
from scrapy_playwright.page import PageMethod
import json
import os
from urllib.parse import quote # 用于URL编码
from ..items import WeiboPostItem
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36" # 使用您常用的User-Agent


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    custom_settings = {
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
    }

    async def _get_json_from_page(self, page, keyword_for_debug):
        """尝试从页面内容中提取JSON"""
        try:
            content = await page.content()
            try:
                json_data = json.loads(content)
                self.logger.info(f"关键词 '{keyword_for_debug}': 直接从页面内容解析 JSON 成功。")
                return json_data
            except json.JSONDecodeError:
                pre_tag_content = await page.query_selector('pre')
                if pre_tag_content:
                    json_text_from_pre = await pre_tag_content.inner_text()
                    try:
                        json_data = json.loads(json_text_from_pre)
                        self.logger.info(f"关键词 '{keyword_for_debug}': 从 <pre> 标签提取并解析 JSON 成功。")
                        return json_data
                    except json.JSONDecodeError as e_pre:
                        self.logger.error(f"关键词 '{keyword_for_debug}': 从 <pre> 标签提取内容后解析 JSON 失败: {e_pre}")
                        self.logger.debug(f"从 <pre> 提取的文本 (前500字符): {json_text_from_pre[:500]}")
                        return None

                self.logger.warning(f"关键词 '{keyword_for_debug}': 页面内容不是预期的 JSON 格式，也没有找到 <pre> 标签包裹的 JSON。")
                return None

        except Exception as e:
            self.logger.error(f"关键词 '{keyword_for_debug}': 从页面提取JSON时发生严重错误: {e}")
            return None

    def start_requests(self):
        keywords = ["#正能量#"]
        CONTAINERID_SEARCH_PREFIX = "100103type%3D61%26q%3D"
        API_BASE_URL = "https://m.weibo.cn/api/container/getIndex"
        storage_state_file_path = os.path.join(os.path.dirname(__file__), 'weibo_auth_state.json')
        playwright_context_args = {}
        if os.path.exists(storage_state_file_path):
            playwright_context_args['storage_state'] = storage_state_file_path
            self.logger.info(f"已配置使用会话状态文件: {storage_state_file_path}")
        else:
            self.logger.warning(f"会话状态文件 '{storage_state_file_path}' 未找到。爬虫将无法携带认证信息。")

        for keyword in keywords:
            keyword_url_encoded = quote(keyword)
            full_containerid = f"{CONTAINERID_SEARCH_PREFIX}{keyword_url_encoded}"
            api_url = f"{API_BASE_URL}?containerid={full_containerid}"
            self.logger.info(f"关键词 '{keyword}': 准备请求 API URL: {api_url}")
            meta = {
                'playwright': True,
                'playwright_include_page': True,
                'playwright_context_args': playwright_context_args.copy(),
                'playwright_page_methods': [
                    PageMethod('goto', api_url, kwargs={"wait_until": "networkidle", "timeout": 30000}),
                    PageMethod('wait_for_timeout', 2000),
                ],
                'playwright_headers': {
                    'User-Agent': USER_AGENT,
                    'Referer': 'https://m.weibo.cn/search',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json, text/plain, */*',
                },
                'keyword': keyword,
                'api_url': api_url
            }
            yield scrapy.Request(
                api_url,
                meta=meta,
                callback=self.parse_api_response,
                errback=self.errback_handle,
            )
async def parse_api_response(self, response):
    keyword = response.meta['keyword']
    api_url = response.meta['api_url']
    page = response.meta.get("playwright_page")

    self.logger.info(f"回调函数 parse_api_response - 关键词 '{keyword}', 请求URL: {api_url}")
    if not page or page.is_closed():
        self.logger.error(f"关键词 '{keyword}': 页面对象无效或已关闭 (parse_api_response)。")
        return
    current_url = page.url
    if "login.sina.com.cn" in current_url or "passport.weibo.com" in current_url:
        self.logger.error(f"关键词 '{keyword}': 请求API {api_url} 时被重定向到登录页: {current_url}。会话状态无效。")
        await page.close()
        return
    json_data = await self._get_json_from_page(page, keyword)

    if page and not page.is_closed():
        await page.close()

    if not json_data:
        self.logger.error(f"关键词 '{keyword}': 未能从API响应 {api_url} 中获取有效的 JSON 数据。")
        return
    self.logger.info(f"关键词 '{keyword}': 成功获取API响应JSON数据 (部分): {str(json_data)[:500]}...")

    cards = []
    if isinstance(json_data, dict) and json_data.get('ok') == 1:
        if 'cards' in json_data.get('data', {}):
            cards = json_data['data']['cards']
        elif 'cards' in json_data:
            cards = json_data['cards']
        else:
            self.logger.warning(f"关键词 '{keyword}': JSON响应中未找到 'cards' 字段。响应结构: {list(json_data.keys())}")
    else:
        self.logger.error(f"关键词 '{keyword}': API响应表明请求失败或格式不正确。ok: {json_data.get('ok') if isinstance(json_data, dict) else 'N/A'}, msg: {json_data.get('msg') if isinstance(json_data, dict) else 'N/A'}")
        return

    if not cards:
        self.logger.info(f"关键词 '{keyword}': API响应中没有找到任何卡片 (帖子)。")
        return

    for card_idx, card_group in enumerate(cards):
        actual_cards_in_group = []
        if isinstance(card_group, dict) and 'card_group' in card_group:
             actual_cards_in_group.extend(card_group.get('card_group', []))
        elif isinstance(card_group, dict): # 直接是card
             actual_cards_in_group.append(card_group)

        for card in actual_cards_in_group:
            card_type = card.get('card_type')
            if card_type == 9 or card_type == 11: 
                mblog = card.get('mblog')
                if not mblog:
                    self.logger.warning(f"关键词 '{keyword}', 卡片组 {card_idx+1}: card_type {card_type} 但缺少 mblog 字段。")
                    continue
                item = WeiboPostItem()
                item['text'] = mblog.get('text', '')

                user_info = mblog.get('user')
                if user_info:
                    item['author'] = user_info.get('screen_name', '')
                else:
                    item['author'] = '未知作者'

                item['date'] = mblog.get('created_at', '') 
                self.logger.info(f"关键词 '{keyword}', 卡片 {card_idx+1}: 提取到微博 - {item['text'][:30]}...")
                if item['text']:
                    yield item
    
async def parse_post_detail(self, response, post_url):
    page = response.meta.get("playwright_page")
    if page:
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(3000) 
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(1000)
            new_content = await page.content()
            response = response.replace(body=new_content)
        except Exception as e:
            self.logger.warning(f"在详情页 {response.url} Playwright 操作失败: {e}")
        finally:
            if page and not page.is_closed():
                await page.close()

    item = WeiboPostItem()
    item['post_url'] = post_url
    text_content_parts = response.css('div.WB_text ::text').getall() 
    full_text = "".join(text_content_parts).strip()
    if not full_text: 
        text_content_parts = response.css('div.detail_wbtext_wrap ::text').getall() 
        full_text = "".join(text_content_parts).strip()
    item['text'] = full_text
    author_name = response.css('div.WB_info a.W_f14::text').get()
    if not author_name:
            author_name = response.css('div.Feed_User_Nick a::text').get()
    item['author'] = author_name.strip() if author_name else "未知作者"
    date_str = response.css('div.WB_from a[suda-data*="time"]::text').get() 
    if not date_str:
        date_str = response.css('div.Frame_ λειτουργίες a.S_txt2::text').get()
    if not date_str:
        time_elements = response.xpath("//*[contains(text(),'发布于')]/following-sibling::span/text() | //*[contains(text(),'发布于')]/following-sibling::a/text()").getall()
        date_str = " ".join(time_elements).strip() if time_elements else "未知时间"
    item['date'] = date_str.strip()
    repost_count_raw = response.css('a[action-type="feed_list_forward"] span em::text').get()
    if not repost_count_raw: 
        repost_count_raw = response.xpath("//*[contains(text(),'转发')]/ancestor::a/span/em/text() | //*[contains(text(),'转发')]/strong/text()").get()
    comment_count_raw = response.css('a[action-type="feed_list_comment"] span em::text').get()
    if not comment_count_raw:
        comment_count_raw = response.xpath("//*[contains(text(),'评论')]/ancestor::a/span/em/text() | //*[contains(text(),'评论')]/strong/text()").get()
    like_count_raw = response.css('a[action-type="feed_list_like"] span em::text').get()
    if not like_count_raw:
            like_count_raw = response.css('button.woo-like- meisjes span.woo-like-count::text').get()
    if not like_count_raw:
        like_count_raw = response.xpath("//*[contains(text(),'赞')]/ancestor::button/span/text() | //*[contains(text(),'赞')]/ancestor::a/span/em/text() | //*[contains(text(),'赞')]/strong/text()").get()


    def parse_count(count_str):
        if not count_str: return 0
        if isinstance(count_str, str):
            if '万' in count_str:
                return int(float(count_str.replace('万', '')) * 10000)
            if '亿' in count_str:
                return int(float(count_str.replace('亿', '')) * 100000000)
            if count_str.isdigit():
                return int(count_str)
        return 0 # 默认或无法解析时

    item['metrics'] = {
        'reposts': parse_count(repost_count_raw),
        'comments': parse_count(comment_count_raw),
        'likes': parse_count(like_count_raw),
    }
    image_urls = []
    # 查找包含图片的 div 容器
    media_boxes = response.css('div.media_box ul li img::attr(src)').getall() # 多图情况
    if not media_boxes:
            media_boxes = response.css('div.WB_pic img::attr(src)').getall() # 单图情况

    for img_src in media_boxes:
        if img_src:
            # 有些图片链接可能是 // 开头，需要补全协议
            if img_src.startswith('//'):
                image_urls.append('http:' + img_src)
            else:
                image_urls.append(img_src)
    item['image_urls'] = image_urls

    self.logger.info(f"成功解析帖子: {item.get('author')}, 赞: {item['metrics']['likes']}")
    yield item

async def errback_handle(self, failure):
    self.logger.error(f"请求失败: {failure.request.url}, 错误类型: {failure.type}, 错误信息: {failure.value}")
    page = failure.request.meta.get("playwright_page")
    if page and not page.is_closed(): # 如果错误发生时page还存在，尝试关闭
        try:
            await page.close()
        except Exception as e:
            self.logger.warning(f"关闭Playwright页面时出错 (errback): {e}")