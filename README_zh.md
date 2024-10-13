# AutoGPT 网络安全助手

**AutoGPT 网络安全助手** 是一个使用 LangChain 和 OpenAI 的 GPT 模型构建的智能代理。它旨在通过利用 Shell 命令和互联网搜索功能等各种工具自主处理与网络安全相关的任务。该代理可以管理任务、根据用户指令使用工具，并保持短期和长期记忆，以随着时间的推移提高其性能。

## 目录

* [功能](#功能)
* [先决条件](#先决条件)
* [先决条件](#先决条件)
* [安装](#安装)
* [使用](#使用)
* [内存管理](#内存管理)
* [贡献](#贡献)
* [许可证](#许可证)

## 功能

* **自主任务处理**：根据用户输入自动处理和执行与网络安全相关的任务。
* **工具集成**：利用 Shell 命令和互联网搜索等工具执行操作。
* **内存管理**：维护短期和长期记忆以增强决策和任务执行。
* **手动模式**：允许用户干预以确认操作和修改计划。
* **可扩展架构**：轻松添加或修改工具以扩展代理的功能。

## 先决条件

在设置 AutoGPT 网络安全助手之前，请确保您具有以下条件：

* **Python 3.8+**：确保您的系统上安装了 Python。您可以从 [python.org](https://www.python.org/downloads/) 下载它。
* **OpenAI API 密钥**：与 OpenAI 的 GPT 模型交互所需。
* **SerpAPI API 密钥**：`SearchTool` 执行互联网搜索所需。
* **Google API 以及search id密钥**：`Google_search` 备用互联网搜索工具。
## 安装

1. **克隆存储库**

```bash
git clone https://github.com/expiol/auto_gpt.git
cd auto_gpt
```

2. **创建虚拟环境（可选但推荐）**

```bash
python3 -m venv venv
source venv/bin/activate # 在 Windows 上：venv\Scripts\activate
```

3. **安装依赖项**

```bash
pip3 install -r requirements.txt
```

**注意：**确保 `requirements.txt` 文件包含所有必需的软件包，例如 `langchain`、`openai`、`serpapi` 等。

4. **运行**

```bash
python3 main.py
```

## 配置

1. **设置环境变量**

在根目录中创建一个 `.env` 文件项目目录并添加您的 API 密钥：

```env
OPENAI_API_KEY='your_openai_api_key'
OPENAI_BASEURL='your_openai_baseurl'
SERPAPI_API_KEY="your_serpapi_api_key"
```

**注意**：将 `your_openai_api_key` 和 `your_serpapi_api_key` 替换为您的实际 API 密钥。

2. **提示配置**

确保您的提示模板在指定的 `prompts_path` 中正确设置。关键提示模板包括：

* `step_instruction.templ`
* `force_rethink.templ`
* `finish_instruction.templ`

这些模板指导代理在任务执行期间的行为。

## 内存管理

代理利用短期和长期记忆来管理上下文并改善其响应。

* **短期记忆**：使用 `ConversationBufferWindowMemory` 存储最近的交互，直至指定窗口大小（`max_thought_steps`）。
* **长期记忆**：使用 `ConversationSummaryMemory` 总结对话，如果提供了记忆检索器，则可选使用 `VectorStoreRetrieverMemory`。

**清除记忆**：

* **任务完成后：**清除记忆，以确保没有残留数据影响未来任务。
* **添加讨论时：**记忆保持完整，以合并其他用户输入，而不会丢失先前的上下文。

## 贡献

欢迎贡献！如果您遇到任何问题或有改进建议，请打开问题或提交拉取请求。

1. **分叉存储库**

2. **创建功能分支**

```bash
git checkout -b feature/YourFeature
```

3. **提交更改**

```bash
git commit -m "添加您的功能"
```

4. **推送到分支**

```bash
git push origin feature/YourFeature
```

5. **打开拉取请求**

## 许可证

本项目根据 MIT 许可证获得许可。

* * *

**免责声明：**请确保您安全地处理 API 密钥并遵守 OpenAI 和 SerpAPI 的使用政策。本项目仅用于教育和授权的网络安全目的。未经授权的访问或滥用可能会导致法律后果。
