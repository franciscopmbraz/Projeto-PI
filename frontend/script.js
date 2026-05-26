
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
            alert("Erro ao conectar à Base de Dados");
        }
    });
}


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
        evento.preventDefault(); // Impede a página de recarregar

        let numeroAluno = document.querySelector('#numero_aluno').value;
        let senhaAluno = document.querySelector('#senha').value;
        
        try {
            // Envia os dados para a API
            let resposta = await fetch('http://localhost:8000/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    numero_aluno: numeroAluno,
                    senha: senhaAluno
                    // Removemos o ano_letivo daqui!
                })
            });

            let dados = await resposta.json();

            // Verifica se a password estava correta
            if (resposta.ok) {
                // Guardar na memória do navegador o número do aluno e os votos para usar na Landing
                localStorage.setItem('aluno_logado', numeroAluno);
                localStorage.setItem('ano_letivo', dados.ano_letivo);
                localStorage.setItem('voto_turma', dados.voto_turma);
                localStorage.setItem('voto_delegado', dados.voto_delegado);

                window.location.href = 'landing.html'; // Manda o aluno para o Landing
            } else {
                // Se der erro mostra o alerta
                alert("Erro: " + dados.detail);
            }

        } catch (erro) {
            console.error("Erro na API:", erro);
            alert("Erro ao conectar à Base de Dados.");
        }
    });
}

// ==========================================
// 3. LÓGICA DO PAINEL DE VOTAÇÃO (landing.html)
// ==========================================
let btnEleicaoLista = document.querySelector('.btn-azul');
let btnEleicaoDelegado = document.querySelector('.btn-castanho');

// Só corre isto se os botões da landing existirem na página atual
if (btnEleicaoLista && btnEleicaoDelegado) {
    let alunoLogado = localStorage.getItem('aluno_logado');
    if (!alunoLogado) {
        window.location.href = 'login.html';
    }

    // Verifica na BD se o aluno já votou, para desativar (bloquear) o botão
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

    // Em vez do aviso popup, enviamos o aluno para a nova página!
    // Adicionamos "?tipo=lista" no link para a página saber o que mostrar
    btnEleicaoLista.addEventListener('click', () => window.location.href = 'votacao.html?tipo=lista');
    btnEleicaoDelegado.addEventListener('click', () => window.location.href = 'votacao.html?tipo=delegado');
}



let formVotacao = document.querySelector('#form-votacao-pagina');

if (formVotacao) {
    let alunoLogado = localStorage.getItem('aluno_logado');
    if (!alunoLogado) window.location.href = 'login.html';

    // Vai ao Link do navegador ver qual foi o botão que o utilizador clicou na página anterior
    let params = new URLSearchParams(window.location.search);
    let tipoEleicao = params.get('tipo'); 

    let tituloPagina = document.querySelector('#titulo-eleicao');
    let listaOpcoes = document.querySelector('#lista-opcoes');

    // Carrega os dados da Base de Dados
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

    // Ação do Botão "Confirmar Voto"
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
                window.location.href = 'landing.html'; // Devolve o aluno à base trancando o botão!
            } else {
                alert("Erro: " + dados.detail);
            }
        } catch (e) { alert("Erro ao enviar o voto."); }
    });
}