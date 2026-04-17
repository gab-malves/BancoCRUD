/**
 * app.js — BancoCRUD Front-end
 *
 * Integração com app_api.py (Flask em localhost:5000).
 * Modo offline/demo disponível sem servidor rodando.
 */

// ─────────────────────────────────────────────────────────────────────────────
// CONFIGURAÇÃO
// ─────────────────────────────────────────────────────────────────────────────
const API = "http://localhost:5000";

// Estado global da sessão
let sessao = {
  usuario: null,   // { username, nome, banco, conta_num }
  offline: false,  // true = modo demo sem servidor
};

// Banco em memória (apenas modo offline)
const demo = { contas: {}, transacoes: {} };

// ─────────────────────────────────────────────────────────────────────────────
// UTILITÁRIOS
// ─────────────────────────────────────────────────────────────────────────────
const fmt = (v) =>
  "R$ " +
  Number(v)
    .toFixed(2)
    .replace(".", ",")
    .replace(/\B(?=(\d{3})+(?!\d))/g, ".");

function showAlerta(id, msg, tipo = "info") {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.className = `alerta ${tipo}`;
  el.style.display = "block";
  setTimeout(() => (el.style.display = "none"), 5000);
}

function ocultarAlerta(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = "none";
}

async function apiFetch(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    ...options,
  });
  return await res.json();
}

// ─────────────────────────────────────────────────────────────────────────────
// ROTEAMENTO DE TELAS
// ─────────────────────────────────────────────────────────────────────────────
function irTela(id) {
  document.querySelectorAll(".tela").forEach((t) => t.classList.remove("ativa"));
  document.getElementById(id).classList.add("ativa");
}

function irAba(nome) {
  document.querySelectorAll(".aba").forEach((a) => a.classList.remove("ativa"));
  document.querySelectorAll(".nav-tab").forEach((t) => t.classList.remove("ativo"));
  document.getElementById("aba-" + nome).classList.add("ativa");
  document.querySelector(`[data-aba="${nome}"]`).classList.add("ativo");

  if (nome === "dashboard") carregarDashboard();
  if (nome === "contas") carregarListaContas();
}

// ─────────────────────────────────────────────────────────────────────────────
// LOGIN
// ─────────────────────────────────────────────────────────────────────────────
function mostrarFormLogin() {
  document.getElementById("tab-login-btn").classList.add("ativo");
  document.getElementById("tab-cad-btn").classList.remove("ativo");
}

async function fazerLogin() {
  const username = document.getElementById("login-user").value.trim();
  const senha = document.getElementById("login-senha").value.trim();

  if (!username || !senha) {
    return showAlerta("alerta-login", "Preencha usuário e senha.", "erro");
  }

  try {
    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, senha }),
    });

    if (!data.sucesso) {
      return showAlerta("alerta-login", data.mensagem, "erro");
    }

    sessao.usuario = data.usuario;
    sessao.offline = false;
    entrarNoApp();
  } catch (e) {
    showAlerta(
      "alerta-login",
      "Não foi possível conectar ao servidor. Use o modo demo.",
      "erro"
    );
  }
}

function usarModoOffline() {
  sessao.usuario = {
    username: "demo",
    nome: "Usuário Demo",
    banco: "—",
    conta_num: "demo",
  };
  sessao.offline = true;
  entrarNoApp();
}

function entrarNoApp() {
  document.getElementById("header-user").textContent =
    "Olá, " + sessao.usuario.nome;
  irTela("tela-app");
  carregarDashboard();
}

async function fazerLogout() {
  if (!sessao.offline) {
    try { await apiFetch("/auth/logout", { method: "POST" }); } catch (_) {}
  }
  sessao = { usuario: null, offline: false };
  irTela("tela-login");
  document.getElementById("login-user").value = "";
  document.getElementById("login-senha").value = "";
}

// ─────────────────────────────────────────────────────────────────────────────
// CADASTRO — navegação entre etapas
// ─────────────────────────────────────────────────────────────────────────────
let bancoCadastro = "";

function irParaCadastro() {
  irTela("tela-cadastro");
  irEtapa1();
}

function voltarLogin() {
  irTela("tela-login");
}

function irEtapa1() {
  document.getElementById("etapa-1").style.display = "block";
  document.getElementById("etapa-2").style.display = "none";
  document.getElementById("etapa-3").style.display = "none";
}

