//frontend/login.js
function main() {
    initLogin();
}

function initLogin() {
    console.log("Inicializando login.js");
    let formLogin = document.querySelector('#formLogin');

    if (formLogin) {
        formLogin.addEventListener('submit', async function(evento) {
            evento.preventDefault(); 
            console.log("Formulário de login submetido");
            let numeroAluno = document.querySelector('#aluno').value;
            let senhaAluno = document.querySelector('#senha').value;
            
            try {
                let resposta = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        numero: numeroAluno,
                        senha: senhaAluno
                    })
                });

                let dados = await resposta.json();

                if (resposta.ok) {
                    localStorage.setItem('aluno_id', dados.id);
                    if (dados.nome) localStorage.setItem('aluno_nome', dados.nome);
                    if (dados.numero) localStorage.setItem('aluno_numero', dados.numero);
                    if (dados.turma_id) localStorage.setItem('aluno_turma', dados.turma_id);

                    window.location.href = 'landing.html';
                } else {
                    alert("Erro: " + dados.detail);
                }
            } catch (erro) {
                console.error("Erro na API:", erro);
                alert("Erro ao conectar à Base de Dados.");
            }
        });
    }

}


main();