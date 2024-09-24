import requests
import threading
import socketio

API_URL = 'http://localhost:8080'
task_running = False  # Used to track if a task is running


def print_menu():
    print("\n请选择一个选项：")
    print("1. 创建新任务")
    print("2. 查看当前命令列表")
    print("3. 修改命令列表")
    print("4. 确认并开始执行任务")
    print("5. 暂停任务")
    print("6. 恢复任务")
    print("7. 跳过当前命令")
    print("8. 与 GPT 讨论")
    print("9. 退出")


def create_task():
    task_description = input("请输入任务描述：")
    model_name = input("请输入模型名称（默认 'gpt-4'）：") or 'gpt-4'
    response = requests.post(f"{API_URL}/execute-task", json={
        'task_description': task_description,
        'model_name': model_name
    })
    data = response.json()
    if data['status'] == 'success':
        print("任务已创建。以下是生成的命令列表：")
        for i, cmd in enumerate(data['commands'], start=1):
            print(f"{i}. {cmd}")
        confirm = input("是否确认并开始执行任务？(y/n): ")
        if confirm.lower() == 'y':
            confirm_commands(confirmed=True, endpoint='/confirm-task')
        else:
            print("任务未确认。")
    else:
        print(f"错误：{data['message']}")


def confirm_commands(confirmed, endpoint):
    response = requests.post(f"{API_URL}{endpoint}", json={'confirmed': confirmed})
    data = response.json()
    if data['status'] == 'success':
        print(data['message'])
    else:
        print(f"错误：{data['message']}")


def view_commands():
    response = requests.get(f"{API_URL}/commands")
    data = response.json()
    if data['status'] == 'success':
        print("当前命令列表：")
        for i, cmd in enumerate(data['commands'], start=1):
            print(f"{i}. {cmd}")
    else:
        print(f"错误：{data['message']}")


def modify_commands():
    print("请输入新的命令列表，每个命令一行。输入空行结束：")
    new_commands = []
    while True:
        cmd = input()
        if cmd == '':
            break
        new_commands.append(cmd)
    response = requests.put(f"{API_URL}/commands", json={'commands': new_commands})
    data = response.json()
    if data['status'] == 'success':
        print("命令列表已更新。")
    else:
        print(f"错误：{data['message']}")


def confirm_and_start_task():
    confirm_commands(confirmed=True, endpoint='/confirm-task')


def pause_task():
    response = requests.post(f"{API_URL}/pause-task")
    data = response.json()
    if data['status'] == 'success':
        print("任务已暂停。")
    else:
        print(f"错误：{data['message']}")


def resume_task():
    response = requests.post(f"{API_URL}/resume-task")
    data = response.json()
    if data['status'] == 'success':
        print("任务已恢复。")
    else:
        print(f"错误：{data['message']}")


def skip_command():
    response = requests.post(f"{API_URL}/skip-command")
    data = response.json()
    if data['status'] == 'success':
        print("当前命令将被跳过。")
    else:
        print(f"错误：{data['message']}")


def discuss_with_gpt():
    message = input("请输入您想与 GPT 讨论的内容：")
    response = requests.post(f"{API_URL}/discuss", json={'message': message})
    data = response.json()
    if data['status'] == 'success':
        if 'commands' in data:
            print("根据讨论，生成了新的命令列表：")
            for i, cmd in enumerate(data['commands'], start=1):
                print(f"{i}. {cmd}")
            confirm = input("是否确认新的命令列表并开始执行？(y/n): ")
            if confirm.lower() == 'y':
                confirm_commands(confirmed=True, endpoint='/confirm-discuss')
            else:
                print("新的命令列表未确认。")
        else:
            print(f"GPT 回复：{data['response']}")
    else:
        print(f"错误：{data['message']}")


def start_socketio_client():
    sio = socketio.Client()

    @sio.event
    def connect():
        print('已连接到服务器，实时输出将显示在这里。')

    @sio.event
    def command_output(data):
        print(f"\n命令输出 [{data['command']}]:\n{data['output']}")

    @sio.event
    def task_summary(data):
        print('\n任务总结:')
        print(data['summary'])

    @sio.event
    def disconnect():
        print('与服务器的连接已断开。')

    try:
        sio.connect(API_URL)
        sio.wait()
    except Exception as e:
        print(f"SocketIO 连接错误：{e}")


def main():
    global task_running
    # 启动 SocketIO 客户端线程
    threading.Thread(target=start_socketio_client, daemon=True).start()

    while True:
        print_menu()
        choice = input("请输入数字选择：")
        if choice == '1':
            create_task()
        elif choice == '2':
            view_commands()
        elif choice == '3':
            modify_commands()
        elif choice == '4':
            confirm_and_start_task()
            task_running = True
            while task_running:
                command = input("任务正在运行。输入 'p' 暂停并返回菜单：")
                if command.lower() == 'p':
                    pause_task()
                    task_running = False
                else:
                    print("无效的输入，请输入 'p' 以暂停。")
        elif choice == '5':
            pause_task()
        elif choice == '6':
            resume_task()
        elif choice == '7':
            skip_command()
        elif choice == '8':
            discuss_with_gpt()
        elif choice == '9':
            print("退出程序。")
            break
        else:
            print("无效的选择，请重新输入。")


if __name__ == '__main__':
    main()
