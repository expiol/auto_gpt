import json

def Friendly(string):
    """
    将 LangChain 的输出解析器返回的描述进行格式化，方便阅读。
    """
    lines = string.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("{") and line.endswith("}"):
            try:
                lines[i] = json.dumps(json.loads(line), ensure_ascii=False)
            except:
                pass
    return '\n'.join(lines)