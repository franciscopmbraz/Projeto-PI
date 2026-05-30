async function main() {
    const alunoId = localStorage.getItem('aluno_id');
    if (!alunoId) { window.location.href = 'login.html'; return; }

    const params = new URLSearchParams(window.location.search);
    const tipo = params.get('tipo');
    const votacaoId = params.get('id');

    
    if (!votacaoId) {
        alert('ID da votação não foi fornecido. Volte para a página de eleições e tente novamente.');
        window.location.href = 'landing.html';
        return;
    }

    const motivo = await carregarVotacao(tipo, votacaoId, alunoId);
    if (motivo) {
        mostrarResultados(tipo, votacaoId, motivo);
    }
}

async function carregarVotacao(tipo, votacaoId, alunoId) {
    try {
        const urlVotacao = tipo === 'lista'
            ? `${API_BASE_URL}/api/votacoes/lista`
            : `${API_BASE_URL}/api/votacoes/delegado`;

        const res = await fetch(urlVotacao);
        const data = await res.json();
        const votacao = data.votacoes.find(v => v.id == votacaoId);

        if (!votacao) { alert("Votação não encontrada."); return false; }

        const encerrada = !votacao.end_date || new Date(votacao.end_date) <= new Date();

        document.getElementById('titulo-eleicao').textContent = votacao.titulo;
        document.getElementById('tipo-badge').textContent = tipo === 'lista' ? 'Lista' : 'Delegado';
        if (tipo === 'delegado') document.getElementById('tipo-badge').classList.add('delegado');
        document.getElementById('end-date').textContent = votacao.end_date
            ? 'Termina a: ' + new Date(votacao.end_date).toLocaleString()
            : 'Sem data de fim';

        if (encerrada) return 'encerrada';

        try {
            const urlVerificar = tipo === 'lista'
                ? `${API_BASE_URL}/api/votos/lista/verificar?utilizador_id=${alunoId}&votacao_id=${votacaoId}`
                : `${API_BASE_URL}/api/votos/delegado/verificar?utilizador_id=${alunoId}&votacao_id=${votacaoId}`;

            const resVerificar = await fetch(urlVerificar);
            const verificar = await resVerificar.json();

            if (verificar.ja_votou) return 'ja-votou';
            if (verificar.turma_errada) return 'turma-errada';
        } catch(e) { console.error(e); }

        const urlCandidatos = tipo === 'lista'
            ? `${API_BASE_URL}/api/candidatos/lista/${votacaoId}`
            : `${API_BASE_URL}/api/candidatos/delegado/${votacaoId}`;

        const resCand = await fetch(urlCandidatos);
        const dataCand = await resCand.json();
        const candidatos = dataCand.candidatos;

        document.getElementById('num-candidatos').textContent = `${candidatos.length} candidatos`;

        const lista = document.getElementById('lista-opcoes');
        lista.innerHTML = '';
        candidatos.forEach(c => {
            const nome = tipo === 'lista' ? c.titulo : c.nome;
            const div = document.createElement('div');
            div.className = 'candidato-card';
            div.dataset.id = c.id;
            div.innerHTML = `
                <div class="candidato-top">
                    <div class="candidato-nome">${nome}</div>
                </div>
                <div class="candidato-desc">${c.descricao || ''}</div>
            `;
            div.addEventListener('click', () => {
                document.querySelectorAll('.candidato-card').forEach(c => c.classList.remove('selected'));
                div.classList.add('selected');
                document.getElementById('btn-votar').disabled = false;
            });
            lista.appendChild(div);
        });

        const oldBtn = document.getElementById('btn-votar');
        const newBtn = oldBtn.cloneNode(true);
        oldBtn.parentNode.replaceChild(newBtn, oldBtn);

        const voteErrorShouldShowResults = (response, payload) => {
            if (!payload) return false;
            const detail = payload.detail;
            if (typeof detail === 'string') {
                return detail.includes('Já votaste') || detail.includes('Não podes votar');
            }
            return false;
        };

        newBtn.addEventListener('click', async () => {
            const selected = document.querySelector('.candidato-card.selected');
            if (!selected) { alert('Por favor selecione um candidato.'); return; }

            newBtn.disabled = true;
            newBtn.textContent = 'A enviar voto...';

            const endpoint = tipo === 'lista' ? '/api/votos/lista' : '/api/votos/delegado';
            try {
                const r = await fetch(`${API_BASE_URL}${endpoint}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        utilizador_id: parseInt(alunoId),
                        votacao_id: parseInt(votacaoId),
                        escolha: parseInt(selected.dataset.id)
                    })
                });
                const d = await r.json();
                if (r.ok) {
                    alert('Voto registado com sucesso!');
                    mostrarResultados(tipo, votacaoId, 'ja-votou');
                } else if (voteErrorShouldShowResults(r, d)) {
                    alert('Já votaste ou não podes votar nesta votação. A mostrar resultados.');
                    mostrarResultados(tipo, votacaoId, 'ja-votou');
                } else {
                    alert('Erro: ' + (typeof d.detail === 'string' ? d.detail : JSON.stringify(d.detail)));
                    newBtn.disabled = false;
                    newBtn.textContent = 'Confirmar voto';
                }
            } catch (e) {
                console.error(e);
                alert('Erro ao enviar voto: ' + e.message);
                newBtn.disabled = false;
                newBtn.textContent = 'Confirmar voto';
            }
        });

        return false;
    } catch (e) {
        console.error(e);
        return false;
    }
}


async function mostrarResultados(tipo, votacaoId, motivo = null) {
    document.getElementById('view-votacao').style.display = 'none';
    document.getElementById('view-resultados').style.display = 'block';


    const banner = document.getElementById('motivo-banner');
    if (motivo) {
        const mensagens = {
            'ja-votou':     { texto: '✓ Já votaste nesta votação.',                          classe: 'ja-votou' },
            'turma-errada': { texto: '⚠ Não podes votar nesta votação (turma diferente).',   classe: 'turma-errada' },
            'encerrada':    { texto: '⏱ Esta votação já terminou.',                          classe: 'encerrada' },
        };
        const m = mensagens[motivo];
        if (m) {
            banner.textContent = m.texto;
            banner.className = 'motivo-banner ' + m.classe;
            banner.style.display = 'flex';
        }
    } else {
        banner.style.display = 'none';
    }

    try {
        const res = await fetch(`${API_BASE_URL}/api/resultados/${tipo}?votacao_id=${votacaoId}`);
        const data = await res.json();
        const resultados = data.resultados;

        const votacaoRes = await fetch(`${API_BASE_URL}/api/votacoes/${tipo}`);
        const votacaoData = await votacaoRes.json();
        const votacao = votacaoData.votacoes.find(v => v.id == votacaoId);

        document.getElementById('titulo-resultados').textContent = votacao?.titulo || '';
        document.getElementById('tipo-badge-res').textContent = tipo === 'lista' ? 'Lista' : 'Delegado';
        if (tipo === 'delegado') document.getElementById('tipo-badge-res').classList.add('delegado');

        const total = resultados.reduce((s, r) => s + r.votos, 0);
        document.getElementById('total-votos').textContent = `${total} votos totais`;

        const maxVotos = Math.max(...resultados.map(r => r.votos));
        const lista = document.getElementById('lista-resultados');
        lista.innerHTML = '';

        resultados.sort((a, b) => b.votos - a.votos).forEach(r => {
            const nome = tipo === 'lista' ? r.titulo : r.nome;
            const initials = nome.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
            const isWinner = r.votos === maxVotos && maxVotos > 0;
            const pct = total > 0 ? Math.round((r.votos / total) * 100) : 0;
            const div = document.createElement('div');
            div.className = 'candidato-card' + (isWinner ? ' winner' : '');
            div.innerHTML = `
                <div class="candidato-top">
                    <div class="avatar ${isWinner ? 'winner' : ''}">${initials}</div>
                    <div class="candidato-nome">${nome}</div>
                    ${isWinner ? '<span class="winner-badge">Vencedor</span>' : ''}
                </div>
                <div class="votos-row">
                    <div class="votos-bar-bg"><div class="votos-bar ${isWinner ? 'winner' : ''}" style="width:${pct}%"></div></div>
                    <span class="votos-count">${r.votos} votos</span>
                </div>
            `;
            lista.appendChild(div);
        });
    } catch (e) {
        console.error(e);
    }
}

main();