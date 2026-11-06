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
    
    prompt = f"""
    今天是 {today}。你是一位资深的英语语言学教授与高级语法专家。
    请为全年龄段英语学习者设计一套涵盖**英语全语法体系**（包括高级时态、虚拟语气、从句嵌套、非谓语动词、倒装强调、主谓一致等核心板块）的深度语法训练卷，总计 30 道题。
    
    【核心要求】：
    1. 今天的日期是 {today}。请从英语全语法大库中精选一个核心且具有深度的语法专题。
    2. 【深度教学笔记 (teaching_notes)】：在生成题目之前，必须提供一份**高密度的专业语法讲义**。要求：
       - 字数在 300-500 字左右，结构化分点阐述（可使用 Markdown 符号如换行）。
       - 包含：核心概念定义、底层逻辑原理、常见易错陷阱（Pitfalls）、以及 3-4 个覆盖不同语境的高级英文例句与精准中文翻译。
    3. 试题必须包含多维度的题型（如单选、填空、改错、句型重写），确保考察深度。
    4. 必须严格只输出一个合法的 JSON 对象（不要包裹在 markdown 代码块中，直接输出纯 JSON 字符串），结构设计如下：
    {{
      "date": "{today}",
      "topic": "今天深入探讨的高级语法专项名称",
      "teaching_notes": "1. 核心定义：...\\n2. 结构与底层逻辑：...\\n3. 典型易错点：...\\n4. 经典例句：...",
      "questions": [
        {{
          "id": 1,
          "type": "multiple_choice",
          "question": "高难度题目文本...",
          "options": {{
            "A": "选项A",
            "B": "选项B",
            "C": "选项C",
            "D": "选项D"
          }},
          "answer": "B",
          "explanation": "深度的语法考点解析与排除法说明..."
        }}
      ]
    }}
    5. 确保 JSON 格式必须完全正确，绝对不能出现截断。确保所有题目加起来一共 30 道。
    """

    max_retries = 3
    response = None
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"正在请求 Gemini API 生成教学内容与新题 (尝试第 {attempt} 次)...")
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt
            )
            break
        except (ServerError, ClientError) as e:
            print(f"遇到 API 限制或服务器拥堵，等待 30 秒后重试... (错误: {e})")
            if attempt == max_retries:
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
        print(f"JSON 解析失败，保存原始内容。错误: {e}")
        data = {
            "date": today,
            "topic": "语法基础巩固",
            "teaching_notes": "今日小课堂生成中遇到格式波动，请先进行日常练习。",
            "raw_content": raw_text
        }

    folder_name = "docs"
    os.makedirs(folder_name, exist_ok=True)
    
    # 1. 保存当日专属文件
    daily_file_path = f"{folder_name}/grammar_{today}.json"
    with open(daily_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    # 2. 更新 latest.json
    latest_file_path = f"{folder_name}/latest.json"
    with open(latest_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 3. 自动扫描并更新 days_index.json 索引文件供网页下拉菜单读取
    dates_list = []
    for filename in os.listdir(folder_name):
        if filename.startswith("grammar_") and filename.endswith(".json"):
            date_str = filename.replace("grammar_", "").replace(".json", "")
            dates_list.append(date_str)
    
    dates_list.sort(reverse=True)
    index_file_path = f"{folder_name}/days_index.json"
    with open(index_file_path, "w", encoding="utf-8") as f:
        json.dump(dates_list, f, ensure_ascii=False, indent=2)
        
    print(f"✅ 成功生成并归档 {today} 的全部数据与索引！")

if __name__ == "__main__":
    generate_daily_grammar()
