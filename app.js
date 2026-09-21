const $=s=>document.querySelector(s);
const chatKey="darck-v2-chats";
let chats=JSON.parse(localStorage.getItem(chatKey)||"[]"), currentId=null, model="Darck V2", busy=false;
const save=()=>localStorage.setItem(chatKey,JSON.stringify(chats));
const toast=t=>{const e=$("#toast");e.textContent=t;e.classList.add("show");setTimeout(()=>e.classList.remove("show"),1800)};
function renderHistory(){const h=$("#history");h.innerHTML="";chats.slice().reverse().forEach(c=>{const b=document.createElement("button");b.className="history-item"+(c.id===currentId?" active":"");b.textContent=c.title||"Nova conversa";b.onclick=()=>loadChat(c.id);h.appendChild(b)})}
function newChat(){currentId=Date.now();chats.push({id:currentId,title:"Nova conversa",messages:[]});save();renderHistory();renderMessages()}
function loadChat(id){currentId=id;renderHistory();renderMessages();$("#sidebar").classList.remove("open")}
function current(){return chats.find(c=>c.id===currentId)}
function renderMessages(){const c=current();$("#messages").innerHTML="";$("#welcome").style.display=c&&c.messages.length?"none":"block";(c?.messages||[]).forEach(m=>addMessage(m.role,m.content,false));$("#chat").scrollTop=$("#chat").scrollHeight}
function addMessage(role,text,scroll=true){const row=document.createElement("div");row.className="message-row "+role;const av=document.createElement("div");av.className="msg-avatar";av.textContent=role==="user"?"U":"✦";const bubble=document.createElement("div");bubble.className="bubble";bubble.textContent=text;role==="assistant"?(row.append(av,bubble)):row.append(bubble);$("#messages").append(row);if(scroll)$("#chat").scrollTop=$("#chat").scrollHeight}
function fakeReply(q){const l=q.toLowerCase();if(l.includes("html")||l.includes("site"))return"Claro! Posso criar a estrutura HTML, CSS e JavaScript completa. Se quiser, diga o tipo de site e eu monto o projeto.";if(l.includes("ia")||l.includes("inteligência"))return"Inteligência artificial é um conjunto de técnicas que permite a computadores executar tarefas que normalmente exigem capacidades humanas, como interpretar texto, reconhecer padrões e gerar conteúdo.";if(l.includes("program"))return"Vamos programar juntos. Posso ajudar com HTML, CSS, JavaScript, Python, Java, Lua e outras linguagens.";return"Entendi. Esta é uma resposta de demonstração do Darck ChatGPT V2. Para respostas reais, conecte o frontend a uma API ou ao seu servidor de IA local."; }
async function send(){if(busy)return;const input=$("#input"),q=input.value.trim();if(!q)return;if(!currentId)newChat();const c=current();c.messages.push({role:"user",content:q});if(c.title==="Nova conversa")c.title=q.slice(0,42);input.value="";input.style.height="auto";$("#welcome").style.display="none";addMessage("user",q);renderHistory();save();busy=true;const row=document.createElement("div");row.className="message-row assistant";row.innerHTML='<div class="msg-avatar">✦</div><div class="bubble typing"><span></span><span></span><span></span></div>';$("#messages").append(row);$("#chat").scrollTop=$("#chat").scrollHeight;await new Promise(r=>setTimeout(r,650));const answer=fakeReply(q);row.querySelector(".bubble").className="bubble";row.querySelector(".bubble").textContent=answer;c.messages.push({role:"assistant",content:answer});save();busy=false;renderHistory()}
$("#newChat").onclick=newChat;$("#sendBtn").onclick=send;
$("#input").addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();send()}});
$("#input").addEventListener("input",e=>{e.target.style.height="auto";e.target.style.height=Math.min(e.target.scrollHeight,150)+"px"});
$("#menuBtn").onclick=()=>$("#sidebar").classList.toggle("open");
$("#modelBtn").onclick=()=>$("#modelMenu").classList.toggle("hidden");
document.querySelectorAll("[data-model]").forEach(b=>b.onclick=()=>{model=b.dataset.model;$("#modelName").textContent=model;$("#modelMenu").classList.add("hidden")});
$("#themeBtn").onclick=()=>{document.body.classList.toggle("light");toast("Tema alternado")};
$("#clearBtn").onclick=()=>{if(confirm("Apagar todas as conversas?")){chats=[];currentId=null;save();renderHistory();newChat()}};
$("#shareBtn").onclick=()=>{navigator.clipboard?.writeText(location.href);toast("Link copiado")};
$("#attachBtn").onclick=()=>toast("Anexos: disponível para conectar ao backend");
$("#micBtn").onclick=()=>toast("Entrada de voz: conecte a Web Speech API");
document.querySelectorAll("[data-prompt]").forEach(b=>b.onclick=()=>{$("#input").value=b.dataset.prompt;send()});
if(chats.length)currentId=chats[chats.length-1].id;else newChat();renderHistory();renderMessages();