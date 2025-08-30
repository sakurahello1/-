import requests
import json
import time
import argparse
from datetime import datetime

# 配置信息 - 请替换为你的实际API密钥
API_KEY = "你的阿里千问API密钥"
API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

# 支持的笑话风格
SUPPORTED_STYLES = {
    "pun": "冷笑话",
    "funny": "搞笑段子",
    "sarcastic": "讽刺幽默",
    "absurd": "荒诞恶搞",
    "kids": "儿童笑话"
}


class JokeGenerator:
    def __init__(self, api_key=API_KEY):
        self.api_key = api_key
        self.session = requests.Session()
        self.saved_jokes = []
        self.load_saved_jokes()

    def load_saved_jokes(self):
        """从文件加载已保存的笑话"""
        try:
            with open("saved_jokes.json", "r", encoding="utf-8") as f:
                self.saved_jokes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.saved_jokes = []

    def save_jokes(self):
        """保存笑话到文件"""
        with open("saved_jokes.json", "w", encoding="utf-8") as f:
            json.dump(self.saved_jokes, f, ensure_ascii=False, indent=2)

    def generate_joke(self, keyword, style="pun"):
        """调用阿里千问API生成笑话"""
        if style not in SUPPORTED_STYLES:
            raise ValueError(f"不支持的笑话风格，请选择: {', '.join(SUPPORTED_STYLES.keys())}")

        # 构建提示词
        style_name = SUPPORTED_STYLES[style]
        prompt = f"""请生成一个关于"{keyword}"的{style_name}。
要求：
1. 内容幽默有趣，符合{style_name}的特点
2. 语言简洁明了，容易理解
3. 避免使用不适当或冒犯性的内容
4. 长度适中，不要过长"""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "qwen-plus",  # 使用阿里千问的模型
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "temperature": 0.8,  # 控制随机性，值越高越随机
                "top_p": 0.8,
                "max_tokens": 200  # 限制生成文本长度
            }
        }

        try:
            print(f"正在生成关于'{keyword}'的{style_name}...")
            response = self.session.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            if "output" in result and "text" in result["output"]:
                joke_text = result["output"]["text"].strip()
                return {
                    "text": joke_text,
                    "keyword": keyword,
                    "style": style,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                print("API返回格式异常")
                return None

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {str(e)}")
            return None

    def save_joke(self, joke):
        """保存笑话到收藏列表"""
        if joke and "text" in joke:
            self.saved_jokes.append(joke)
            self.save_jokes()
            return True
        return False

    def get_saved_jokes(self):
        """获取所有收藏的笑话"""
        return self.saved_jokes

    def rate_joke(self, joke, rating):
        """为笑话评分，用于后续优化"""
        # 实际应用中可以根据评分调整生成策略
        if joke and "text" in joke:
            joke["rating"] = rating
            print(f"已记录评分: {'👍' if rating > 0 else '👎'}")
            return True
        return False


def main():
    parser = argparse.ArgumentParser(description="智能笑话生成器")
    parser.add_argument("--keyword", help="笑话关键词", default="程序员")
    parser.add_argument("--style", help="笑话风格", default="pun")
    args = parser.parse_args()

    # 初始化生成器
    generator = JokeGenerator()

    # 生成笑话
    joke = generator.generate_joke(args.keyword, args.style)

    if joke:
        print("\n生成的笑话:")
        print("=" * 50)
        print(joke["text"])
        print("=" * 50)

        # 交互选项
        while True:
            print("\n请选择操作:")
            print("1. 收藏这个笑话")
            print("2. 评分 (好笑/一般)")
            print("3. 再生成一个")
            print("4. 查看收藏的笑话")
            print("5. 退出")

            choice = input("请输入选项 (1-5): ")

            if choice == "1":
                if generator.save_joke(joke):
                    print("已成功收藏笑话!")
                break
            elif choice == "2":
                rate = input("这个笑话好笑吗? (1=好笑, 0=一般): ")
                generator.rate_joke(joke, 1 if rate == "1" else 0)
                break
            elif choice == "3":
                new_keyword = input("请输入新的关键词 (回车使用相同关键词): ") or args.keyword
                new_style = input(f"请输入笑话风格 ({', '.join(SUPPORTED_STYLES.keys())}): ") or args.style
                joke = generator.generate_joke(new_keyword, new_style)
                if joke:
                    print("\n生成的新笑话:")
                    print("=" * 50)
                    print(joke["text"])
                    print("=" * 50)
            elif choice == "4":
                saved = generator.get_saved_jokes()
                if saved:
                    print("\n收藏的笑话:")
                    print("=" * 50)
                    for i, j in enumerate(saved, 1):
                        print(f"{i}. {j['text']}")
                        print(f"   关键词: {j['keyword']}, 风格: {SUPPORTED_STYLES[j['style']]}")
                        print(f"   保存时间: {j['timestamp']}\n")
                    print("=" * 50)
                else:
                    print("还没有收藏任何笑话哦!")
            elif choice == "5":
                print("谢谢使用，再见!")
                break
            else:
                print("无效的选项，请重试")


if __name__ == "__main__":
    main()
