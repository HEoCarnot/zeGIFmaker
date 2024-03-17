from pathlib import Path
import shutil

xmlPath = Path(r'xml/path/to/character')
destPath = Path(r'./source/character')

for folder in xmlPath.glob('*'):
    if folder.is_dir():
        for file in folder.glob('*.xml'):
            destFile = destPath / file.relative_to(xmlPath)
            
            # 创建目标文件的父目录
            # destFile.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            shutil.copy2(file, destFile)
            print(f'{file} -> {destFile}')