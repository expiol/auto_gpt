import re

def extract_commands_from_response(response_text):
    """
    Extracts commands wrapped within <COMMAND> and </COMMAND> tags from GPT's response.
    """
    if not response_text or not isinstance(response_text, str):
        return []
    pattern = r'<COMMAND>(.*?)</COMMAND>'
    matches = re.findall(pattern, response_text, re.DOTALL)
    commands = [cmd.strip() for cmd in matches if cmd.strip()]
    return commands

