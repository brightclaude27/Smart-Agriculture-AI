import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# Shyiramo API Key yawe ya OpenAI (cyangwa uyishyire muri Environment Variables kuri Render)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Nta butumwa bwoherejwe"}), 400

    try:
        # Dukoresheje Responses API ya OpenAI ifite Web Search kugira ngo itange amakuru yizewe
        response = client.responses.create(
            model="gpt-4o",
            tools=[{"type": "web_search_preview"}],
            input=[
                {
                    "role": "system",
                    "content": (
                        "Uri umujyanama w'ubuhinzi witwa Smart Agriculture AI. "
                        "Subiza ibibazo mu Kinyarwanda cyiza, kandi ukoreshe amakuru yizewe "
                        "avuye mu bushakashatsi bw'ubuhinzi (nka RAB, FAO). "
                        "Niba umuntu aguhaye ibipimo bya N, P, K, ubushyuhe na pH, mufashe kubisesengura."
                    )
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        reply = response.output_text
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Habayemo ikibazo: {str(e)}"}), 500

# Urupapuro rwa Chat Box (Frontend)
@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

# Kode ya HTML/CSS/JS ya Chat Box
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="rw">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Agriculture AI - Chat</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f4f1; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .chat-container { width: 400px; max-width: 95%; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; display: flex; flex-direction: column; height: 80vh; }
        .chat-header { background: #2e7d32; color: white; padding: 15px; text-align: center; font-weight: bold; font-size: 18px; }
        .chat-box { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .message { padding: 10px 14px; border-radius: 10px; max-width: 80%; line-height: 1.4; font-size: 14px; }
        .user { background: #dcf8c6; align-self: flex-end; color: #111; }
        .bot { background: #f1f0f0; align-self: flex-start; color: #111; }
        .input-area { display: flex; border-top: 1px solid #ddd; padding: 10px; background: #fff; }
        input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 20px; outline: none; }
        button { background: #2e7d32; color: white; border: none; padding: 10px 18px; margin-left: 8px; border-radius: 20px; cursor: pointer; font-weight: bold; }
        button:hover { background: #1b5e20; }
    </style>
</head>
<body>

<div class="chat-container">
    <div class="chat-header">🌱 Smart Agriculture AI</div>
    <div class="chat-box" id="chatBox">
        <div class="message bot">Muraho! Ndi Smart Agriculture AI. Mbaza ikibazo cyose ku buhinzi cyangwa umpe ibipimo by'ubutaka bwawe (N, P, K, pH).</div>
    </div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Andika ikibazo cyawe hano..." onkeypress="if(event.key==='Enter') sendMessage()">
        <button onclick="sendMessage()">Ohereza</button>
    </div>
</div>

<script>
    async function sendMessage() {
        const input = document.getElementById("userInput");
        const chatBox = document.getElementById("chatBox");
        const text = input.value.trim();
        if (!text) return;

        // Erekana ubutumwa bw'umukoresha
        chatBox.innerHTML += `<div class="message user">${text}</div>`;
        input.value = "";
        chatBox.scrollTop = chatBox.scrollHeight;

        // Erekana ko AI iri gutekereza
        const loadingId = "loading-" + Date.now();
        chatBox.innerHTML += `<div class="message bot" id="${loadingId}">Irashakisha igisubizo...</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();
            document.getElementById(loadingId).innerText = data.reply;
        } catch (error) {
            document.getElementById(loadingId).innerText = "Habayemo ikibazo cyo guhura na seriveri.";
        }
        chatBox.scrollTop = chatBox.scrollHeight;
    }
</script>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
