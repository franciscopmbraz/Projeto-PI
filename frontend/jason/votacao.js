// frontend/votacao.js
let formVotacao = document.querySelector('#form-votacao-pagina');

if (formVotacao) {
    let alunoLogado = localStorage.getItem('aluno_logado');
    if (!alunoLogado) window.location.href = 'login.html';

    let params = new URLSearchParams(window.location.search);
    let tipoEleicao = params.get('tipo'); 

    let tituloPagina = document.querySelector('#titulo-eleicao');
    let listaOpcoes = document.querySelector('#lista-opcoes');

    async function carregarOpcoes() {
        try {
            let resposta = await fetch(`${API_BASE_URL}/api/candidatos/${alunoLogado}`);
            let dados = await resposta.json();

            if (tipoEleicao === 'lista') {
                tituloPagina.textContent = "Eleição: Associação de Estudantes";
                dados.listas.forEach(lista => {
                    listaOpcoes.innerHTML += `
                        <label style="display: block; margin: 15px 0; font-size: 18px; cursor: pointer;">
                            <input type="radio" name="candidato" value="${lista.id}" required style="transform: scale(1.3); margin-right: 10px;">
                            <b>${lista.nome}</b>
                        </label>
                    `;
                });
            } else if (tipoEleicao === 'delegado') {
                tituloPagina.textContent = `Eleição: Delegado (Turma ${dados.turma})`;
                if (dados.delegados.length === 0) {
                    listaOpcoes.innerHTML = "<p>Sem candidatos registados nesta turma.</p>";
                } else {
                    dados.delegados.forEach(del => {
                        listaOpcoes.innerHTML += `
                            <label style="display: block; margin: 15px 0; font-size: 18px; cursor: pointer;">
                                <input type="radio" name="candidato" value="${del.id}" required style="transform: scale(1.3); margin-right: 10px;">
                                <b>${del.nome}</b>
                            </label>
                        `;
                    });
                }
            }
        } catch (e) { console.error(e); }
    }
    carregarOpcoes();

    formVotacao.addEventListener('submit', async function(evento) {
        evento.preventDefault();
        let escolhido = document.querySelector('input[name="candidato"]:checked').value;
        let urlEndpoint = (tipoEleicao === 'lista') ? "/api/votar/lista" : "/api/votar/delegado";

        try {
            let resposta = await fetch(`${API_BASE_URL}${urlEndpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ numero_aluno: alunoLogado, escolha: escolhido })
            });
            let dados = await resposta.json();
            if (resposta.ok) {
                alert("✅ " + dados.mensagem);
                window.location.href = 'landing.html'; 
            } else {
                alert("Erro: " + dados.detail);
            }
        } catch (e) { alert("Erro ao enviar o voto."); }
    });
}