function irEtapa2() {
  const user = document.getElementById("cad-user").value.trim();
  const senha = document.getElementById("cad-senha").value.trim();
  if (!user || !senha) {
    return alert("Preencha usuário e senha.");
  }
  document.getElementById("etapa-1").style.display = "none";
  document.getElementById("etapa-2").style.display = "block";
  document.getElementById("etapa-3").style.display = "none";
}

function irEtapa3() {
  const nome = document.getElementById("cad-nome").value.trim();
  if (!nome) return alert("Informe o nome completo.");
  document.getElementById("etapa-1").style.display = "none";
  document.getElementById("etapa-2").style.display = "none";
  document.getElementById("etapa-3").style.display = "block";
}

function selecionarBanco(el) {
  document.querySelectorAll(".banco-card").forEach((c) =>
    c.classList.remove("selecionado")
  );
  el.classList.add("selecionado");
  bancoCadastro = el.dataset.banco;
}

// Busca CEP via API (proxy no Flask evita CORS)
async function buscarCep() {
  const cep = document.getElementById("cad-cep").value.replace(/\D/g, "");
  if (cep.length !== 8) {
    return showAlerta("alerta-cep", "CEP deve ter 8 dígitos.", "erro");
  }

  showAlerta("alerta-cep", "Buscando endereço...", "info");

  try {
    let data;
    if (sessao.offline) {
      // Em modo offline faz a chamada direta ao ViaCEP
      const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
      const raw = await res.json();
      if (raw.erro) throw new Error("CEP não encontrado.");
      data = {
        sucesso: true,
        logradouro: raw.logradouro,
        bairro: raw.bairro,
        cidade: raw.localidade,
        uf: raw.uf,
      };
    } else {
      data = await apiFetch(`/cep/${cep}`);
    }

    if (!data.sucesso) {
      return showAlerta("alerta-cep", data.mensagem, "erro");
    }

    document.getElementById("cad-logradouro").value = data.logradouro;
    document.getElementById("cad-bairro").value = data.bairro;
    document.getElementById("cad-cidade").value = data.cidade;
    document.getElementById("cad-uf").value = data.uf;
    document.getElementById("campos-endereco").style.display = "flex";
    document.getElementById("campos-cidade").style.display = "flex";
    ocultarAlerta("alerta-cep");
  } catch (e) {
    showAlerta("alerta-cep", e.message || "Erro ao buscar CEP.", "erro");
  }
}

// Formata CPF enquanto digita
document.addEventListener("DOMContentLoaded", () => {
  const cpfInput = document.getElementById("cad-cpf");
  if (cpfInput) {
    cpfInput.addEventListener("input", (e) => {
      let v = e.target.value.replace(/\D/g, "");
      v = v.replace(/(\d{3})(\d)/, "$1.$2");
      v = v.replace(/(\d{3})(\d)/, "$1.$2");
      v = v.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
      e.target.value = v;
    });
  }

  // Formata CEP enquanto digita
  const cepInput = document.getElementById("cad-cep");
  if (cepInput) {
    cepInput.addEventListener("input", (e) => {
      let v = e.target.value.replace(/\D/g, "");
      v = v.replace(/^(\d{5})(\d)/, "$1-$2");
      e.target.value = v;
    });
  }
});

