import os
import datetime
import json
import time
from google import genai
from google.genai.errors import ServerError

def generate_daily_grammar():
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"开始执行 {today} 的语法生成任务...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("错误: 未检测到 GEMINI_API_KEY")
        return

    client = genai.Client(api_key=api_key)
    
    # 核心改进：把日期放进提示词，并强制要求 AI 每天更换不同的语法专项主题
    prompt = f"""
    今天是 {today}。你是一位优秀的国际学校小学英语高级教师。
    请为 4-5 年级（Primary 4-5）学生设计一套全新的、绝对不与往常重复的 30 道英语语法单选题。
    
    【核心要求】：
    1. 今天的日期是 {today}，请根据这个日期随机挑选一个**特定的、深入的语法专项主题**（例如：今天可以专门考“动词不规则过去式与过去分词”，明天考“介词与时间地点的搭配”，后天考“情态动词”等，严禁每次都出大杂烩）。
    2. 必须严格只输出一个合法的 JSON 对象（不要包裹在 markdown 代码块中，直接输出纯 JSON 字符串），格式如下：
    {{
      "date": "{today}",
      "topic": "今天具体的语法专项名称（例如：专项练习 - 过去完成时）",
      "questions": [
        {{
          "id": 1,
          "question": "题目文本...",
          "options": {{
            "A": "选项A",
            "B": "选项B",
            "C": "选项C",
            "D": "选项D"
          }},
          "answer": "B",
          "explanation": "详细解析..."
        }}
      ]
    }}
    3. 确保必须刚好有 30 道题，且 JSON 格式必须完全正确。
    """

    max_retries = 3
    response = None
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"正在请求 Gemini API 生成新题 (尝试第 {attempt} 次)...")
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt
            )
            break
        except ServerError as e:
            print(f"遇到服务器拥堵 (503)，等待 5 秒后重试... (错误: {e})")
            if attempt == max_retries:
                raise e
            time.sleep(5)

    raw_text = response.text.strip()
    
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
        
    print(f"新鲜出炉的题目数据已成功保存至: {file_path}")

if __name__ == "__main__":
    generate_daily_grammar()
