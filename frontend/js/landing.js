function main() {
    if (!localStorage.getItem('aluno_id')) {
        window.location.href = 'login.html';
    } else {
    load_votacoes();
    }
}

async function load_votacoes() {
    let votacoes_ativas = []
    let votacoes_completas = []
    try {
        const response_votdel = await fetch(`${API_BASE_URL}/api/votacoes/delegado`);
        const data_votdel = await response_votdel.json();
        if (!data_votdel || data_votdel.status !== "SUCCESS") {
            
            console.error("Erro ao carregar eleições:", data_votdel && data_votdel.message ? data_votdel.message : data_votdel);
            return;
        } else {
            for (let votacao of data_votdel.votacoes) {
                if (votacao.end_date && new Date(votacao.end_date) > new Date()) {
                    
                    votacoes_ativas.push({...votacao, tipo: 'delegado'});
                } else {                    
                    votacoes_completas.push({...votacao, tipo: 'delegado'});
                }
            }
        }

        const response_votlista = await fetch(`${API_BASE_URL}/api/votacoes/lista`);
        const data_votlista = await response_votlista.json();

        if (!data_votlista || data_votlista.status !== "SUCCESS") {
            console.error("Erro ao carregar eleições:", data_votlista && data_votlista.message ? data_votlista.message : data_votlista);
            return;
        } else {
            for (let votacao of data_votlista.votacoes) {
                console.log("Processando votação:", votacao);
                if (votacao.end_date && new Date(votacao.end_date) > new Date()) {
                    votacoes_ativas.push({...votacao, tipo: 'lista'});
                } else {
                    votacoes_completas.push({...votacao, tipo: 'lista'});
                }
            }
        }

        render_votacoes(votacoes_ativas, votacoes_completas);


    } catch (error) {
        console.error("Erro ao carregar eleições:", error);
        alert(error);
    }
}

function render_votacoes(votacoes_ativas, votacoes_completas) {
    let containerAtivas = document.querySelector('.votacoes_ativas');
    let containerCompletas = document.querySelector('.votacoes_completas');

    for (let votacao of votacoes_ativas) {
        let div = document.createElement('div');
        div.classList.add('votacao-item');
        div.innerHTML = `
            <h3>${votacao.titulo}</h3>
            <p>Termina a: ${new Date(votacao.end_date).toLocaleString()}</p>
            <button class="btn-eleicao" onclick="window.location.href='votacao.html?tipo=${votacao.tipo}&id=${votacao.id}'">Votar</button>
        `;
        containerAtivas.appendChild(div);
    }

    for (let votacao of votacoes_completas) {
        let div = document.createElement('div');
        div.classList.add('votacao-item');
        div.innerHTML = `
            <h3>${votacao.titulo}</h3>
            <p>Termina a: ${new Date(votacao.end_date).toLocaleString()}</p>
            <button class="btn-eleicao" onclick="window.location.href='votacao.html?tipo=${votacao.tipo}&id=${votacao.id}'">Ver Resultados</button>
        `;
        containerCompletas.appendChild(div);
    }
}

main();