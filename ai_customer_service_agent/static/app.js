const sessionId = "web-" + Math.random().toString(36).slice(2);

function addMessage(text, role, meta = "") {
  const box = document.getElementById("messages");
  const div = document.createElement("div");
  div.className = "msg " + role;
  div.textContent = text;

  if (meta) {
    const m = document.createElement("div");
    m.className = "meta";
    m.textContent = meta;
    div.appendChild(m);
  }

  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById("input");
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: text, session_id: sessionId})
    });

    const data = await res.json();
    const meta = `意图：${data.intent} ｜ ${data.need_human ? "建议转人工" : "AI可处理"} ｜ 检索片段：${data.retrieved_docs.length}`;
    addMessage(data.answer, "bot", meta);
  } catch (e) {
    addMessage("请求失败，请检查后端服务是否正常启动。", "bot");
  }
}

document.getElementById("input").addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});
