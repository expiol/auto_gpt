from langchain.chat_models.base import BaseChatModel
from langchain.llms.base import BaseLLM
from langchain.tools import BaseTool
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.output_parsers import PydanticOutputParser
from typing import List, Optional
from Utils.ThoughtAndAction import ThoughtAndAction
from Utils.CommonUtils import Friendly  
from Utils.PromptTemplateBuilder import PromptTemplateBuilder
from langchain.memory import (
    ConversationBufferWindowMemory,
    ConversationSummaryMemory,
    VectorStoreRetrieverMemory,
)
from langchain.schema import Document
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
from langchain_openai import OpenAI
from langchain_core.pydantic_v1 import ValidationError


class AutoGPT:
    def __init__(
        self,
        llm: BaseLLM | BaseChatModel,
        prompts_path: str,
        tools: List[BaseTool],
        agent_name: Optional[str] = "Cyber Security Assistant",
        agent_role: Optional[str] = "Cybersecurity intelligent assistant robot that can automatically solve problems by using tools and instructions",
        max_thought_steps: Optional[int] = 10,
        memory_retriever: Optional[VectorStoreRetriever] = None,
        manual: Optional[bool] = False,  # 新增参数，决定模式
    ):
        self.llm = llm
        self.prompts_path = prompts_path
        self.tools = tools
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.max_thought_steps = max_thought_steps
        self.memory_retriever = memory_retriever  
        self.manual = manual 

        self.output_parser = PydanticOutputParser(
            pydantic_object=ThoughtAndAction
        )

        self.step_prompt = (
            PromptTemplateBuilder(self.prompts_path, "step_instruction.templ")
            .build()
            .format()
        )
        self.force_rethink_prompt = (
            PromptTemplateBuilder(self.prompts_path, "force_rethink.templ")
            .build()
            .format()
        )

    def run(self, task_description: str, verbose=False) -> str:
        """
        Runs the AutoGPT agent, handling multiple tasks based on user input.
        """
        initial_task_description = task_description  # Rename for internal use
        finish_all_tasks = False
        reply = ""

        # Initialize memories
        short_term_memory = ConversationBufferWindowMemory(
            ai_prefix="Reason",  # 默认格式是：human 和 AI，AutoGpt 不存在 human，所以改成和我们情况符合的思考和行动
            human_prefix="Act",
            k=self.max_thought_steps,  # 短时记忆存储的窗口大小，设置为思考步数，表示全部存储
        )

        # 长时记忆通过 summary 来总结，使用统一的 self.llm
        summary_memory = ConversationSummaryMemory(
            llm=self.llm,  
            buffer="问题：" + initial_task_description + "\n",
            ai_prefix="Reason",
            human_prefix="Act",
        )

        if self.memory_retriever is not None:
            long_term_memory = VectorStoreRetrieverMemory(
                retriever=self.memory_retriever,
            )
        else:
            long_term_memory = None

        while not finish_all_tasks:
            thought_step_count = 0  # 当前思考轮数
            last_action = None  # 更新上一次的 action 标识
            finish_turn = False  # 是否完成任务，判断 action 是否是 FINISH 得到，如果完成，需要进行输出最终结果

            prompt_template = (
                PromptTemplateBuilder(self.prompts_path)
                .build(
                    tools=self.tools,
                    output_parser=self.output_parser,
                )
                .partial(
                    ai_name=self.agent_name,
                    ai_role=self.agent_role,
                    task_description=initial_task_description,
                )
            )
            chain = prompt_template | self.llm

            while thought_step_count < self.max_thought_steps:
                # 调用一次 step，获取 thought 和 action
                thought_and_action = self._step(
                    chain=chain,
                    task_description=initial_task_description,
                    short_term_memory=short_term_memory,
                    long_term_memory=long_term_memory,
                )
                # 判断是否重复，如果重复，则需要重新思考
                action = thought_and_action.action
                if self._is_repeated(last_action, action):  # 这里只让他进行一次重思考
                    thought_and_action = self._step(
                        chain=chain,
                        task_description=initial_task_description,
                        short_term_memory=short_term_memory,
                        long_term_memory=long_term_memory,
                        force_rethink=True,
                    )
                    action = thought_and_action.action

                # 更新上一次的 action
                last_action = action

                # 打印当前的 thought 和 action
                if verbose:
                    print(str(thought_and_action.thought))

                # 根据指令判断整体任务是否完成
                if thought_and_action.is_finish():  # 之所以在这里判断 finish 进行 break，因为是根据前面的 short_term_memory 来判断的任务结束，所以不需要存储后面的 short_term_memory, 任务已经结束
                    finish_turn = True
                    break

                # 如果 manual 模式开启，进行用户确认
                if self.manual:
                    user_confirm = self._prompt_user_confirmation(action)
                    if not user_confirm:
                        # 用户未确认，提供选项
                        user_choice = self._prompt_user_choice()
                        if user_choice == '1':
                            # 选项1：总结并退出
                            reply = self._final_step(short_term_memory, initial_task_description)
                            print(reply)
                            finish_all_tasks = True
                            break
                        elif user_choice == '2':
                            # 选项2：添加讨论并修改操作
                            additional_discussion = self._get_user_input("请输入额外的讨论内容，以修改操作：")
                            
                            # 将讨论内容添加到长时记忆中，以便 GPT 进行调整
                            summary_memory.save_context(
                                {"input": "用户添加的讨论内容"},
                                {"output": additional_discussion},
                            )
                            
                            if long_term_memory is not None:
                                long_term_memory.save_context(
                                    {"input": "用户添加的讨论内容"},
                                    {"output": additional_discussion},
                                )
                            
                            print("已添加额外的讨论内容，系统将重新评估操作。")
                            
                            # 重新构建链以包含更新后的长时记忆
                            prompt_template = (
                                PromptTemplateBuilder(self.prompts_path)
                                .build(
                                    tools=self.tools,
                                    output_parser=self.output_parser,
                                )
                                .partial(
                                    ai_name=self.agent_name,
                                    ai_role=self.agent_role,
                                    task_description=initial_task_description,
                                )
                            )
                            chain = prompt_template | self.llm
                            
                            # 重置思考步数和上一个动作，以重新开始思考过程
                            thought_step_count = 0
                            last_action = None
                            continue  # 重新开始思考步骤
                        else:
                            print("无效的选择，继续执行默认操作。")

                # 正常情况下，是需要去调用工具
                tool = self._find_tool(action.name)
                if tool is None:  # 没有找到对应的工具，报错
                    result = (
                        f"Error: 找不到工具或指令 '{action.name}'. "
                        f"请从提供的工具/指令列表中选择，请确保按对的格式输出."
                    )
                else:  # 找到工具，进行运行，得到结果
                    try:
                        observation = tool.run(action.args)
                    except ValidationError as e:
                        observation = (
                            f"Validation Error in args: {str(e)}, args: {action.args}."
                        )
                    except Exception as e:
                        observation = (
                            f"Error: {str(e)}, {type(e).__name__}, args: {action.args}."
                        )
                    result = (
                        f"执行：{str(action)}\n"
                        f"返回结果：{observation}"
                    )
                # 打印中间结果
                if verbose:
                    print(result)

                # 更新短时记忆，存储 thought 和 action 作为输入，以及执行结果作为输出
                short_term_memory.save_context(
                    {"input": str(thought_and_action.thought)},
                    {"output": result},
                )

                # 更新短时记忆时，也更新一下长时记忆，但是长时记忆是通过 summary 来总结
                summary_memory.save_context(
                    {"input": str(thought_and_action.thought)},
                    {"output": result},
                )

                thought_step_count += 1

            # 任务结束的时候，加入长时记忆即可
            if long_term_memory is not None:
                long_memory_history = summary_memory.load_memory_variables({}).get("history", "")
                long_term_memory.save_context(
                    {"input": initial_task_description},
                    {"output": long_memory_history},
                )

            if finish_turn:  # 如果满足结束条件，则进行后续处理
                reply = self._final_step(short_term_memory, initial_task_description)
                print(reply)  # Optionally print the final reply

                # Prompt the user to decide whether to continue or exit
                user_decision = self._prompt_user_to_continue()
                if user_decision.lower() in ['yes', 'y', '是', 'y是', '是的']:
                    # Prompt the user for the next task description
                    task_description = self._get_user_input("请输入下一个任务描述：")
                    initial_task_description = task_description  # Update for next iteration
                    # Continue the loop with the new task_description
                    continue
                else:
                    # User chose to exit, clear memories
                    finish_all_tasks = True
                    short_term_memory.clear()
                    if long_term_memory is not None:
                        self._clear_long_term_memory(long_term_memory)
                    print("记忆已清除，任务已结束。")
                    break
            else:  # 没有结果，返回最后一次思考的结果
                reply = thought_and_action.thought.speak
                print(reply)
                # Decide whether to continue based on the context
                user_decision = self._prompt_user_to_continue()
                if user_decision.lower() in ['yes', 'y', '是', 'y是', '是的']:
                    task_description = self._get_user_input("请输入下一个任务描述：")
                    initial_task_description = task_description  # Update for next iteration
                    continue
                else:
                    finish_all_tasks = True
                    short_term_memory.clear()
                    if long_term_memory is not None:
                        self._clear_long_term_memory(long_term_memory)
                    print("记忆已清除，任务已结束。")
                    break

        return reply

    def _step(
        self,
        chain,
        task_description,
        short_term_memory,
        long_term_memory,
        force_rethink=False,
    ):
        # 去向量库里检索相似度符合的长时记忆
        long_memory = ""
        if long_term_memory is not None:
            long_memory = long_term_memory.load_memory_variables(
                {"prompt": task_description}  # 拿任务检索内存 memory，获取历史记录；至于里面的 key，并不重要，可以认为是标识而已；根据相似度检索的
            ).get("history", "")
        else:
            long_memory = ""

        current_response = chain.invoke(
            {
                "short_term_memory": short_term_memory.load_memory_variables({}).get("history", ""),
                "long_term_memory": long_memory,
                "step_instruction": self.step_prompt if not force_rethink else self.force_rethink_prompt,
            }
        )
        try:
            thought_and_action = self.output_parser.parse(
                Friendly(current_response.content)
            )
        except Exception as e:
            print("---------------------------------------------------")
            print(Friendly(current_response.content))  # 这个地方容易报错，暂时没有查出来，偶尔报错
            print("---------------------------------------------------")
            thought_and_action = ThoughtAndAction()  # 提供一个默认值以避免后续错误
        return thought_and_action

    # 用于判断两次 action (Action 对象) 是否重复，如果重复需要 reforce，判断名称和参数
    def _is_repeated(self, last_action, action):
        # 判断 obj
        if last_action is None:
            return False
        if action is None:
            return True

        # 判断 name
        if last_action.name != action.name:
            return False

        # 判断参数
        if set(last_action.args.keys()) != set(action.args.keys()):
            return False

        for k, v in last_action.args.items():
            if action.args.get(k) != v:
                return False

        return True

    # 根据名称查找工具
    def _find_tool(self, tool_name):
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None

    def _final_step(self, short_term_memory, task_description):
        finish_prompt = (
            PromptTemplateBuilder(self.prompts_path, "finish_instruction.templ")
            .build()
            .partial(
                ai_name=self.agent_name,
                ai_role=self.agent_role,
                task_description=task_description,
                short_term_memory=short_term_memory.load_memory_variables({}).get("history", ""),
            )
        )

        chain = finish_prompt | self.llm
        response = chain.invoke({})
        return response

    def _prompt_user_to_continue(self) -> str:
        """
        Prompts the user to decide whether to continue with another task or exit.
        """
        # Here, you can implement the prompt using input(), a GUI dialog, or any other method.
        # For simplicity, we'll use input().
        decision = input("是否继续追问？ (yes/no): ")
        return decision

    def _get_user_input(self, prompt: str) -> str:
        """
        Prompts the user to enter a new task description.
        """
        return input(prompt)

    def _prompt_user_confirmation(self, action):
        """
        在 manual 模式下，提示用户确认是否执行操作。
        """
        decision = input(f"准备执行操作: {action}. 确认吗? (yes/no): ")
        return decision.lower() in ['yes', 'y', '是', 'y是', '是的']

    def _prompt_user_choice(self) -> str:
        """
        当用户不确认执行操作时，提供选项让用户选择下一步操作。
        """
        print("请选择下一步操作：")
        print("1. 直接总结内容并退出")
        print("2. 添加额外的讨论内容以修改操作")
        choice = input("请输入选项编号 (1/2): ")
        return choice.strip()

    def _clear_long_term_memory(self, long_term_memory: VectorStoreRetrieverMemory):

        try:
            long_term_memory.clear()
            print("长时记忆已清除。")
        except AttributeError:
            print("无法清除长时记忆：'clear' 方法不存在。请根据您的 VectorStoreRetrieverMemory 实现进行清除。")
