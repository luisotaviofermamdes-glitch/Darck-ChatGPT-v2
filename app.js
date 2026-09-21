const $ = s => document.querySelector(s);

const chatKey = "darck-v2-chats";
const apiKey = "darck-v2-api";
const modelKey = "darck-v2-model";

let chats = [];
let currentId = null;
let model = localStorage.getItem(modelKey) || "Darck V2";
let busy = false;

try {
  chats = JSON.parse(localStorage.getItem(chatKey) || "[]");
  if (!Array.isArray(chats)) chats = [];
} catch {
  chats = [];
}

const save = () => localStorage.setItem(chatKey, JSON.stringify(chats));

const toast = text => {
  const e = $("#toast");
  if (!e) return;
  e.textContent = text;
  e.classList.add("show");
  setTimeout(() => e.classList.remove("show"), 1800);
};

function renderHistory() {
  const h = $("#history");
  h.innerHTML = "";

  chats.slice().reverse().forEach(c => {
    const b = document.createElement("button");
    b.className = "history-item" + (c.id === currentId ? " active" : "");
    b.textContent = c.title || "Nova conversa";
    b.onclick = () => loadChat(c.id);
    h.appendChild(b);
  });
}

function newChat() {
  const chat = {
    id: Date.now(),
    title: "Nova conversa",
    messages: []
  };

  chats.push(chat);
  currentId = chat.id;
  save();
  renderHistory();
  renderMessages();
}

function loadChat(id) {
  currentId = id;
  renderHistory();
  renderMessages();
  $("#sidebar").classList.remove("open");
}

function current() {
  return chats.find(c => c.id === currentId);
}

function renderMessages() {
  const c = current();

  $("#messages").innerHTML = "";
  $("#welcome").style.display =
    c && c.messages.length ? "none" : "block";

  (c?.messages || []).forEach(m =>
    addMessage(m.role, m.content, false)
  );

  $("#chat").scrollTop = $("#chat").scrollHeight;
}

function addMessage(role, text, scroll = true) {
  const row = document.createElement("div");
  row.className = "message-row " + role;

  const av = document.createElement("div");
  av.className = "msg-avatar";
  av.textContent = role === "user" ? "U" : "✦";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  if (role === "assistant") {
    row.append(av, bubble);
  } else {
    row.append(bubble);
  }

  $("#messages").append(row);

  if (scroll) {
    $("#chat").scrollTop = $("#chat").scrollHeight;
  }

  return row;
}

function fakeReply(q) {
  const l = q.toLowerCase();

  if (l.includes("html") || l.includes("site")) {
    return "Claro! Posso criar a estrutura HTML, CSS e JavaScript completa. Conecte uma API real em Configuração da IA para obter respostas geradas por um modelo.";
  }

  if (l.includes("ia") || l.includes("inteligência")) {
    return "O Darck ChatGPT V2 está preparado para usar uma IA real. Configure uma API compatível ou um servidor local e as mensagens serão enviadas para ele.";
  }

  if (l.includes("program")) {
    return "Vamos programar juntos. Posso trabalhar com HTML, CSS, JavaScript, Python, Java, Lua e outras linguagens quando uma IA real estiver conectada.";
  }

  return "O Darck ChatGPT V2 está funcionando. Para respostas geradas por IA, configure o endpoint da API no botão •••.";
}

function getApiEndpoint() {
  return localStorage.getItem(apiKey) || "/api/chat";
}

async function realAI(messages) {
  const endpoint = getApiEndpoint();

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model,
      messages,
      stream: false
    })
  });

  if (!response.ok) {
    throw new Error("API HTTP " + response.status);
  }

  const data = await response.json();

  const answer =
    data?.message?.content ??
    data?.choices?.[0]?.message?.content ??
    data?.response ??
    data?.content ??
    data?.text ??
    "";

  if (!String(answer).trim()) {
    throw new Error("A API não retornou texto.");
  }

  return String(answer);
}

