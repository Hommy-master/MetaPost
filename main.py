import asyncio
from playwright.async_api import async_playwright


async def baidu_search():
    async with async_playwright() as p:
        # 启动浏览器（默认使用Chromium，headless=False表示显示浏览器界面）
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
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
