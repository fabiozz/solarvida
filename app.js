// state
let db = {
  users: [{ id: 1, name: "demo", email: "demo@solarvida.com", pwd: "demo123" }],
  sims: [],
  nextId: 1
};

let currentUser = null;

// AUTH
function doLogin() {
  const email = document.getElementById("loginEmail").value;
  const pwd = document.getElementById("loginPwd").value;

  const u = db.users.find(u => u.email === email && u.pwd === pwd);
  if (!u) return document.getElementById("loginError").style.display = "block";

  currentUser = u;
  document.getElementById("authOverlay").style.display = "none";
  document.getElementById("userNameBadge").textContent = u.name;
}

// NAV
function showView(v) {
  document.querySelectorAll(".view").forEach(x => x.classList.remove("active"));
  document.getElementById("view" + v.charAt(0).toUpperCase() + v.slice(1)).classList.add("active");
}

// SIM
function salvarSimulacao() {
  const nome = document.getElementById("fNome").value;
  const consumo = +document.getElementById("fConsumo").value;
  const fatura = +document.getElementById("fFatura").value;

  db.sims.push({
    id: (++db.nextId),
    userId: currentUser.id,
    nome,
    consumo,
    fatura
  });

  renderSidebar();
}

// RENDER
function renderSidebar() {
  const el = document.getElementById("simList");
  el.innerHTML = db.sims.map(s =>
    `<div onclick="showDetalhe(${s.id})">${s.nome}</div>`
  ).join("");
}

function showDetalhe(id) {
  const s = db.sims.find(x => x.id === id);
  document.getElementById("detalheContent").innerHTML =
    `<h2>${s.nome}</h2>`;
}

function doLogout() {
  currentUser = null;
  document.getElementById("authOverlay").style.display = "flex";
}

// init
renderSidebar();