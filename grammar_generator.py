import os
import datetime
import json
import time
from google import genai
from google.genai.errors import ServerError, ClientError

def generate_daily_grammar():
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"开始执行 {today} 的语法生成与教学任务...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("错误: 未检测到 GEMINI_API_KEY")
        return

    client = genai.Client(api_key=api_key)
    
    # 💡 注意：f-string 里面的 JSON 大括号必须写成双大括号 {{ 和 }}
    prompt = f"""
    今天是 {today}。你是一位优秀的国际学校小学英语高级教师。
    请为 4-5 年级（Primary 4-5）学生设计一套全新的、绝对不与往常重复的 20 道英语语法单选题。
    
    【核心要求】：
    1. 今天的日期是 {today}，请根据这个日期随机挑选一个特定的、深入的语法专项主题（例如：一般过去时、介词搭配、情态动词等）。
    2. 【新增教学模块】：在生成题目之前，请先用通俗易懂、生动有趣、带例句的方式写一段“今日语法小课堂 (teaching_notes)”，用中文向小学生讲解这个语法的核心概念、用法和注意事项（控制在 3-5 句话内，带 1-2 个清晰的英文例句）。
    3. 必须严格只输出一个合法的 JSON 对象（不要包裹在 markdown 代码块中，直接输出纯 JSON 字符串），格式如下：
    {{
      "date": "{today}",
      "topic": "今天具体的语法专项名称",
      "teaching_notes": "这里是今日语法小课堂的讲解文本与例句...",
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
    4. 确保 JSON 格式必须完全正确，绝对不能出现截断。
    """

    max_retries = 3
    response = None
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"正在请求 Gemini API 生成教学内容与新题 (尝试第 {attempt} 次)...")
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            break
        except (ServerError, ClientError) as e:
            print(f"遇到 API 限制或服务器拥堵，等待 30 秒后重试... (错误: {e})")
            if attempt == max_retries:
                print("❌ 达到最大重试次数，准备启用降级兜底数据...")
                raise e
            time.sleep(30)

    if not response:
        return

    raw_text = response.text.strip()
    
    # 清洗 Markdown 标记
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    try:
        data = json.loads(raw_text)
    except Exception as e:
        print(f"JSON 解析失败，尝试保存原始内容。错误: {e}")
        data = {
            "date": today,
            "topic": "语法基础巩固",
            "teaching_notes": "今日小课堂内容生成中遇到格式波动，请先进行日常语法练习。",
            "raw_content": raw_text
        }

    folder_name = "docs"
    os.makedirs(folder_name, exist_ok=True)
    
    file_path = f"{folder_name}/latest.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"✅ 包含语法教学与最新题目的数据已成功保存至: {file_path}")

if __name__ == "__main__":
    generate_daily_grammar()
