// frontend/landing.js
let btnEleicaoLista = document.querySelector('.btn-azul');
let btnEleicaoDelegado = document.querySelector('.btn-castanho');

if (btnEleicaoLista && btnEleicaoDelegado) {
    let alunoLogado = localStorage.getItem('aluno_logado');
    if (!alunoLogado) {
        window.location.href = 'login.html';
    }

    async function verificarBloqueios() {
        try {
            let resposta = await fetch(`${API_BASE_URL}/api/candidatos/${alunoLogado}`);
            let dados = await resposta.json();
            if (resposta.ok) {
                if (dados.ja_votou_lista) {
                    btnEleicaoLista.textContent = "Voto Submetido";
                    btnEleicaoLista.disabled = true;
                    btnEleicaoLista.style.backgroundColor = "#cccccc";
                }
                if (dados.ja_votou_delegado) {
                    btnEleicaoDelegado.textContent = "Voto Submetido";
                    btnEleicaoDelegado.disabled = true;
                    btnEleicaoDelegado.style.backgroundColor = "#cccccc";
                }
            }
        } catch (erro) { console.error(erro); }
    }
    verificarBloqueios();
    
    btnEleicaoLista.addEventListener('click', () => window.location.href = 'votacao.html?tipo=lista');
    btnEleicaoDelegado.addEventListener('click', () => window.location.href = 'votacao.html?tipo=delegado');
}