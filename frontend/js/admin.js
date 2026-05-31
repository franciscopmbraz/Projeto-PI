let turmasCache = [];
let utilizadoresCache = {};

function main() {
    const alunoId = localStorage.getItem('aluno_id');
    const isAdmin = localStorage.getItem('is_admin') === 'true';
    if (!alunoId || !isAdmin) {
        window.location.href = 'landing.html';
        return;
    }
    carregarTurmas();
    carregarVotacoes();
}

async function carregarTurmas() {
    const res = await fetch(`${API_BASE_URL}/api/turmas`);
    const data = await res.json();
    turmasCache = data.turmas;
    const select = document.getElementById('del-turma');
    select.innerHTML = '<option value="">-- selecione --</option>';
    for (let t of turmasCache) {
        select.innerHTML += `<option value="${t.id}">${t.nome}</option>`;
    }
}

async function carregarUtilizadoresDaTurma(turmaId) {
    if (!turmaId) {
        document.getElementById('del-candidatos').innerHTML = '<p class="text-muted small">Selecione uma turma primeiro.</p>';
        return;
    }
    if (utilizadoresCache[turmaId]) {
        renderUtilizadores(utilizadoresCache[turmaId]);
        return;
    }
    try {
        const res = await fetch(`${API_BASE_URL}/api/utilizadores/turma/${turmaId}`);
        const data = await res.json();
        utilizadoresCache[turmaId] = data.utilizadores;
        renderUtilizadores(data.utilizadores);
    } catch(e) {
        console.error(e);
    }
}

function renderUtilizadores(utilizadores) {
    const container = document.getElementById('del-candidatos');
    container.innerHTML = '';
    if (!utilizadores || utilizadores.length === 0) {
        container.innerHTML = '<p class="text-muted small">Sem utilizadores nesta turma.</p>';
        return;
    }
    for (let u of utilizadores) {
        const div = document.createElement('div');
        div.className = 'candidato-entry border rounded p-2 mb-2';
        div.dataset.utilizadorId = u.id;
        div.innerHTML = `
            <div class="form-check mb-1">
                <input class="form-check-input candidato-check" type="checkbox" value="${u.id}" id="cand-${u.id}">
                <label class="form-check-label" for="cand-${u.id}">
                    <strong>${u.nome}</strong> <span class="text-muted">#${u.numero}</span>
                </label>
            </div>
            <div class="desc-field" style="display:none">
                <input type="text" class="form-control form-control-sm candidato-desc" placeholder="Descrição do candidato (opcional)">
            </div>
        `;
        div.querySelector('.candidato-check').addEventListener('change', function() {
            div.querySelector('.desc-field').style.display = this.checked ? 'block' : 'none';
        });
        container.appendChild(div);
    }
}

function addCandidatoLista() {
    const container = document.getElementById('lista-candidatos');
    const div = document.createElement('div');
    div.className = 'd-flex gap-2 mb-2 candidato-lista-row';
    div.innerHTML = `
        <input type="text" class="form-control form-control-sm" placeholder="Nome da lista" required>
        <input type="text" class="form-control form-control-sm" placeholder="Descrição (opcional)">
        <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.parentElement.remove()">
            <i class="bi bi-x"></i>
        </button>
    `;
    container.appendChild(div);
}

async function carregarVotacoes() {
    const [resDel, resLista] = await Promise.all([
        fetch(`${API_BASE_URL}/api/votacoes/delegado`),
        fetch(`${API_BASE_URL}/api/votacoes/lista`)
    ]);
    const dataDel = await resDel.json();
    const dataLista = await resLista.json();

    const containerDel = document.getElementById('lista-delegado');
    const containerLista = document.getElementById('lista-lista');
    containerDel.innerHTML = '';
    containerLista.innerHTML = '';

    for (let v of dataDel.votacoes) containerDel.appendChild(criarCardVotacao(v, 'delegado'));
    for (let v of dataLista.votacoes) containerLista.appendChild(criarCardVotacao(v, 'lista'));
}

