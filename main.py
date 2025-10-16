import asyncio
import random
import os
import json
from playwright.async_api import async_playwright
from urllib.parse import urljoin


class RC4Cipher:
    """RC4加密解密类"""
    
    def __init__(self, key):
        self.key = key.encode('utf-8') if isinstance(key, str) else key
    
    def _keystream(self, key):
        """生成密钥流"""
        S = list(range(256))
        j = 0
        for i in range(256):
            j = (j + S[i] + key[i % len(key)]) % 256
            S[i], S[j] = S[j], S[i]
        i = j = 0
        while True:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            yield S[(S[i] + S[j]) % 256]
    
    def encrypt(self, data):
        """加密数据"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        keystream = self._keystream(self.key)
        encrypted = bytes([byte ^ next(keystream) for byte in data])
        return encrypted
    
    def decrypt(self, data):
        """解密数据"""
        keystream = self._keystream(self.key)
        decrypted = bytes([byte ^ next(keystream) for byte in data])
        return decrypted


class UserDataManager:
    """用户数据管理类"""
    
    def __init__(self, password="gogoshine"):
        self.cipher = RC4Cipher(password)
        self.data_dir = "user_data"
        self.session_file = os.path.join(self.data_dir, "user_session.dat")
        
        # 创建数据目录
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_user_data(self, fingerprint, cookies):
        """加密保存用户数据"""
        try:
            # 组合用户数据
            user_data = {
                "fingerprint": fingerprint,
                "cookies": cookies
            }
            
            # 转换为JSON字符串
            json_data = json.dumps(user_data, indent=2, ensure_ascii=False)
            
            # 加密数据
            encrypted_data = self.cipher.encrypt(json_data)
            
            # 保存到文件
            with open(self.session_file, 'wb') as f:
                f.write(encrypted_data)
            
            print(f"用户数据已加密保存到 {self.session_file}")
            return True
        except Exception as e:
            print(f"保存用户数据时出错: {e}")
            return False
    
    def load_user_data(self):
        """解密加载用户数据"""
        if not os.path.exists(self.session_file):
            print(f"用户数据文件 {self.session_file} 不存在")
            return None, None
        
        try:
            # 读取加密数据
            with open(self.session_file, 'rb') as f:
                encrypted_data = f.read()
            
            # 解密数据
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # 转换为字符串并解析JSON
            json_data = decrypted_data.decode('utf-8')
            user_data = json.loads(json_data)
            
            print(f"从 {self.session_file} 解密加载了用户数据")
            return user_data.get("fingerprint"), user_data.get("cookies")
        except Exception as e:
            print(f"加载用户数据时出错: {e}")
            return None, None


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
        (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
        (1600, 900), (2560, 1440), (3840, 2160), (1280, 720),
        (1680, 1050), (1280, 1024), (1920, 1200), (1024, 768)
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


async def doubao_image_generation():
    """访问豆包网站，支持用户手动登录并保存所有用户痕迹"""
    # 初始化用户数据管理器
    user_manager = UserDataManager()
    
    async with async_playwright() as p:
        # 启动浏览器（默认使用Chromium，headless=False表示显示浏览器界面）
        browser = await p.chromium.launch(headless=False)
        
        # 加载已保存的用户数据
        fingerprint, saved_cookies = user_manager.load_user_data()
        
        # 如果没有已保存的指纹信息，生成新的指纹
        if fingerprint is None:
            print("首次使用，正在生成随机浏览器指纹信息...")
            fingerprint = generate_random_fingerprint()
        else:
            print("加载已保存的浏览器指纹信息")
        
        # 显示当前使用的指纹信息
        print("使用浏览器指纹信息:")
        print(f"  操作系统: {fingerprint['os']}")
        print(f"  User-Agent: {fingerprint['user_agent']}")
        print(f"  屏幕分辨率: {fingerprint['viewport']['width']}x{fingerprint['viewport']['height']}")
        print(f"  设备缩放因子: {fingerprint['device_scale_factor']}")
        print(f"  移动端: {fingerprint['is_mobile']}")
        print(f"  触摸支持: {fingerprint['has_touch']}")
        print(f"  语言: {fingerprint['locale']}")
        print(f"  时区: {fingerprint['timezone_id']}")
        
        # 创建带有指纹信息的浏览器上下文，直接设置最大化视口
        context = await browser.new_context(
            user_agent=fingerprint['user_agent'],
            viewport={"width": 1920, "height": 1080},  # 直接设置最大化视口
            device_scale_factor=fingerprint['device_scale_factor'],
            is_mobile=fingerprint['is_mobile'],
            has_touch=fingerprint['has_touch'],
            locale=fingerprint['locale'],
            timezone_id=fingerprint['timezone_id']
        )
        
        # 如果有已保存的cookies，则加载
        if saved_cookies:
            await context.add_cookies(saved_cookies)
            print("已加载保存的用户登录信息")
        else:
            print("未找到已保存的用户登录信息")
        
        page = await context.new_page()
        
        try:
            # 导航到豆包网站
            print("正在访问豆包网站...")
            await page.goto('https://www.doubao.com/chat/')
            
            # 等待页面加载完成
            await page.wait_for_load_state('networkidle')
            
            # 显示当前页面信息
            print(f"当前URL: {page.url}")
            print(f"页面标题: {await page.title()}")
            
            # 等待用户操作
            print("请在浏览器中进行所需操作（如登录、生成图片等）...")
            print("完成所有操作后，请手动关闭浏览器窗口，程序将自动保存所有用户痕迹")
            
            # 一直等待用户关闭浏览器
            try:
                # 持续检查页面状态，直到浏览器被关闭
                while True:
                    try:
                        # 尝试获取页面标题来检查页面是否仍然存在
                        await page.title()
                        # 页面仍然存在，继续等待
                        await asyncio.sleep(5)  # 每5秒检查一次
                    except:
                        # 页面已关闭，跳出循环
                        print("检测到浏览器已关闭")
                        break
            except Exception as e:
                print(f"等待过程中出现异常: {e}")
            
        except Exception as e:
            print(f"执行过程中出现错误: {e}")
        finally:
            # 保存所有用户痕迹
            print("正在保存用户痕迹...")
            
            try:
                # 获取当前会话的cookies
                current_cookies = await context.cookies()
                
                # 加密保存指纹信息和cookies
                if user_manager.save_user_data(fingerprint, current_cookies):
                    print("所有用户痕迹已加密保存，下次启动时将自动加载")
                else:
                    print("保存用户痕迹失败")
            except Exception as e:
                print(f"保存用户数据时出错: {e}")
            
            # 关闭浏览器
            await browser.close()


if __name__ == "__main__":
    asyncio.run(doubao_image_generation())