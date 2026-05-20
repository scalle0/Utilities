const log = document.getElementById("log");
const form = document.getElementById("form");
const input = document.getElementById("input");
const send = document.getElementById("send");
const statusEl = document.getElementById("status");

const history = [];

function addBubble(role, text = "") {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
  return div;
}

async function refreshStatus() {
  try {
    const r = await fetch("/health");
    const j = await r.json();
    statusEl.textContent = j.ok
      ? `model: ${j.model}`
      : `ollama unreachable: ${j.error ?? "?"}`;
  } catch (e) {
    statusEl.textContent = "server unreachable";
  }
}
refreshStatus();

async function sendMessage(text) {
  history.push({ role: "user", content: text });
  addBubble("user", text);
  const bubble = addBubble("assistant", "…");
  send.disabled = true;

  let assistantText = "";
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: history }),
    });
    if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const events = buf.split("\n\n");
      buf = events.pop();
      for (const evt of events) {
        if (!evt.startsWith("data:")) continue;
        const payload = evt.slice(5).trim();
        if (payload === "[DONE]") continue;
        try {
          const obj = JSON.parse(payload);
          if (obj.error) {
            bubble.textContent = `error: ${obj.error}`;
            return;
          }
          if (obj.delta) {
            if (assistantText === "") bubble.textContent = "";
            assistantText += obj.delta;
            bubble.textContent = assistantText;
            log.scrollTop = log.scrollHeight;
          }
        } catch {
          // ignore malformed event
        }
      }
    }
    if (assistantText) {
      history.push({ role: "assistant", content: assistantText });
    } else {
      bubble.textContent = "(no response)";
    }
  } catch (e) {
    bubble.textContent = `error: ${e.message}`;
  } finally {
    send.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  sendMessage(text);
});

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});
