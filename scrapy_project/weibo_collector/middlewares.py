import random, time
from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from twocaptcha import TwoCaptcha
import undetected_chromedriver as uc  # :contentReference[oaicite:5]{index=5}

class ProxyMiddleware:
    def __init__(self, proxy_list, proxy_enabled):
        self.proxies = proxy_list
        self.proxy_enabled = proxy_enabled 

    @classmethod
    def from_crawler(cls, crawler):
        proxy_list = crawler.settings.getlist('PROXY_LIST')
        proxy_enabled = crawler.settings.getbool('PROXY_ENABLED', True) # 从settings读取是否启用代理, 默认True
        #     raise NotConfigured("ProxyMiddleware disabled: PROXY_ENABLED is false or PROXY_LIST is not set.")
        return cls(proxy_list, proxy_enabled)

    def process_request(self, request, spider):
        if self.proxy_enabled and self.proxies:
            proxy = random.choice(self.proxies)
            request.meta['proxy'] = proxy
            spider.logger.debug(f"正在使用代理: {proxy} 发送请求 {request.url}")
        elif self.proxy_enabled and not self.proxies:
            spider.logger.warning(f"代理功能已启用 (PROXY_ENABLED=True)，但 PROXY_LIST 为空。请求将不通过代理发送: {request.url}")
        
class UAMiddleware:
    def __init__(self, uas):
        self.uas = uas

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('USER_AGENT_LIST'))

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.uas))

class CaptchaMiddleware:
    def __init__(self, api_key):
        self.solver = TwoCaptcha(api_key)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('TWO_CAPTCHA_KEY'))

    def process_response(self, request, response, spider):
        if b'captcha' in response.body.lower():
            token = self.solver.recaptcha(sitekey='SITEKEY', url=request.url)['code']
            form_data = {'g-recaptcha-response': token}
            return request.replace(method='POST', body=form_data)
        return response
