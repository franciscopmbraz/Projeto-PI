
async function initNavbar() {
    const currentPage = window.location.pathname.split('/').pop() || 'landing.html';
    const isAuthPage = currentPage === 'login.html' || currentPage === 'signup.html';

    if (isAuthPage) return;
    let alunoNome = localStorage.getItem('aluno_nome') || localStorage.getItem('nome');
    let alunoNumero = localStorage.getItem('aluno_numero') || localStorage.getItem('aluno_id');
    let alunoTurma = localStorage.getItem('aluno_turma') || localStorage.getItem('turma') || localStorage.getItem('turma_id');

    if (!alunoNome && alunoNumero) {
        alunoNome = 'Aluno ' + alunoNumero;
    }

    const navbarHTML = `
        <nav class="navbar navbar-expand-lg navbar-light bg-light border-bottom sticky-top">
            <div class="container-fluid">
                <a class="navbar-brand fw-bold" href="landing.html">
                    <strong>VotosEscola</strong>
                </a>
                <div class="ms-auto d-flex align-items-center">
                    <div id="navbar-right-placeholder"></div>
                </div>
            </div>
        </nav>
    `;

    const navElement = document.createElement('div');
    navElement.innerHTML = navbarHTML;
    document.body.insertBefore(navElement.firstElementChild, document.body.firstChild);

  
    if (!isAuthPage) {
        const placeholder = document.getElementById('navbar-right-placeholder');
        if (placeholder) {
            placeholder.innerHTML = `<div class="text-end"><div class="navbar-user-name">${alunoNome || 'Utilizador'}</div><small class="text-muted">#${alunoNumero || '-'} | ${alunoTurma || '-'}</small></div><button class="btn btn-sm btn-outline-danger ms-2" onclick="logout()">Sair</button>`;

            if (alunoTurma && /^[0-9]+$/.test(String(alunoTurma))) {
                try {
                    const resp = await fetch(`${API_BASE_URL}/api/turmas`);
                    const data = await resp.json();
                    if (data && data.status === 'SUCCESS' && Array.isArray(data.turmas)) {
                        const found = data.turmas.find(t => String(t.id) === String(alunoTurma));
                        if (found) {
                            alunoTurma = found.nome;
                            placeholder.innerHTML = `<div class="text-end"><div class="navbar-user-name">${alunoNome || 'Utilizador'}</div><small class="text-muted">#${alunoNumero || '-'} | ${alunoTurma}</small></div><button class="btn btn-sm btn-outline-danger ms-2" onclick="logout()">Sair</button>`;
                        }
                    }
                } catch (e) {
                    console.debug('Could not resolve turma name', e);
                }
            }
        }
    }
}

function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavbar);
} else {
    initNavbar();
}
