import streamlit as st
import os
import zipfile
import tempfile
from agent_generator import generate_manual_content, save_to_word
from core_generator import generate_source_code_doc # 引入第一天写的核心代码

# 设置网页全局属性 (让页面变宽一点，体验更好)
st.set_page_config(page_title="软著文档自动化系统", page_icon="🚀", layout="wide")

st.title("🚀 软件著作权申请文档·极速自动生成工作台")
st.markdown("---")

# 引入强大的多标签页功能，区分两块核心业务
tab1, tab2 = st.tabs(["📝 1. 智能用户手册生成 (AI Agent)", "💻 2. 源代码合规文档生成 (清洗与排版)"])

# ================= TAB 1: 智能用户手册 =================
with tab1:
    st.header("基于大模型的《操作手册》智能编写")
    st.write("只需输入项目简介，AI 智能体将自动规划架构、推演业务流并生成符合国标的 Word 手册。")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        project_name = st.text_input("📦 请输入软件名称：", value="EduMemory教育记忆管理系统")
        brief_desc = st.text_area(
            "💡 请输入核心功能简述：", 
            value="这是一个结合大模型的智能教育辅助系统，提供个性化学习路径规划、知识库管理以及记忆曲线复习提醒等核心功能。",
            height=120
        )
    
    if st.button("🤖 启动 AI 智能体一键生成手册", type="primary"):
        if project_name and brief_desc:
            with st.spinner('AI 正在推演系统架构并疯狂码字中，预计需要 15-20 秒...'):
                content = generate_manual_content(project_name, brief_desc)
                if content:
                    output_filename = f"{project_name}_用户手册.docx"
                    save_to_word(content, output_filename)
                    st.success("✅ 智能分析与文档组装成功！")
                    with open(output_filename, "rb") as file:
                        st.download_button(
                            label="⬇️ 点击下载 Word 手册",
                            data=file,
                            file_name=output_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("❌ 生成失败，请检查 API Key 余量或网络连通性。")
        else:
            st.warning("⚠️ 请先填写完整的软件名称和简述！")

# ================= TAB 2: 源代码文档 =================
with tab2:
    st.header("源代码极速清洗与标准排版")
    st.write("上传包含项目代码的 `.zip` 压缩包，系统将自动遍历提取代码、剔除空行、按要求截取 3000 行，并生成宋体五号的无缝排版文档。")
    
    uploaded_zip = st.file_uploader("📂 请上传项目代码压缩包 (.zip)", type=["zip"])
    
    if uploaded_zip is not None:
        if st.button("⚙️ 开始提取并生成代码文档", type="primary"):
            with st.spinner('正在解压并清洗代码结构，请稍候...'):
                # 工业级做法：使用临时文件夹处理用户文件，处理完自动销毁，防止硬盘撑爆
                with tempfile.TemporaryDirectory() as temp_dir:
                    # 1. 暂存上传的 zip
                    zip_path = os.path.join(temp_dir, "upload.zip")
                    with open(zip_path, "wb") as f:
                        f.write(uploaded_zip.getbuffer())
                    
                    # 2. 安全解压
                    extract_dir = os.path.join(temp_dir, "source_codes")
                    os.makedirs(extract_dir, exist_ok=True)
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(extract_dir)
                    except zipfile.BadZipFile:
                        st.error("❌ 解压失败：上传的文件不是有效的 ZIP 格式。")
                        st.stop()
                        
                    # 3. 调用核心脚本生成文档
                    output_docx_path = os.path.join(temp_dir, "源代码文档_排版合规版.docx")
                    
                    # 执行第一天写的函数，直接把输出路径指定到临时文件夹
                    generate_source_code_doc(extract_dir, output_file=output_docx_path)
                    
                    # 4. 提供下载
                    if os.path.exists(output_docx_path):
                        st.success("✅ 源代码文档读取与排版完成！")
                        with open(output_docx_path, "rb") as file:
                            st.download_button(
                                label="⬇️ 点击下载《源代码合规文档》",
                                data=file,
                                file_name="源代码文档_排版合规版.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                    else:
                        st.error("❌ 提取失败，请检查压缩包内是否包含常见的代码文件（.py, .java, .vue 等）。")