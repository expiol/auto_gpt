from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers.base import BaseOutputParser
from langchain_core.tools import BaseTool
from .FileUtils import load_file
from .CommonUtils import *
import json

class PromptTemplateBuilder:
    def __init__(self,
                 prompt_path: str,
                 prompt_file: str = "main.templ",
    ):
        self.prompt_path = prompt_path
        self.prompt_file = prompt_file
        
    def build(
        self,
        tools: Optional[List[BaseTool]] = None,
        output_parser: Optional[BaseOutputParser] = None,
    ) -> PromptTemplate:
        main_templ_str = load_file(self.prompt_path, self.prompt_file)
        main_templ = PromptTemplate.from_template(main_templ_str)   
        #使用了langchain的from_template方法，可以直接从字符串中构建PromptTemplate对象,字符串里面的占位会被解析为变量,然后通过partial_variables参数指定变量名和对应的值
        """
        print(main_templ)
        input_variables=['ai_name', 'ai_role', 'constraints_templ', 'format_instruction', 'instructions_templ', 'long_term_memory', 'performance_evalution_tmpl', 'resources_templ', 'short_term_memory', 'step_instruction', 'task_desctription', 'tools'] 
        template='你的名字是{ai_name},你是{ai_role}\n\nYou must follow the instruction below to complete the ask.\n{instructions_templ}\n\n你的任务是：\n{task_desctription}\n\nConstraints:\n{constraints_templ}\n\n你可以使用一下工具或指令，它们又被称为actions：\n0. FINISH：任务完成， args：None\n{tools}\n\nResources:\n{resources_templ}\n\nPerformance Evaluation:\n{performance_evalution_tmpl}\n\n相关的历史记录:\n{long_term_memory}\n\n当前任务的执行记录：\n{short_term_memory}\n\nYou should only respond in JSON format as desctibed below.\nResponse Format:\n{format_instruction}\n\nEnsure the response can be parsed by Python json.loads\n\n{step_instruction}'
        """
        partial_variables = {}
        for var in main_templ.input_variables:
            if var.endswith("_templ"):
                var_file = var[:-6] + ".templ"
                var_str = self._get_prompt(var_file)
                partial_variables[var] = var_str
            
        if tools is not None:
            tools_prompt = self._get_tools_prompt(tools)
            partial_variables["tools"] = tools_prompt
        
        if output_parser is not None:
            # 为了避免ascii码转入我们的prompt导致问题，我们调用该函数进行转换
            partial_variables["format_instruction"] = Friendly(output_parser.get_format_instructions())
            
        return main_templ.partial(**partial_variables)  #返回填充了templ文件、tools、output_parser的prompt，其他变量用户单独传递

            
    # 加载模板，返回给partial_variables使用
    def _get_prompt(self, prompt_file):     #没有破环
        builder = PromptTemplateBuilder(self.prompt_path,prompt_file=prompt_file)
        return builder.build().format()
    
    # 获取工具提示:根据工具集里面每个工具的提示生成对应的prompt
    def _get_tools_prompt(self, tools):
        tools_prompt = ""
        for i,tool in enumerate(tools):
            tools_prompt += f"{i+1}. {tool.name} : {tool.description},\
                args json schema: {json.dumps(tool.args,ensure_ascii=False)}\n"
        return tools_prompt
            