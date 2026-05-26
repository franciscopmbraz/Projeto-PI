//frontend/login.js
let formLogin = document.querySelector('#formLogin');

if (formLogin) {
    let botaoSignUp = document.querySelector('.btn-signup');
    
    if (botaoSignUp) {
        botaoSignUp.addEventListener('click', function(evento) {
            evento.preventDefault(); 
            window.location.href = 'signup.html';
        });
    }

    formLogin.addEventListener('submit', async function(evento) {
        evento.preventDefault(); 

        let numeroAluno = document.querySelector('#numero_aluno').value;
        let senhaAluno = document.querySelector('#senha').value;
        
        try {
            let resposta = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    numero_aluno: numeroAluno,
                    senha: senhaAluno
                })
            });

            let dados = await resposta.json();

            if (resposta.ok) {
                localStorage.setItem('aluno_logado', numeroAluno);
                localStorage.setItem('ano_letivo', dados.ano_letivo);
                localStorage.setItem('voto_turma', dados.voto_turma);
                localStorage.setItem('voto_delegado', dados.voto_delegado);
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