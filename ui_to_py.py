import subprocess
import os


files_path = os.path.abspath("./src/ui")
# 遍历 ui 文件夹下的所有文件

ui_files = []
for root, dirs, files in os.walk(files_path):
    for file in files:
        if file.endswith(".ui"):
            # 打印文件名
            print(file)
            command = (
                r".\Scripts\python.exe -m PyQt5.uic.pyuic -x "
                + f"{os.path.join(root, file)}"
                + " -o "
                + f"{os.path.join(root, file.replace('.ui', '.py'))}"
            )
            subprocess.run(command, shell=True)
