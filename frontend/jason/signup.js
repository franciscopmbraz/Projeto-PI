// frontend/signup.js
let formSignup = document.querySelector('#formsignup');

if (formSignup) {
    formSignup.addEventListener('submit', async function(evento) {
        evento.preventDefault(); 

        let numeroAluno = document.querySelector('#numero_aluno').value;
        let anoLetivo = document.querySelector('#ano').value;
        let senhaAluno = document.querySelector('#senha').value;

        if (numeroAluno.length < 3) {
            alert("O Número de Aluno tem de ter pelo menos 3 caracteres.");
            return; 
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
            let resposta = await fetch(`${API_BASE_URL}/auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    numero_aluno: numeroAluno,
                    ano_letivo: anoLetivo,
                    senha: senhaAluno
                })
            });

            let dados = await resposta.json();

            if (resposta.ok) {
                alert("Aluno registado com sucesso! Agora podes fazer login.");
                window.location.href = 'login.html'; 
            } else {
                alert("Erro: " + dados.detail);
            }
        } catch (erro) {
            console.error("Erro na API:", erro);
            alert("Erro ao conectar à Base de Dados");
        }
    });
}