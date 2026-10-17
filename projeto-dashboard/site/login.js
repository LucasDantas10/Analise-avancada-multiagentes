"use strict";

const USUARIO_DEMO = "admin";
const SENHA_DEMO = "papelaria2026";
const CHAVE_SESSAO = "papelaria-demo-auth";

document.getElementById("formulario-login").addEventListener("submit", (evento) => {
  evento.preventDefault();
  const usuario = document.getElementById("usuario");
  const senha = document.getElementById("senha");
  const erro = document.getElementById("erro-login");
  const corresponde = usuario.value.trim() === USUARIO_DEMO && senha.value === SENHA_DEMO;

  if (!corresponde) {
    erro.hidden = false;
    senha.setAttribute("aria-invalid", "true");
    senha.focus();
    return;
  }

  try {
    sessionStorage.setItem(CHAVE_SESSAO, "ok");
    window.location.assign("vendas/");
  } catch (_erro) {
    erro.textContent = "Não foi possível iniciar a sessão neste navegador. Permita o armazenamento de sessão e tente novamente.";
    erro.hidden = false;
  }
});

for (const campo of ["usuario", "senha"]) {
  document.getElementById(campo).addEventListener("input", () => {
    document.getElementById("erro-login").hidden = true;
    document.getElementById("senha").removeAttribute("aria-invalid");
  });
}
