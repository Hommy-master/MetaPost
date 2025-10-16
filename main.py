import asyncio
import random
from playwright.async_api import async_playwright


def generate_random_fingerprint():
    """生成随机浏览器指纹信息"""
    # 随机选择操作系统和对应的User-Agent
    os_options = [
        {
            "name": "Windows",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.{} Safari/537.36",
            "is_mobile": False,
            "has_touch": False
        },
        {
            "name": "macOS",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.{} Safari/537.36",
            "is_mobile": False,
            "has_touch": False
        },
        {
            "name": "Linux",
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.{} Safari/537.36",
            "is_mobile": False,
            "has_touch": False
        },
        {
            "name": "Android",
            "user_agent": "Mozilla/5.0 (Linux; Android {}; {}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.{} Mobile Safari/537.36",
            "is_mobile": True,
            "has_touch": True
        }
    ]
    
    selected_os = random.choice(os_options)
    
    # 随机生成Chrome版本号
    major_version = random.randint(80, 120)
    minor_version = random.randint(1000, 9999)
    build_version = random.randint(10, 99)
    
    # 随机生成Android版本和设备型号（仅对Android）
    android_version = f"{random.randint(8, 13)}.{random.randint(0, 9)}"
    android_device = random.choice(["SM-G960U", "Pixel 4", "ONEPLUS A6013", "Moto G7"])
    
    # 构造User-Agent
    if selected_os["name"] == "Android":
        user_agent = selected_os["user_agent"].format(android_version, android_device, major_version, minor_version, build_version)
    else:
        user_agent = selected_os["user_agent"].format(major_version, minor_version, build_version)
    
    # 随机屏幕分辨率
    resolutions = [
        (1920, 1080)
    ]
    width, height = random.choice(resolutions)
    
    # 随机设备缩放因子
    device_scale_factors = [1, 1.25, 1.5, 1.75, 2]
    device_scale_factor = random.choice(device_scale_factors)
    
    # 随机语言和地区
    locales = ["zh-CN", "en-US", "en-GB", "ja-JP", "ko-KR", "fr-FR", "de-DE"]
    locale = random.choice(locales)
    
    # 随机时区
    timezones = ["Asia/Shanghai", "America/New_York", "Europe/London", "Asia/Tokyo", "Europe/Paris", "America/Los_Angeles"]
    timezone_id = random.choice(timezones)
    
    return {
        "user_agent": user_agent,
        "viewport": {"width": width, "height": height},
        "device_scale_factor": device_scale_factor,
        "is_mobile": selected_os["is_mobile"],
        "has_touch": selected_os["has_touch"],
        "locale": locale,
        "timezone_id": timezone_id,
        "os": selected_os["name"]
    }


async def baidu_search():
    async with async_playwright() as p:
        # 启动浏览器（默认使用Chromium，headless=False表示显示浏览器界面）
        browser = await p.chromium.launch(headless=False)
        
        # 生成随机浏览器指纹信息
        fingerprint = generate_random_fingerprint()
        print(f"使用随机指纹信息:")
        print(f"  操作系统: {fingerprint['os']}")
        print(f"  User-Agent: {fingerprint['user_agent']}")
        print(f"  屏幕分辨率: {fingerprint['viewport']['width']}x{fingerprint['viewport']['height']}")
        print(f"  设备缩放因子: {fingerprint['device_scale_factor']}")
        print(f"  移动端: {fingerprint['is_mobile']}")
        print(f"  触摸支持: {fingerprint['has_touch']}")
        print(f"  语言: {fingerprint['locale']}")
        print(f"  时区: {fingerprint['timezone_id']}")
        
        # 创建带有随机指纹信息的浏览器上下文
        context = await browser.new_context(
            user_agent=fingerprint['user_agent'],
            viewport=fingerprint['viewport'],
            device_scale_factor=fingerprint['device_scale_factor'],
            is_mobile=fingerprint['is_mobile'],
            has_touch=fingerprint['has_touch'],
            locale=fingerprint['locale'],
            timezone_id=fingerprint['timezone_id']
        )
        page = await context.new_page()
        
        try:
            # 导航到百度首页
            await page.goto('https://www.baidu.com')
            
            # 等待页面加载完成
            await page.wait_for_load_state('networkidle')
            
            # 添加调试信息，查看当前URL和页面标题
            print(f"当前URL: {page.url}")
            print(f"页面标题: {await page.title()}")
            
            # 定位搜索框并输入关键词
            print("尝试定位搜索框...")
            search_box = await page.query_selector('#kw')
            if search_box:
                print("搜索框定位成功")
                await search_box.type('Playwright自动化测试')
                # 尝试直接按Enter键搜索，避免点击按钮
                await search_box.press('Enter')
                print("已按Enter键提交搜索")
            else:
                print("搜索框定位失败，尝试使用其他选择器")
                # 尝试使用其他选择器
                search_box = await page.query_selector('[name="wd"]')
                if search_box:
                    print("使用备用选择器定位搜索框成功")
                    await search_box.type('Playwright自动化测试')
                    # 尝试直接按Enter键搜索
                    await search_box.press('Enter')
                    print("已按Enter键提交搜索")
                else:
                    print("无法定位搜索框")
                    return
            
            # 等待搜索结果页面加载
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)  # 等待2秒确保结果稳定
            
            # 保存结果页面截图
            await page.screenshot(path='baidu_results.png')
            print("搜索完成！已保存搜索结果页面截图")
            
        except Exception as e:
            print(f"执行过程中出现错误: {e}")
            # 发生错误时也保存截图
            try:
                await page.screenshot(path='error_screenshot.png')
                print("已保存错误页面截图")
            except:
                pass
        finally:
            # 等待一会儿以便观察结果，然后关闭浏览器
            await asyncio.sleep(3)
            await browser.close()

if __name__ == "__main__":
    # 运行异步函数
    asyncio.run(baidu_search())