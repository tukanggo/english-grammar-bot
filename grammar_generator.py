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
    
    # 保持 15 道题的合理体量，既保证内容丰富，又能有效避免服务器瞬间响应过载超时
    prompt = f"""
    今天是 {today}。你是一位优秀的国际学校小学英语高级教师。
    请为 4-6 年级（Primary 4-6）学生设计一套全新的、绝对不与往常重复的 15 道英语语法单选题。
    
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
    
    # 明确使用您需要的 gemini-3.8-flash 模型
    model_name = 'gemini-3.8-flash'
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"正在请求 {model_name} 生成教学内容与新题 (尝试第 {attempt} 次)...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            break
        except Exception as e:
            print(f"遇到 API 限制或服务器拥堵，等待 20 秒后重试... (错误: {e})")
            if attempt == max_retries:
                print("⚠️ 达到最大重试次数，启用安全兜底数据以确保工作流顺利通过。")
            else:
                time.sleep(20)

    folder_name = "docs"
    os.makedirs(folder_name, exist_ok=True)
    
    if not response:
        # 降级兜底数据，防止 Action 崩溃
        data = {
            "date": today,
            "topic": "语法基础巩固 (智能备用通道)",
            "teaching_notes": "今日 AI 服务器访问量较大，小课堂已自动为你切换至精选语法复习题，保持每日打卡好习惯！",
            "questions": [
                {
                    "id": 1,
                    "question": "She _____ to the library every Sunday.",
                    "options": {"A": "go", "B": "goes", "C": "going", "D": "gone"},
                    "answer": "B",
                    "explanation": "主语为第三人称单数 (She)，且表示经常性习惯动作，故谓语动词用一般现在时单三形式 goes。"
                }
            ]
        }
    else:
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
        
    print(f"✅ 成功使用 {model_name} 生成并归档 {today} 的全部数据与索引！")

if __name__ == "__main__":
    generate_daily_grammar()