async function send() {
  if (busy) return;

  const input = $("#input");
  const q = input.value.trim();

  if (!q) return;

  if (!currentId) newChat();

  const c = current();

  c.messages.push({
    role: "user",
    content: q
  });

  if (c.title === "Nova conversa") {
    c.title = q.slice(0, 42);
  }

  input.value = "";
  input.style.height = "auto";
  $("#welcome").style.display = "none";

  addMessage("user", q);
  renderHistory();
  save();

  busy = true;

  const row = document.createElement("div");
  row.className = "message-row assistant";
  row.innerHTML =
    '<div class="msg-avatar">✦</div>' +
    '<div class="bubble typing">' +
    "<span></span><span></span><span></span>" +
    "</div>";

  $("#messages").append(row);
  $("#chat").scrollTop = $("#chat").scrollHeight;

  let answer;

  try {
    answer = await realAI(c.messages);
  } catch (error) {
    console.warn("IA real indisponível:", error);
    answer = fakeReply(q);
  }

  row.querySelector(".bubble").className = "bubble";
  row.querySelector(".bubble").textContent = answer;

  c.messages.push({
    role: "assistant",
    content: answer
  });

  save();
  renderHistory();
  busy = false;
}

function setModel(nextModel) {
  model = nextModel;
  localStorage.setItem(modelKey, model);
  $("#modelName").textContent = model;
}

function configureAPI() {
  const currentEndpoint = getApiEndpoint();

  const endpoint = prompt(
    "Endpoint da API de IA:\n\n" +
    "Exemplo local: http://127.0.0.1:11434/api/chat\n" +
    "Ou seu backend: https://seu-servidor/api/chat\n\n" +
    "Deixe vazio para usar /api/chat.",
    currentEndpoint === "/api/chat" ? "" : currentEndpoint
  );

  if (endpoint === null) return;

  const value = endpoint.trim();

  if (value) {
    localStorage.setItem(apiKey, value);
    toast("API configurada");
  } else {
    localStorage.removeItem(apiKey);
    toast("API padrão restaurada");
  }
}

$("#newChat").onclick = newChat;
$("#sendBtn").onclick = send;

$("#input").addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});

$("#input").addEventListener("input", e => {
  e.target.style.height = "auto";
  e.target.style.height =
    Math.min(e.target.scrollHeight, 150) + "px";
});

$("#menuBtn").onclick = () =>
  $("#sidebar").classList.toggle("open");

$("#modelBtn").onclick = () =>
  $("#modelMenu").classList.toggle("hidden");

document.querySelectorAll("[data-model]").forEach(b => {
  b.onclick = () => {
    setModel(b.dataset.model);
    $("#modelMenu").classList.add("hidden");
    toast("Modelo: " + model);
  };
});

$("#themeBtn").onclick = () => {
  document.body.classList.toggle("light");
  toast("Tema alternado");
};

$("#clearBtn").onclick = () => {
  if (!confirm("Apagar todas as conversas?")) return;

  chats = [];
  currentId = null;
  save();
  newChat();
  toast("Histórico apagado");
};

$("#shareBtn").onclick = async () => {
  try {
    await navigator.clipboard.writeText(location.href);
    toast("Link copiado");
  } catch {
    toast("Não foi possível copiar");
  }
};

$("#attachBtn").onclick = () =>
  toast("Anexos podem ser conectados ao backend");

$("#micBtn").onclick = () => {
  const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    toast("Seu navegador não suporta voz");
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = "pt-BR";
  recognition.interimResults = false;

  recognition.onresult = event => {
    $("#input").value =
      event.results[0][0].transcript;
    $("#input").dispatchEvent(new Event("input"));
  };

  recognition.onerror = () =>
    toast("Erro no reconhecimento de voz");

  recognition.start();
  toast("Escutando...");
};

$("#moreBtn").onclick = configureAPI;

document.querySelectorAll("[data-prompt]").forEach(b => {
  b.onclick = () => {
    $("#input").value = b.dataset.prompt;
    send();
  };
});

$("#modelName").textContent = model;

if (chats.length) {
  currentId = chats[chats.length - 1].id;
} else {
  newChat();
}

renderHistory();
renderMessages();
