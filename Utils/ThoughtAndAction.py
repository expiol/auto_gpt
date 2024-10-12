from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class Action(BaseModel):
    name: str = Field(description="工具或指令名称")
    args: Optional[Dict[str, Any]] = Field(description="工具或指令参数，由参数名称和参数值组成")

class Thought(BaseModel):
    text: str = Field(description="思考内容")
    reasoning: str = Field(description="思考过程")
    plan: List[str] = Field(description="思考结果形成的一系列执行计划")
    criticism: str = Field(description="建设性的自我批评")
    speak: str = Field(description="将思考结果转换为语言，用于输出")

class ThoughtAndAction(BaseModel):
    thought: Thought = Field(description="思考过程")
    action: Action = Field(description="当前的执行动作")

    def is_finish(self) -> bool:
        return self.action.name.lower() == "finish"