function criarCardVotacao(v, tipo) {
    const div = document.createElement('div');
    div.className = 'votacao-item d-flex align-items-center justify-content-between';
    const encerrada = !v.end_date || new Date(v.end_date) <= new Date();
    const turmaLabel = tipo === 'delegado' && v.turma_id
        ? ` | ${turmasCache.find(t => t.id === v.turma_id)?.nome || 'Turma ' + v.turma_id}`
        : '';
    div.innerHTML = `
        <div>
            <div class="fw-500">${v.titulo || 'Sem título'}</div>
            <small class="text-muted">
                ${v.end_date ? (encerrada ? 'Encerrada a: ' : 'Termina a: ') + new Date(v.end_date).toLocaleString() : 'Sem data de fim'}
                ${turmaLabel}
            </small>
        </div>
        <button class="btn btn-sm btn-outline-danger" onclick="eliminarVotacao(${v.id}, '${tipo}')">
            <i class="bi bi-trash"></i>
        </button>
    `;
    return div;
}

async function eliminarVotacao(id, tipo) {
    if (!confirm('Tens a certeza? Todos os votos serão apagados.')) return;
    const alunoId = localStorage.getItem('aluno_id');
    const res = await fetch(`${API_BASE_URL}/api/votacoes/${tipo}/${id}?utilizador_id=${alunoId}`, {
        method: 'DELETE'
    });
    const data = await res.json();
    if (res.ok) carregarVotacoes();
    else alert('Erro: ' + data.detail);
}

function abrirModalDelegado() {
    document.getElementById('del-titulo').value = '';
    document.getElementById('del-turma').value = '';
    document.getElementById('del-start').value = '';
    document.getElementById('del-end').value = '';
    document.getElementById('del-candidatos').innerHTML = '<p class="text-muted small">Selecione uma turma primeiro.</p>';
    new bootstrap.Modal(document.getElementById('modalDelegado')).show();
}

function abrirModalLista() {
    document.getElementById('lista-titulo').value = '';
    document.getElementById('lista-start').value = '';
    document.getElementById('lista-end').value = '';
    document.getElementById('lista-candidatos').innerHTML = '';
    addCandidatoLista();
    new bootstrap.Modal(document.getElementById('modalLista')).show();
}

async function criarDelegado() {
    const titulo = document.getElementById('del-titulo').value.trim();
    const turma_id = parseInt(document.getElementById('del-turma').value);
    const start_date = document.getElementById('del-start').value || null;
    const end_date = document.getElementById('del-end').value || null;

    if (!titulo) { alert('Insere um título.'); return; }
    if (!turma_id) { alert('Seleciona uma turma.'); return; }

    const res = await fetch(`${API_BASE_URL}/api/votacoes/delegado`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ titulo, turma_id, start_date, end_date })
    });
    if (!res.ok) { const d = await res.json(); alert('Erro: ' + d.detail); return; }
    const votacaoData = await res.json();
    const votacaoId = votacaoData.votacao_id;

    const checks = document.querySelectorAll('.candidato-check:checked');
    for (let check of checks) {
        const utilizadorId = parseInt(check.value);
        const desc = check.closest('.candidato-entry').querySelector('.candidato-desc').value.trim();
        await fetch(`${API_BASE_URL}/api/candidatos/delegado`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ utilizador_id: utilizadorId, votacao_id: votacaoId, descricao: desc || null })
        });
    }

    bootstrap.Modal.getInstance(document.getElementById('modalDelegado')).hide();
    carregarVotacoes();
}

async function criarLista() {
    const titulo = document.getElementById('lista-titulo').value.trim();
    const start_date = document.getElementById('lista-start').value || null;
    const end_date = document.getElementById('lista-end').value || null;

    if (!titulo) { alert('Insere um título.'); return; }

    const rows = document.querySelectorAll('.candidato-lista-row');
    const candidatos = [];
    for (let row of rows) {
        const inputs = row.querySelectorAll('input');
        const nome = inputs[0].value.trim();
        const desc = inputs[1].value.trim();
        if (nome) candidatos.push({ titulo: nome, descricao: desc || null });
    }
    if (candidatos.length === 0) { alert('Adiciona pelo menos um candidato.'); return; }

    const res = await fetch(`${API_BASE_URL}/api/votacoes/lista`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ titulo, start_date, end_date })
    });
    if (!res.ok) { const d = await res.json(); alert('Erro: ' + d.detail); return; }
    const votacaoData = await res.json();
    const votacaoId = votacaoData.votacao_id; 

    for (let c of candidatos) {
        await fetch(`${API_BASE_URL}/api/candidatos/lista`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ titulo: c.titulo, descricao: c.descricao, votacao_id: votacaoId })
        });
    }

    bootstrap.Modal.getInstance(document.getElementById('modalLista')).hide();
    carregarVotacoes();
}

main();