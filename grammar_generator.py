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
    今天是 {today}。你是一位深谙中小学英语教学规律（Primary 4 - Secondary 5 / 7-18 岁）的顶级英语教学专家与考纲分析师。
    请为中小学生设计一套全新的、兼顾**基础巩固与中小学考纲进阶**的综合语法试题与讲义，总计 30 道题。

    【核心要求】：
    1. **主题精选与梯度设计**：
       - 今天的日期是 {today}。请从中小学核心语法库（如：时态与语态、非谓语动词、情态动词、比较级/最高级、定语/状语从句、主谓一致、倒装句等）中精选一个主题。
       - 30 道题目必须体现**难度梯度**：Q1-Q15 适合 Primary 4-6（小学中高年级基础与进阶），Q16-Q30 适合 Form 1-5 / Secondary（中学高阶与考纲压轴）。

    2. **中小学友好型教学笔记 (teaching_notes)**：
       - 用生动有趣、通俗易懂且条理清晰的语言写一段 250-400 字的“今日语法大讲堂”。
       - 必须包含：
         1) 【核心概念】：用小学生也能听懂的比喻或一句话总结解释该语法。
         2) 【口诀/公式】：给出清晰易记的语法结构公式或记忆口诀。
         3) 【避坑指南】：指出中小学生在考试中最常犯的 2-3 个典型错误。
         4) 【经典例句】：提供 3 个带有情景感的中英文对照例句。

    3. **多元题型架构 (Multi-type Questions)**：
       包含单选题（multiple_choice）、填空题（fill_in_the_blank）、改错题（error_correction）和句型转换（sentence_transformation）。

    4. **严格的 JSON 输出规范**：
       必须严格只输出一个合法的 JSON 对象（绝对不要包裹在 ```json 代码块中），结构设计如下：
    {{
      "date": "{today}",
      "target_audience": "Primary & Secondary School (Ages 9-17)",
      "topic": "今天的中小学核心语法专项名称",
      "teaching_notes": "1. 核心概念：...\\n2. 语法公式与口诀：...\\n3. 中小学生易错点：...\\n4. 经典例句：...",
      "questions": [
        {{
          "id": 1,
          "level": "Primary (P4-P6)",
          "type": "multiple_choice",
          "question": "适合小学的题目文本...",
          "options": {{
            "A": "选项A",
            "B": "选项B",
            "C": "选项C",
            "D": "选项D"
          }},
          "answer": "B",
          "explanation": "通俗易懂的解析，指出语法考点..."
        }},
        {{
          "id": 16,
          "level": "Secondary (Form 1-5)",
          "type": "fill_in_the_blank",
          "question": "适合中学的进阶填空题...",
          "options": null,
          "answer": "correct_answer",
          "explanation": "针对中学生的考点拆解解析..."
        }}
      ]
    }}

    5. 确保 JSON 格式完全正确，防止截断，所有题目加起来正好 30 道。
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
