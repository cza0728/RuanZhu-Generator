import os
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn

def generate_source_code_doc(source_dir, output_file="源代码文档.docx", extensions=('.py', '.java', '.cpp', '.js', '.vue', '.html', '.css')):
    print(f"🔍 正在扫描目录: {source_dir}")
    all_lines = []
    
    # 1. 遍历并读取所有代码
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(extensions):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            # 剔除首尾空白，如果是空行则跳过（软著要求不能有大段空行）
                            stripped_line = line.strip()
                            if stripped_line: 
                                # 保持原始缩进，只去除换行符
                                all_lines.append(line.rstrip('\n'))
                except Exception as e:
                    print(f"⚠️ 无法读取文件 {filepath}: {e}")

    total_lines = len(all_lines)
    print(f"📝 共提取到 {total_lines} 行有效代码。")

    # 2. 截取代码：最多3000行 (60页 * 50行)
    # 软著规则：超过60页，取前30页和后30页
    if total_lines > 3000:
        print("✂️ 代码超过3000行，正在截取前1500行和后1500行...")
        final_lines = all_lines[:1500] + all_lines[-1500:]
    else:
        final_lines = all_lines

    # 3. 生成 Word 文档
    print("⏳ 正在生成 Word 文档，请稍候...")
    doc = Document()
    
    # 设置全文字体为宋体，字号为五号 (10.5磅) - 这是标准的公文格式
    style = doc.styles['Normal']
    font = style.font
    font.name = '宋体'
    font.size = Pt(10.5)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    # 将代码写入 Word
    for line in final_lines:
        p = doc.add_paragraph(line)
        # 设置段落格式，尽量保证每页能放下50行
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = Pt(12) 

    doc.save(output_file)
    print(f"✅ 生成成功！文件已保存至: {output_file}")

# ====== 测试运行 ======
if __name__ == "__main__":
    # 这里替换成你准备的测试代码文件夹路径
    TARGET_CODE_FOLDER = "./test_code" 
    
    if os.path.exists(TARGET_CODE_FOLDER):
        generate_source_code_doc(TARGET_CODE_FOLDER)
    else:
        print(f"❌ 找不到测试文件夹 '{TARGET_CODE_FOLDER}'，请先创建并放一些代码进去。")