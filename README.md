# AutoGPT Cyber Security Assistant

**AutoGPT Cyber Security Assistant** is an intelligent agent built using LangChain and OpenAI's GPT models. It is designed to autonomously handle cybersecurity-related tasks by leveraging various tools such as Shell commands and internet search capabilities. The agent can manage tasks, utilize tools based on user instructions, and maintain both short-term and long-term memory to improve its performance over time.

## Table of Contents

* [Features](#features)
* [Prerequisites](#prerequisites)
* [Prerequisites](#prerequisites)
* [Installation](#Installation)
* [Usage](#usage)
* [Memory Management](#memory-management)
* [Contributing](#contributing)
* [License](#license)

## Features

* **Autonomous Task Handling:** Automatically processes and executes cybersecurity-related tasks based on user input.
* **Tool Integration:** Utilizes tools like Shell commands and internet search to perform actions.
* **Memory Management:** Maintains short-term and long-term memory to enhance decision-making and task execution.
* **Manual Mode:** Allows user intervention for confirming actions and modifying plans.
* **Extensible Architecture:** Easily add or modify tools to extend the agent's capabilities.

## Prerequisites

Before setting up the AutoGPT Cyber Security Assistant, ensure you have the following:

* **Python 3.8+**: Make sure Python is installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
* **API Keys**:
    * **OpenAI API Key**: Required for interacting with OpenAI's GPT models.
    * **SerpAPI API Key**: Required for the `SearchTool` to perform internet searches.

## Installation

1. **Clone the Repository**
    
    ```bash
    git clone https://github.com/expiol/auto_gpt.git
    cd auto_gpt
    ```
    
2. **Create a Virtual Environment (Optional but Recommended)**
    
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
    
3. **Install Dependencies**
    
    ```bash
    pip3 install -r requirements.txt
    ```
    
    **Note:** Ensure that the `requirements.txt` file includes all necessary packages such as `langchain`, `openai`, `serpapi`, etc.
    
4. **Install Dependencies**

    ```bash
    
    ```

## Configuration

1. **Set Up Environment Variables**
    
    Create a `.env` file in the root directory of the project and add your API keys:
    
    ```env
    OPENAI_API_KEY='your_openai_api_key'
    OPENAI_BASEURL='your_openai_baseurl'
    SERPAPI_API_KEY="your_serpapi_api_key"
    ```
    
    **Note:** Replace `your_openai_api_key` and `your_serpapi_api_key` with your actual API keys.
    
2. **Prompts Configuration**
    
    Ensure that your prompt templates are correctly set up in the specified `prompts_path`. The key prompt templates include:
    
    * `step_instruction.templ`
    * `force_rethink.templ`
    * `finish_instruction.templ`
    
    These templates guide the agent's behavior during task execution.
    

## Memory Management

The agent utilizes both short-term and long-term memory to manage context and improve its responses.

* **Short-Term Memory:** Uses `ConversationBufferWindowMemory` to store recent interactions up to a specified window size (`max_thought_steps`).
* **Long-Term Memory:** Uses `ConversationSummaryMemory` to summarize conversations and, optionally, `VectorStoreRetrieverMemory` if a memory retriever is provided.

**Clearing Memory:**

* **After Task Completion:** Memory is cleared to ensure no residual data affects future tasks.
* **When Adding Discussions:** Memory remains intact to incorporate additional user inputs without losing previous context.


## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

1. **Fork the Repository**
    
2. **Create a Feature Branch**
    
    ```bash
    git checkout -b feature/YourFeature
    ```
    
3. **Commit Your Changes**
    
    ```bash
    git commit -m "Add Your Feature"
    ```
    
4. **Push to the Branch**
    
    ```bash
    git push origin feature/YourFeature
    ```
    
5. **Open a Pull Request**
    

## License

This project is licensed under the MIT License.

* * *

**Disclaimer:** Ensure that you handle API keys securely and adhere to the usage policies of OpenAI and SerpAPI. This project is intended for educational and authorized cybersecurity purposes only. Unauthorized access or misuse may lead to legal consequences.
