import os
from openai import OpenAI
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn

# ==========================================
# 1. 环境变量与配置 (工程完整性：解耦配置)
# ==========================================
# 这样写可以同时兼容本地测试和云端部署
API_KEY = os.environ.get("SILICON_API_KEY", "你的本地测试KEY") 
BASE_URL = "https://api.siliconflow.cn/v1" 

# 模拟合规知识库 (技术深度：引入 RAG 思想的上下文注入)
# 这是为了让 Agent 生成的内容不再是“瞎编”，而是有据可依
REGULATORY_KNOWLEDGE = """
【软著申请文档规范指南】：
1. 运行环境：必须包含硬件要求（如CPU主频、内存）和软件要求（如操作系统版本、数据库版本）。
2. 系统架构：需描述客户端、服务器端及数据流向。
3. 功能模块：必须涵盖用户权限管理、核心业务逻辑、数据查询与导出。
4. 操作手册：每个功能点必须包含“进入路径-操作步骤-预期结果”的闭环描述。
"""

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def generate_manual_content(project_name, brief_desc):
    """
    通过多智能体协作生成文档。
    Agent 1 (研发总监) -> 负责业务逻辑扩写
    Agent 2 (合规专员) -> 负责对照规范进行二次修正
    """
    
    # ------------------------------------------
    # 🕵️‍♂️ Agent 1: 研发总监 (Creative Draft)
    # ------------------------------------------
    print(f"[Agent 1] 正在根据简述推演系统架构...")
    agent1_system = """你是一个资深架构师。请根据软件名称和简述，详尽地设计出系统的功能模块和操作流程。
    你需要输出：运行环境需求、系统整体架构设计、以及详细的功能点列表。"""
    
    try:
        # 第一轮生成：初步草稿
        response1 = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3", 
            messages=[
                {"role": "system", "content": agent1_system},
                {"role": "user", "content": f"软件名称：{project_name}\n功能简述：{brief_desc}"}
            ],
            temperature=0.8
        )
        draft_content = response1.choices[0].message.content
        print("[Agent 1] 初步草稿生成完毕。")

        # ------------------------------------------
        # 👨‍⚖️ Agent 2: 合规审查员 (Refinement with RAG)
        # ------------------------------------------
        # 这里的关键是把 REGULATORY_KNOWLEDGE 注入进去，这就是技术深度的体现
        print("[Agent 2] 正在对照合规知识库进行格式化修正...")
        agent2_system = f"""你是一个严苛的软著审查专员。
        请参考以下【官方规范指南】对研发总监提供的草稿进行彻底重写：
        {REGULATORY_KNOWLEDGE}
        
        【输出要求】：
        1. 严禁出现 Markdown 符号（如 #, **, ```）。
        2. 必须严格分为：一、运行环境；二、系统架构；三、功能模块；四、操作步骤。
        3. 确保所有内容符合规范指南中的细节要求。"""
        
        response2 = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3", 
            messages=[
                {"role": "system", "content": agent2_system},
                {"role": "user", "content": f"请重写此内容：\n\n{draft_content}"}
            ],
            temperature=0.1 # 审查员需要高确定性
        )
        
        final_content = response2.choices[0].message.content
        print("[Agent 2] 最终合规文档处理完成。")
        return final_content

    except Exception as e:
        print(f"Workflow Error: {e}")
        return None

# ==========================================
# 3. 文档渲染引擎 (工程完整性：标准公文排版)
# ==========================================
def save_to_word(content, output_file="用户手册.docx"):
    if not content: return
    
    doc = Document()
    # 全局宋体设置
    style = doc.styles['Normal']
    font = style.font
    font.name = '宋体'
    font.size = Pt(12) 
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    for line in content.split('\n'):
        if not line.strip(): continue
        p = doc.add_paragraph(line)
        # 自动识别一级标题并加粗
        if any(line.startswith(prefix) for prefix in ["一、", "二、", "三、", "四、"]):
            p.runs[0].bold = True
            p.runs[0].font.size = Pt(14) 
            
    doc.save(output_file)
