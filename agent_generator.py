import os
from openai import OpenAI
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn

# ⚠️ 这里请务必填入你自己的硅基流动 API Key 和 Base URL



API_KEY = os.environ.get("SILICON_API_KEY", "sk-sqpcbyhnoephdzhicbkutczzcxochdumhyhhkespkqmezcol") 
BASE_URL = "https://api.siliconflow.cn/v1"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def generate_manual_content(project_name, brief_desc):
    # ==========================================
    # 🕵️‍♂️ Agent 1: 研发总监 (负责内容发散与起草)
    # ==========================================
    print(f"🧠 [Agent 1 - 研发总监] 正在疯狂推演 {project_name} 的业务逻辑...")
    agent1_system = """你是一个拥有10年经验的资深软件研发总监。
    请根据用户提供的【软件名称】和【简述】，发散思维，详尽地设计出该系统的功能模块和操作流程。
    尽量多写具体的细节和专业术语，哪怕是虚构的也要符合逻辑。"""
    
    try:
        response1 = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3", # ⚠️ 替换为你使用的硅基流动模型
            messages=[
                {"role": "system", "content": agent1_system},
                {"role": "user", "content": f"软件名称：{project_name}\n功能简述：{brief_desc}"}
            ],
            temperature=0.8
        )
        draft_content = response1.choices[0].message.content
        print("✅ [Agent 1] 草稿生成完毕，交由审查员质检。")
        
        # ==========================================
        # 👨‍⚖️ Agent 2: 合规审查员 (负责格式清洗与规范化)
        # ==========================================
        print(f"🔍 [Agent 2 - 合规审查员] 正在按照国标严格清洗和重组文档...")
        agent2_system = """你是一个极其严苛的软件著作权审查专员。你的任务是重写和优化研发总监给出的草稿。
        【极其严格的输出格式要求】：
        1. 必须严格划分为四个部分，开头必须是这四个标题：一、软件运行环境；二、系统整体架构；三、核心功能模块设计；四、详细操作步骤。
        2. 绝对不允许输出任何 Markdown 标记（严禁出现 ```, **, #, -, > 等符号）！！！
        3. 列表只能使用中文数字（如 一、二、）或阿拉伯数字（如 1. 2. 3.）。
        4. 不要输出任何寒暄语，直接输出正文。"""
        
        response2 = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3", # ⚠️ 同样替换为你的模型
            messages=[
                {"role": "system", "content": agent2_system},
                {"role": "user", "content": f"请审查并彻底重写以下草稿，严格遵守格式要求：\n\n{draft_content}"}
            ],
            temperature=0.1 # 审查员需要极低的温度，确保严谨不发散
        )
        final_content = response2.choices[0].message.content
        print("✅ [Agent 2] 文档审查与清洗完成！")
        return final_content

    except Exception as e:
        print(f"❌ 多智能体工作流执行异常: {e}")
        return None

# 👇 下面的排版代码保持不变
def save_to_word(content, output_file="用户手册.docx"):
    if not content: return
    print("⏳ 正在排版并生成 Word 文档...")
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = '宋体'
    font.size = Pt(12) 
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    lines = content.split('\n')
    for line in lines:
        if line.strip() == "": continue
        p = doc.add_paragraph(line)
        if line.startswith("一、") or line.startswith("二、") or line.startswith("三、") or line.startswith("四、"):
            p.runs[0].bold = True
            p.runs[0].font.size = Pt(14) 
    doc.save(output_file)
    print(f"🎉 最终交付物已生成: {output_file}")