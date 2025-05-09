from playwright.sync_api import sync_playwright
import time
AUTH_STATE_PATH = r"C:\Users\17193\Desktop\spider\scrapy_project\weibo_collector\spiders\weibo_auth_state.json" # 请修改为您的实际期望路径

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36" # 使用您常用的User-Agent
VIEWPORT = {"width": 1920, "height": 1080}
LOCALE = "zh-CN"
TIMEZONE_ID = "Asia/Shanghai"

def save_weibo_auth_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport=VIEWPORT,
            locale=LOCALE,
            timezone_id=TIMEZONE_ID,
        )
        page = context.new_page()

        print("正在导航到微博登录页面 (m.weibo.cn)...")
        page.goto("https://m.weibo.cn/", wait_until="networkidle")
        print("请在弹出的浏览器窗口中手动登录微博。")
        print(f"登录成功后，这个脚本会自动检测并保存会话状态到: {AUTH_STATE_PATH}")
        print("如果您长时间未登录，脚本可能会超时。")

        try:
            page.wait_for_selector("div.nav-main a[href*='/profile/']", timeout=60 * 1000) # 等待“我”的按钮，超时5分钟


            print("检测到登录成功迹象！正在保存会话状态...")
            context.storage_state(path=AUTH_STATE_PATH)
            print(f"会话状态已成功保存到: {AUTH_STATE_PATH}")
            print("您可以关闭浏览器窗口了。")

        except Exception as e:
            print(f"错误：未能自动检测到登录成功状态或发生超时: {e}")
            print("请确保您已在浏览器中成功登录。如果已登录，脚本可能未能正确检测到。")
            print("您可以尝试在登录后，手动修改此脚本，直接执行 context.storage_state() 保存。")
            context.storage_state(path=AUTH_STATE_PATH)
        time.sleep(10)
        browser.close()

if __name__ == "__main__":
    save_weibo_auth_state()