async function finalizarCadastro() {
  const username = document.getElementById("cad-user").value.trim();
  const senha = document.getElementById("cad-senha").value.trim();
  const nome = document.getElementById("cad-nome").value.trim();
  const data_nasc = document.getElementById("cad-nasc").value;
  const cpf = document.getElementById("cad-cpf").value.trim();
  const cep = document.getElementById("cad-cep").value.trim();
  const logradouro = document.getElementById("cad-logradouro").value;
  const bairro = document.getElementById("cad-bairro").value;
  const cidade = document.getElementById("cad-cidade").value;
  const uf = document.getElementById("cad-uf").value;
  const saldo_ini = parseFloat(document.getElementById("cad-saldo").value) || 0;

  if (!bancoCadastro) {
    return showAlerta("alerta-cad", "Selecione um banco.", "erro");
  }

  if (sessao.offline) {
    // Modo demo: simula cadastro em memória
    if (demo.contas[username]) {
      return showAlerta("alerta-cad", "Usuário já existe.", "erro");
    }
    demo.contas[username] = { numero: username, titular: nome, saldo: saldo_ini };
    demo.transacoes[username] = [];
    sessao.usuario = { username, nome, banco: bancoCadastro, conta_num: username };
    document.getElementById("header-user").textContent = "Olá, " + nome;
    irTela("tela-app");
    carregarDashboard();
    return;
  }

  try {
    const data = await apiFetch("/auth/registrar", {
      method: "POST",
      body: JSON.stringify({
        username, senha, nome, data_nasc, cpf, cep,
        logradouro, bairro, cidade, uf,
        banco: bancoCadastro, saldo_ini,
      }),
    });

    if (!data.sucesso) {
      return showAlerta("alerta-cad", data.mensagem, "erro");
    }

    showAlerta("alerta-cad", "Conta criada! Fazendo login...", "sucesso");

    setTimeout(async () => {
      const loginData = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, senha }),
      });
      if (loginData.sucesso) {
        sessao.usuario = loginData.usuario;
        sessao.offline = false;
        entrarNoApp();
      }
    }, 1200);
  } catch (e) {
    showAlerta("alerta-cad", "Erro ao conectar ao servidor.", "erro");
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// DASHBOARD
// ─────────────────────────────────────────────────────────────────────────────
async function carregarDashboard() {
  try {
    let contas = [];

    if (sessao.offline) {
      contas = Object.values(demo.contas);
    } else {
      const data = await apiFetch("/dashboard");
      if (data.sucesso) {
        contas = data.contas || [];
        document.getElementById("dash-saldo-total").textContent = fmt(data.saldo_total);
        document.getElementById("dash-num-contas").textContent = data.num_contas;
        document.getElementById("dash-saldo-sub").textContent =
          data.num_contas === 1 ? "em 1 conta" : `em ${data.num_contas} contas`;
        renderDashResumo(contas);
        renderGrafico(contas);
        return;
      }
    }

    // Fallback para modo offline
    const total = contas.reduce((s, c) => s + (c.saldo || 0), 0);
    document.getElementById("dash-saldo-total").textContent = fmt(total);
    document.getElementById("dash-num-contas").textContent = contas.length;
    document.getElementById("dash-saldo-sub").textContent =
      contas.length === 1 ? "em 1 conta" : `em ${contas.length} contas`;
    renderDashResumo(contas);
    renderGrafico(contas);
  } catch (_) {
    // Sem servidor — mantém valores padrão
  }
}

function renderDashResumo(contas) {
  const el = document.getElementById("dash-resumo");
  if (!contas.length) {
    el.innerHTML = '<span style="color:var(--text3)">Nenhuma conta cadastrada.</span>';
    return;
  }
  const maior = contas.reduce((a, b) => (a.saldo > b.saldo ? a : b));
  el.innerHTML = `
    <div>Total de contas: <strong>${contas.length}</strong></div>
    <div>Maior saldo: <strong style="color:var(--success)">${fmt(maior.saldo)}</strong></div>
    <div>Titular: ${maior.titular || maior.numero}</div>
  `;
}

function renderGrafico(contas) {
  const wrap = document.getElementById("grafico-barras");
  if (!contas.length) {
    wrap.innerHTML = '<p class="grafico-vazio">Nenhuma conta cadastrada.</p>';
    return;
  }

  const max = Math.max(...contas.map((c) => c.saldo || 0), 1);
  const ALT_MAX = 100; // px

  wrap.innerHTML = contas
    .slice(0, 12) // limita a 12 barras
    .map((c) => {
      const pct = ((c.saldo || 0) / max) * ALT_MAX;
      return `
        <div class="grafico-barra-wrap">
          <div class="grafico-valor">${fmt(c.saldo || 0)}</div>
          <div class="grafico-barra" style="height:${Math.max(pct, 4)}px"></div>
          <div class="grafico-label">#${c.numero || c.numero}</div>
        </div>
      `;
    })
    .join("");
}

// ─────────────────────────────────────────────────────────────────────────────
// CONTAS
// ─────────────────────────────────────────────────────────────────────────────
async function criarConta() {
  const numero = document.getElementById("c-num").value.trim();
  const titular = document.getElementById("c-nome").value.trim();
  const saldo = parseFloat(document.getElementById("c-saldo").value) || 0;

  if (!numero || !titular) {
    return showAlerta("alerta-criar", "Número e titular são obrigatórios.", "erro");
  }

  try {
    let data;
    if (sessao.offline) {
      if (demo.contas[numero]) {
        data = { sucesso: false, mensagem: "Conta já existe." };
      } else {
        demo.contas[numero] = { numero, titular, saldo };
        demo.transacoes[numero] = [];
        data = { sucesso: true, mensagem: "Conta criada com sucesso!" };
      }
    } else {
      data = await apiFetch("/contas", {
        method: "POST",
        body: JSON.stringify({ numero, titular, saldo }),
      });
    }

    showAlerta("alerta-criar", data.mensagem, data.sucesso ? "sucesso" : "erro");
    if (data.sucesso) {
      document.getElementById("c-num").value = "";
      document.getElementById("c-nome").value = "";
      document.getElementById("c-saldo").value = "";
      carregarListaContas();
      carregarDashboard();
    }
  } catch (e) {
    showAlerta("alerta-criar", "Erro ao comunicar com a API.", "erro");
  }
}

async function carregarListaContas() {
  const lista = document.getElementById("lista-contas");
  try {
    let contas = [];
    if (sessao.offline) {
      contas = Object.values(demo.contas);
    } else {
      const data = await apiFetch("/contas");
      contas = data.contas || [];
    }

    if (!contas.length) {
      lista.innerHTML = '<p class="lista-vazia">Nenhuma conta cadastrada.</p>';
      return;
    }

    lista.innerHTML = contas
      .map(
        (c) => `
          <div class="conta-item">
            <div>
              <div class="conta-num">#${c.numero}</div>
              <div class="conta-name">${c.titular || c.info || ""}</div>
            </div>
            <div class="conta-saldo">${fmt(c.saldo || 0)}</div>
          </div>
        `
      )
      .join("");
  } catch (_) {
    lista.innerHTML = '<p class="lista-vazia">Erro ao carregar contas.</p>';
  }
}

async function excluirConta() {
  const numero = document.getElementById("del-num").value.trim();
  if (!numero) return showAlerta("alerta-del", "Informe o número da conta.", "erro");
  if (!confirm(`Excluir a conta ${numero}? Esta ação não pode ser desfeita.`)) return;

  try {
    let data;
    if (sessao.offline) {
      if (!demo.contas[numero]) {
        data = { sucesso: false, mensagem: "Conta não encontrada." };
      } else {
        delete demo.contas[numero];
        delete demo.transacoes[numero];
        data = { sucesso: true, mensagem: "Conta excluída." };
      }
    } else {
      data = await apiFetch(`/contas/${numero}`, { method: "DELETE" });
    }

    showAlerta("alerta-del", data.mensagem, data.sucesso ? "sucesso" : "erro");
    if (data.sucesso) {
      document.getElementById("del-num").value = "";
      carregarListaContas();
      carregarDashboard();
    }
  } catch (e) {
    showAlerta("alerta-del", "Erro ao comunicar com a API.", "erro");
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// OPERAÇÕES
// ─────────────────────────────────────────────────────────────────────────────
let opAtual = "deposito";

function setOp(op) {
  opAtual = op;
  const labels = {
    deposito: "Depositar",
    saque: "Sacar",
    pix: "Enviar PIX",
    transferencia: "Transferir",
  };
  const origens = {
    deposito: "Conta",
    saque: "Conta",
    pix: "Conta de origem",
    transferencia: "Conta de origem",
  };

  document.querySelectorAll(".op-tab").forEach((t) => t.classList.remove("ativo"));
  const btn = document.getElementById(`op-tab-${op}`);
  if (btn) btn.classList.add("ativo");

  document.getElementById("btn-executar-op").textContent = labels[op];
  document.getElementById("label-conta-origem").textContent = origens[op];
  document.getElementById("op-destino-wrap").style.display =
    op === "pix" || op === "transferencia" ? "block" : "none";
}

async function executarOperacao() {
  const conta = document.getElementById("op-conta").value.trim();
  const destino = document.getElementById("op-destino").value.trim();
  const valor = parseFloat(document.getElementById("op-valor").value);

  if (!conta) return showAlerta("alerta-op", "Informe a conta.", "erro");
  if (!valor || valor <= 0) return showAlerta("alerta-op", "Informe um valor positivo.", "erro");
  if ((opAtual === "pix" || opAtual === "transferencia") && !destino) {
    return showAlerta("alerta-op", "Informe a conta de destino.", "erro");
  }

  try {
    let data;

    if (sessao.offline) {
      data = _demoOperacao(opAtual, conta, destino, valor);
    } else {
      const endpoints = {
        deposito: { url: "/transacoes/deposito", body: { numero: conta, valor } },
        saque: { url: "/transacoes/saque", body: { numero: conta, valor } },
        pix: { url: "/transacoes/pix", body: { origem: conta, destino, valor } },
        transferencia: { url: "/transacoes/transferencia", body: { origem: conta, destino, valor } },
      };
      const ep = endpoints[opAtual];
      data = await apiFetch(ep.url, {
        method: "POST",
        body: JSON.stringify(ep.body),
      });
    }

    showAlerta("alerta-op", data.mensagem, data.sucesso ? "sucesso" : "erro");
    if (data.sucesso) {
      document.getElementById("op-valor").value = "";
      carregarDashboard();
    }
  } catch (e) {
    showAlerta("alerta-op", "Erro ao comunicar com a API.", "erro");
  }
}

// Demo offline: replica lógica dos controllers
function _demoOperacao(op, conta, destino, valor) {
  const agora = new Date().toLocaleString("pt-BR");

  if (!demo.contas[conta]) return { sucesso: false, mensagem: "Conta não encontrada." };

  if (op === "deposito") {
    demo.contas[conta].saldo += valor;
    demo.transacoes[conta].unshift({ tipo: "Depósito", valor, data: agora });
    return { sucesso: true, mensagem: `Depósito realizado. Novo saldo: ${fmt(demo.contas[conta].saldo)}` };
  }

  if (op === "saque") {
    if (valor > demo.contas[conta].saldo)
      return { sucesso: false, mensagem: "Saldo insuficiente." };
    demo.contas[conta].saldo -= valor;
    demo.transacoes[conta].unshift({ tipo: "Saque", valor: -valor, data: agora });
    return { sucesso: true, mensagem: `Saque realizado. Novo saldo: ${fmt(demo.contas[conta].saldo)}` };
  }

  if (op === "pix" || op === "transferencia") {
    if (!demo.contas[destino]) return { sucesso: false, mensagem: "Conta destino não encontrada." };
    if (valor > demo.contas[conta].saldo) return { sucesso: false, mensagem: "Saldo insuficiente." };
    demo.contas[conta].saldo -= valor;
    demo.contas[destino].saldo += valor;
    const tipo = op === "pix" ? "PIX" : "Transferência";
    demo.transacoes[conta].unshift({ tipo: `${tipo} enviado → #${destino}`, valor: -valor, data: agora });
    demo.transacoes[destino].unshift({ tipo: `${tipo} recebido ← #${conta}`, valor, data: agora });
    return { sucesso: true, mensagem: `${tipo} realizado. Saldo restante: ${fmt(demo.contas[conta].saldo)}` };
  }

  return { sucesso: false, mensagem: "Operação desconhecida." };
}

// ─────────────────────────────────────────────────────────────────────────────
// EXTRATO
// ─────────────────────────────────────────────────────────────────────────────
async function verExtrato() {
  const numero = document.getElementById("ext-num").value.trim();
  if (!numero) return showAlerta("alerta-ext", "Informe o número da conta.", "erro");

  try {
    let transacoes = [];
    let tituloExtra = "";

    if (sessao.offline) {
      if (!demo.contas[numero]) {
        return showAlerta("alerta-ext", "Conta não encontrada.", "erro");
      }
      transacoes = demo.transacoes[numero] || [];
      tituloExtra = `Conta #${numero} — ${demo.contas[numero].titular}`;
    } else {
      const data = await apiFetch(`/transacoes/extrato/${numero}`);
      if (!data.sucesso) return showAlerta("alerta-ext", data.mensagem, "erro");
      transacoes = data.transacoes || [];
      tituloExtra = `Extrato — conta #${numero}`;
    }

    ocultarAlerta("alerta-ext");
    document.getElementById("painel-extrato").style.display = "block";
    document.getElementById("ext-titulo").textContent = tituloExtra;

    const lista = document.getElementById("lista-extrato");

    if (!transacoes.length) {
      lista.innerHTML = '<div class="tx-vazio">Nenhuma transação encontrada.</div>';
      return;
    }

    lista.innerHTML = transacoes
      .map((t) => {
        // Normaliza: pode vir como objeto { tipo, valor, data } ou string
        let tipo = "", valor = null, data = "";
        if (typeof t === "object") {
          tipo = t.tipo || t.descricao || JSON.stringify(t);
          valor = t.valor != null ? parseFloat(t.valor) : null;
          data = t.data || t.data_hora || "";
        } else {
          tipo = String(t);
        }

        const positivo = valor === null ? true : valor >= 0;
        const valStr =
          valor !== null
            ? `<span class="${positivo ? "tx-val-entrada" : "tx-val-saida"}">${positivo ? "+" : ""}${fmt(valor)}</span>`
            : "";

        return `
          <div class="tx-item">
            <div>
              <div class="tx-tipo">${tipo}</div>
              ${data ? `<div class="tx-data">${data}</div>` : ""}
            </div>
            ${valStr}
          </div>
        `;
      })
      .join("");
  } catch (e) {
    showAlerta("alerta-ext", "Erro ao carregar extrato.", "erro");
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────────────────────────────────────
irTela("tela-login");