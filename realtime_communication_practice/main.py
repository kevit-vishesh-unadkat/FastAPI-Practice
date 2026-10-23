from xmlrpc.client import FastParser

from fastapi import FastAPI,HTTPException,WebSocket,WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app=FastAPI()

# Connection Manager

class ConnectionManager:

        def __init__(self):
            self.active_connections = {}

        async def connect(self, websocket: WebSocket, username: str):
            await websocket.accept()
            self.active_connections[websocket] = username

        def disconnect(self, websocket: WebSocket):
            self.active_connections.pop(websocket, None)

        async def broadcast(self, message: dict):
            disconnected = []

            for connection in list(self.active_connections):
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)

            for connection in disconnected:
                self.disconnect(connection)

manager = ConnectionManager()


# Frontend
html = """
<!DOCTYPE html>
<html>
<head>
    <title>FastAPI Chat</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 700px;
            margin: 30px auto;
            padding: 15px;
            background: #f4f4f4;
        }

        h1 {
            text-align: center;
        }

        .panel {
            background: white;
            padding: 20px;
            border-radius: 10px;
        }

        input, button {
            padding: 10px;
            margin: 5px 0;
            box-sizing: border-box;
        }

        input {
            width: 100%;
        }

        button {
            cursor: pointer;
        }

        #messages {
            height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            margin: 15px 0;
            background: white;
        }

        .message {
            padding: 8px;
            margin-bottom: 8px;
            background: #eef2ff;
            border-radius: 5px;
            overflow-wrap: anywhere;
        }

        .system {
            color: #555;
            font-style: italic;
        }

        #status {
            font-weight: bold;
        }

        .chat-controls {
            display: flex;
            gap: 8px;
        }

        .chat-controls input {
            flex: 1;
            min-width: 0;
        }
    </style>
</head>

<body>

    <h1>FastAPI Real-Time Chat</h1>

    <div class="panel">

        <label for="username">Your username</label>
        <input
            id="username"
            placeholder="Enter your username"
            maxlength="20"
        >

        <button id="connectBtn">Connect to Chat</button>

        <p id="status">Disconnected</p>

        <div id="messages" aria-live="polite"></div>

        <form id="chatForm">
            <div class="chat-controls">
                <input
                    id="messageInput"
                    placeholder="Type a message..."
                    maxlength="500"
                    autocomplete="off"
                    disabled
                >

                <button id="sendBtn" type="submit" disabled>
                    Send
                </button>
            </div>
        </form>

    </div>

    <script>
        let socket = null;

        const usernameInput = document.getElementById("username");
        const connectBtn = document.getElementById("connectBtn");
        const status = document.getElementById("status");
        const messages = document.getElementById("messages");
        const messageInput = document.getElementById("messageInput");
        const chatForm = document.getElementById("chatForm");
        const sendBtn = document.getElementById("sendBtn");

        function addMessage(data) {
            const item = document.createElement("div");

            item.className = "message";

            if (data.type === "system") {
                item.classList.add("system");
                item.textContent = data.text;
            } else {
                const time = data.time
                    ? new Date(data.time).toLocaleTimeString()
                    : "";

                item.textContent =
                    "[" + time + "] " +
                    data.username + ": " +
                    data.text;
            }

            messages.appendChild(item);
            messages.scrollTop = messages.scrollHeight;
        }

        connectBtn.addEventListener("click", function () {
            const username = usernameInput.value.trim();

            if (!username) {
                alert("Please enter a username.");
                return;
            }

            if (socket && socket.readyState === WebSocket.OPEN) {
                alert("You are already connected.");
                return;
            }

            if (
                socket &&
                socket.readyState === WebSocket.CONNECTING
            ) {
                return;
            }

            const protocol =
                window.location.protocol === "https:"
                    ? "wss:"
                    : "ws:";

            const url =
                protocol + "//" + window.location.host +
                "/ws/" + encodeURIComponent(username);

            socket = new WebSocket(url);

            status.textContent = "Connecting...";

            socket.onopen = function () {
                status.textContent = "Connected as " + username;

                usernameInput.disabled = true;
                connectBtn.disabled = true;
                messageInput.disabled = false;
                sendBtn.disabled = false;

                messageInput.focus();
            };

            socket.onmessage = function (event) {
                const data = JSON.parse(event.data);
                addMessage(data);
            };

            socket.onclose = function () {
                status.textContent = "Disconnected";

                usernameInput.disabled = false;
                connectBtn.disabled = false;
                messageInput.disabled = true;
                sendBtn.disabled = true;

                socket = null;
            };

            socket.onerror = function () {
                status.textContent = "Connection error";
            };
        });

        chatForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const text = messageInput.value.trim();

            if (!text) {
                return;
            }

            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({
                    text: text
                }));

                messageInput.value = "";
                messageInput.focus();
            }
        });

        window.addEventListener("beforeunload", function () {
            if (socket) {
                socket.close();
            }
        });
    </script>

</body>
</html>
"""


# --------------------------------
# Home page
# --------------------------------

@app.get("/")
async def home():
    return HTMLResponse(html)


# --------------------------------
# WebSocket Chat
# --------------------------------

@app.websocket("/ws/{username}")
async def chat(websocket: WebSocket, username: str):

    username = username.strip()

    if not username or len(username) > 20:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, username)

    await manager.broadcast({
        "type": "system",
        "text": f"{username} joined the chat"
    })

    try:
        while True:

            raw_message = await websocket.receive_text()

            try:
                data = json.loads(raw_message)
            except ValueError:
                continue

            if not isinstance(data, dict):
                continue

            text = data.get("text")

            if not isinstance(text, str):
                continue

            text = text.strip()

            if not text or len(text) > 500:
                continue

            message = {
                "type": "chat_message",
                "username": username,
                "text": text,
                "time": __import__("datetime").datetime.now(
                    __import__("datetime").timezone.utc
                ).isoformat()
            }

            await manager.broadcast(message)

    except WebSocketDisconnect:

        manager.disconnect(websocket)

        await manager.broadcast({
            "type": "system",
            "text": f"{username} left the chat"
        })