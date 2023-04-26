import tkinter as tk
import requests
import json
import uuid
import threading
from tkinter import messagebox


def close_app():
    window.destroy()


# 获取公网IP
def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org")
        return response.text
    except Exception as e:
        print(f"Error: {e}")
        return None
    
# 生成全局唯一的sessionId
def generate_session_id():
    return str(uuid.uuid4())

def update_ui(result):
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, result)
    query_button.config(state=tk.NORMAL)
    loading_label.config(text="")

# 请求API的函数
def request_api(query_text):
    url = "https://api.openai-proxy.com/pro/chat/completions"

    payload = json.dumps({
        "apiKey": "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",
        "sessionId": "8d1cb9b0-d535-43a8-b738-4f61b1608579",
        "content": query_text
    })

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=60)
        response_data = json.loads(response.text)
        result = f"查询结果：{response_data['data']}"
        # 更新UI
        
    except requests.exceptions.Timeout:
        window.after(0, handle_timeout)

     # 更新UI
    window.after(0, update_ui, result)

    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, result)
    query_button.config(state=tk.NORMAL)
    loading_label.config(text="")

# 在后台线程中运行请求API的函数
def start_request_api_thread():
    query_text = input_text.get(1.0, tk.END).strip()
    query_button.config(state=tk.DISABLED)
    loading_label.config(text="Loading...")
    threading.Thread(target=request_api, args=(query_text,)).start()

# 查询按钮的回调函数
def on_query_click():
    start_request_api_thread()

# 创建主窗口
window = tk.Tk()
window.title("eBest ChatGPT")
window.geometry("1200x600")

# 设定字体和颜色
font_family = "Helvetica"
font_size = 14
font = (font_family, font_size)
bg_color = "#1c1c1c"
fg_color = "#ffffff"
highlight_color = "#42a5f5"

# 创建左侧输入区域
input_frame = tk.Frame(window, bg=bg_color)
input_frame.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)

input_label = tk.Label(input_frame, text="请输入您的问题：", font=font, bg=bg_color, fg=fg_color)
input_label.pack()

input_text = tk.Text(input_frame, width=60, height=20, wrap=tk.WORD, font=font, bg=bg_color, fg=fg_color)
input_text.pack(expand=True, fill=tk.BOTH)

# 查询按钮
query_button = tk.Button(input_frame, text="提问", command=on_query_click, font=font, bg=highlight_color, fg=fg_color)
query_button.pack(pady=10)

# 处理API访问超时
def handle_timeout():
    messagebox.showerror("超时", "接口调用超时，小主稍后再试")
    query_button.config(state=tk.NORMAL)
    loading_label.config(text="")

# 获取外网IP
public_ip = get_public_ip()


# 检查IP是否为180.166.98.82
if public_ip != "180.166.98.82":
    query_button.config(state=tk.DISABLED)
    messagebox.showerror("访问限制", "该App仅限eBest内部使用")
    close_app()

# 创建右侧输出区域
output_frame = tk.Frame(window, bg=bg_color)
output_frame.pack(side=tk.RIGHT, padx=10, pady=10, expand=True, fill=tk.BOTH)

output_label = tk.Label(output_frame, text="查询结果：", font=font, bg=bg_color, fg=fg_color)
output_label.pack()

output_text = tk.Text(output_frame, width=60, height=20, wrap=tk.WORD, font=font, bg=bg_color, fg=fg_color)
output_text.pack(expand=True, fill=tk.BOTH)

# Loading 标签
loading_label = tk.Label(input_frame, text="", font=font, bg=bg_color, fg=fg_color)
loading_label.pack()


# 运行主循环
window.mainloop()