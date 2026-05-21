
const API_BASE_URL = "http://localhost:8000";



let formSignup = document.querySelector('#formsignup');

// Só corre este código se estivermos na página signup.html
if (formSignup) {
    formSignup.addEventListener('submit', async function(evento) {
        evento.preventDefault(); // Impede a página de recarregar quando clicas no botão

        let numeroAluno = document.querySelector('#numero_aluno').value;
        let anoLetivo = document.querySelector('#ano').value;
        let senhaAluno = document.querySelector('#senha').value;
        

        if (numeroAluno.length < 3) {
            alert("O Número de Aluno tem de ter pelo menos 3 caracteres.");
            return; // O 'return' cancela a operação e não deixa o código continuar!
        }
        
        if (anoLetivo.length < 1) {
            alert("O Ano Escolar não pode estar vazio.");
            return;
        }
        
        if (senhaAluno.length < 4) {
            alert("A Palavra-passe tem de ter pelo menos 4 caracteres.");
            return;
        }

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
                alert("Aluno registado com sucesso! Agora podes fazer login.");
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


let formLogin = document.querySelector('#formLogin');

// O redirecionamento solto só vai existir se o formLogin estiver no ecrã!
if (formLogin) {
    let botaoLogin = document.querySelector('.btn-login');
    botaoLogin.addEventListener('click', function(evento) {
        evento.preventDefault();
        window.location.href = 'landing.html';
    });
}