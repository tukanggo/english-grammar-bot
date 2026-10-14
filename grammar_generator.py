import os
import datetime
from google import genai

def generate_daily_grammar():
    print("开始执行语法生成任务...")
    
    # 检查环境变量中是否有 API Key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("错误: 未检测到 GEMINI_API_KEY 环境变量！请检查 GitHub Secrets 设置。")
        return
    else:
        print("成功检测到 API Key。")

    # 初始化 Gemini 客户端
    client = genai.Client(api_key=api_key)
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"当前日期: {today}")
    
    prompt = """
    你是一位优秀的小学英语高级教师。请为新加坡或国际学校 4-5 年级（Primary 4 to Primary 5）的学生设计一份大规模的英语语法测试卷。
    
    要求严格按照以下格式输出：
    1. 【测试主题】（例如：综合语法专项练习）
    2. 【30道单项选择题】
       - 必须刚好生成 30 道题。
       - 每道题必须有 4 个选项：A、B、C、D。
       - 题目难度符合 Primary 4 至 Primary 5 的标准。
    3. 【参考答案与详细解析】
       - 在文末给出 1 到 30 题的标准答案和简短解析。
    
    请使用清晰的 Markdown 格式排版。
    """

    print("正在向 Gemini API 发送请求...")
    try:
        # 强制更新为官方要求的 gemini-3.8-flash 模型
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt
        )
        grammar_content = response.text
        print("Gemini 响应成功！")
    except Exception as e:
        print(f"调用 Gemini API 时发生错误: {e}")
        raise e

    # 保存文件
    folder_name = "daily_grammar"
    os.makedirs(folder_name, exist_ok=True)
    
    file_path = f"{folder_name}/{today}_30_questions_grammar.md"
    file_content = f"# Primary 4-5 English Grammar - 30 Questions ({today})\n\n{grammar_content}"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)
    print(f"文件已成功保存至: {file_path}")

if __name__ == "__main__":
    generate_daily_grammar()
