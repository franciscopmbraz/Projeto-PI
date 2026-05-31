function initSignup() {
    let formSignup = document.querySelector('#formsignup');

    
    if (formSignup) {
        formSignup.addEventListener('submit', async function(evento) {
            evento.preventDefault(); 

            let numeroAluno = document.querySelector('#numero_aluno_input').value;
            let nomeAluno = document.querySelector('#nome_input').value;
            let turma = document.querySelector('#turma_select').value;
            let senhaAluno = document.querySelector('#senha_input').value;
            let confirmarSenha = document.querySelector('#confirmar_senha_input').value;


            if (numeroAluno.length < 3) {
                alert("O Número de Aluno tem de ter pelo menos 3 caracteres.");
                return; 
            }
            if (!nomeAluno || nomeAluno.trim().length < 1) {
                alert("Por favor, insira o seu nome completo.");
                return;
            }
            if (!turma) {
                alert("Por favor, selecione uma turma válida.");
                return;
            }
            if (senhaAluno.length < 4) {
                alert("A Palavra-passe tem de ter pelo menos 4 caracteres.");
                return;
            }
            if (senhaAluno !== confirmarSenha) {
                alert("As palavras-passe não coincidem.");
                return;
            }

            try {
                let resposta = await fetch(`${API_BASE_URL}/auth/signup`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        numero: numeroAluno,
                        nome: nomeAluno,
                        turma_id: Number(turma),
                        senha: senhaAluno
                    })
                });

                let dados = await resposta.json();

                if (resposta.ok) {
                    window.location.href = 'login.html'; 
                } else {
                    alert("Erro: " + dados.detail);
                }
            } catch (erro) {
                console.error("Erro na API:", erro);
                alert("Erro na API: " + erro.message);
            }
        });
    }
}

async function get_turmas() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/turmas`);
        const data = await response.json();
        console.log("Data recebida:", data);

        if (!data || data.status !== "SUCCESS") {
            console.error("Erro ao carregar turmas:", data && data.message ? data.message : data);
            return;
        }

        const turmaSelect = document.getElementById('turma_select');
        if (!turmaSelect) {
            console.error("Elemento #turma_select não encontrado no DOM");
            return;
        }

        turmaSelect.innerHTML = '<option value="">-- selecione --</option>';

        for (let turma of data.turmas) {
            const option = document.createElement('option');
            option.value = turma.id;
            option.textContent = turma.nome;
            turmaSelect.appendChild(option);
        }
    } catch (err) {
        console.error("Erro na API ao buscar turmas:", err);
    }
}

function main() {
    get_turmas();
    initSignup();
}

main();
