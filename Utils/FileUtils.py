import os

def load_file(file_path, file_name):
    full_path = os.path.join(file_path, file_name)
    try:
        with open(full_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"文件未找到：{full_path}")
        raise
    except Exception as e:
        print(f"读取文件时发生错误：{e}")
        raise