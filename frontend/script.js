
const API_BASE_URL = "http://localhost:8000";



let formSignup = document.querySelector('#formsignup');

// Só corre este código se estivermos na página signup.html
if (formSignup) {
    formSignup.addEventListener('submit', async function(evento) {
        evento.preventDefault(); // Impede a página de recarregar quando clicas no botão

        let numeroAluno = document.querySelector('#numero_aluno').value;
        let anoLetivo = document.querySelector('#ano').value;
        let senhaAluno = document.querySelector('#senha').value;

        try {
            // Envia os dados para a tua API (FastAPI) no Docker
            let resposta = await fetch('http://localhost:8000/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    numero_aluno: numeroAluno,
                    ano_letivo: anoLetivo,
                    senha: senhaAluno
                })
            });

            let dados = await resposta.json();

            // Verifica a resposta da API
            if (resposta.ok) {
                alert("🎉 " + dados.mensagem); // Mensagem de sucesso!
                window.location.href = 'login.html'; // Manda o aluno para o Login
            } else {
                // Se der erro mostra o alerta
                alert("Erro: " + dados.detail);
            }

        } catch (erro) {
            console.error("Erro na API:", erro);
            alert("Erro ao conectar à Base de Dados. Verifica se o Docker está a rodar.");
        }
    });
}







let botaoLogin = document.querySelector('.btn-login');
botaoLogin.addEventListener('click', function() {
        window.location.href = 'landing.html';
    });