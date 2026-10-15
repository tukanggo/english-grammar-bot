import os
import datetime
import json
import time
from google import genai
from google.genai.errors import ServerError

def generate_daily_grammar():
    print("开始执行语法生成任务 (JSON 格式)...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("错误: 未检测到 GEMINI_API_KEY")
        return

    client = genai.Client(api_key=api_key)
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    prompt = """
    你是一位优秀的小学英语高级教师。请为新加坡或国际学校 4-5 年级（Primary 4-5）学生设计 30 道英语语法单选题。
    
    你必须严格只输出一个合法的 JSON 对象（不要包裹在 markdown 代码块中，直接输出纯 JSON 字符串），格式如下：
    {
      "date": "2026-10-14",
      "topic": "综合语法专项练习",
      "questions": [
        {
          "id": 1,
          "question": "题目文本...",
          "options": {
            "A": "选项A内容",
            "B": "选项B内容",
            "C": "选项C内容",
            "D": "选项D内容"
          },
          "answer": "B",
          "explanation": "详细的中文/英文解析..."
        }
      ]
    }
    确保必须刚好有 30 道题，且 JSON 格式必须完全正确。
    """

    # 设置最多重试 3 次，应对 503 拥堵
    max_retries = 3
    response = None
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"正在请求 Gemini API (尝试第 {attempt} 次)...")
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt
            )
            break # 成功则跳出循环
        except ServerError as e:
            print(f"遇到服务器拥堵 (503)，等待 5 秒后重试... (错误: {e})")
            if attempt == max_retries:
                raise e
            time.sleep(5) # 等待 5 秒再试

    raw_text = response.text.strip()
    
    # 清理可能带有的 markdown 符号
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    try:
        data = json.loads(raw_text)
    except Exception as e:
        print(f"JSON 解析失败，保存原始内容。错误: {e}")
        data = {"raw_content": raw_text}

    folder_name = "docs"
    os.makedirs(folder_name, exist_ok=True)
    
    file_path = f"{folder_name}/latest.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"题目数据已成功保存至: {file_path}")

if __name__ == "__main__":
    generate_daily_grammar()
