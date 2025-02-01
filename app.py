from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import time
import re
import base64
from openai import OpenAI

app = Flask(__name__)
CORS(app)  # فعال‌سازی CORS

client = OpenAI(api_key="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")

@app.route("/")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message")

        if not user_message:
            return jsonify({"response": "لطفاً یک پیام وارد کنید."}), 400

        # ایجاد Thread جدید
        thread = client.beta.threads.create()

        # آماده‌سازی پیام
        messages = [{"role": "user", "content": user_message}]

        # ارسال پیام به Thread
        for message in messages:
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role=message["role"],
                content=message["content"]
            )

        # اجرای Assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id="asst_SNOcJrAYp0g5Wjtwg8v0A2Zr"
        )

        # منتظر بمانید تا Assistant پاسخ دهد
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            time.sleep(0.05)

        # دریافت پیام‌ها از Thread
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        assistant_messages = ""
        for message in messages.data:
            if message.role == "assistant":
                assistant_messages += message.content[0].text.value

        # پاک کردن خروجی از تگ‌ها
        cleaned_output = re.sub(r"【\d+:\d+†source】", "", assistant_messages)

        return jsonify({"response": cleaned_output}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": f"خطایی رخ داد: {str(e)}"}), 500


if __name__ == "__main__":
    app.run()
