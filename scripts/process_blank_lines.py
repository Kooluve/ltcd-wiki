# scripts/process_blank_lines.py
import os
import re
import shutil

SRC_DIR = "docs"
DST_DIR = "docs_temp"

if os.path.exists(DST_DIR):
    shutil.rmtree(DST_DIR)
shutil.copytree(SRC_DIR, DST_DIR)

pattern = re.compile(r'\n{2,}')

for root, _, files in os.walk(DST_DIR):
    for file in files:
        if file.endswith(".md"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            # 保留原来的换行，将多空行转换为 <br>
            def repl(m):
                n = len(m.group(0)) - 1
                return "\n" + "<br>\n" * n + "\n"
            content_new = pattern.sub(repl, content)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content_new)
print("Markdown 文件多空行已处理完成")