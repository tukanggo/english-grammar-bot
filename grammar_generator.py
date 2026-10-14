import os
import datetime
from google import genai

client = genai.Client()

def generate_daily_grammar():
    print("1. 正在请求 Gemini AI 生成 30 道小学 4-5 年级英语语法练习题...")
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    prompt = """
    你是一位优秀的小学英语高级教师。请为新加坡或国际学校 4-5 年级（Primary 4 to Primary 5）的学生设计一份大规模的英语语法测试卷。
    
    要求严格按照以下格式输出：
    1. **【测试主题】**（例如：综合语法专项练习 - 时态、介词、代词、形容词比较级等）
    2. **【30道单项选择题】**
       - 必须刚好生成 30 道题。
       - 每道题必须有 4 个选项：A、B、C、D。
       - 题目难度要符合 Primary 4 至 Primary 5 的标准。
    3. **【参考答案与详细解析】**
       - 在文末给出 1 到 30 题的标准答案。
       - 针对每一道题给出简短、清晰的中文或双语解析。
    
    请使用清晰的 Markdown 格式排版。
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    grammar_content = response.text
    folder_name = "daily_grammar"
    os.makedirs(folder_name, exist_ok=True)
    
    file_path = f"{folder_name}/{today}_30_questions_grammar.md"
    file_content = f"# Primary 4-5 English Grammar - 30 Questions ({today})\n\n{grammar_content}"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)
    print(f"3. 成功保存到文件: {file_path}")

if __name__ == "__main__":
    generate_daily_grammar()
