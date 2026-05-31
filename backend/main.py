from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func



from database import Base, SessionLocal, engine, get_db
from models import (
    UtilizadorDB,
    Votacao_listaDB,
    Votacao_delegadoDB,
    Voto_utilizador_delegadoDB,
    Candidato_delegado_utilizadorDB,
    Voto_utilizador_listaDB,
    Candidato_listaDB,
    TurmaDB,

)
from schemas import (
    LoginRequest,
    SignupRequest,
    VotoDelegadoRequest,
    VotoListaRequest,
    VotacaoDelegadoRequest,
    VotacaoListaRequest,
    CandidatoDelegadoRequest,
    CandidatoListaRequest,
    TurmaRequest,
)
from seed_db import seed_database

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="Sistema de Votação Eletrónica - API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AUTH
@app.post("/auth/signup")
def signup(signup_request: SignupRequest, db=Depends(get_db)):
    existing_student = db.query(UtilizadorDB).filter(UtilizadorDB.numero == signup_request.numero).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Student already exists")

    novo_utilizador = UtilizadorDB(
        numero=signup_request.numero,
        nome=signup_request.nome,
        turma_id=signup_request.turma_id,
        senha=pwd_context.hash(signup_request.senha),
    )
    try:
        db.add(novo_utilizador)
        db.commit()
        db.refresh(novo_utilizador)
        return {"message": "User registered successfully", "id": novo_utilizador.id}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Erro de concorrência detetado. Transação abortada. (ID: { novo_utilizador.id })",
        )


@app.post("/auth/login")
def login(login_request: LoginRequest, db=Depends( get_db)):
    utilizador = db.query(UtilizadorDB).filter(UtilizadorDB.numero == login_request.numero).first()
    if not utilizador or not pwd_context.verify(login_request.senha, utilizador.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    return {
        "status": "sucesso",
        "mensagem": "Autenticação efetuada com sucesso!",
        "id": utilizador.id,
        "numero": utilizador.numero,
        "nome": utilizador.nome,
        "turma_id": utilizador.turma_id,
        "is_admin": utilizador.is_admin,
    }

def require_admin(utilizador_id: int, db):
    user = db.query(UtilizadorDB).filter(UtilizadorDB.id == utilizador_id).first()
    if not user or not user.is_admin :
        raise HTTPException(status_code=403, detail="Acesso negado.")

# TURMAS

@app.post("/api/turmas")
def criar_turma(req: TurmaRequest, db=Depends(get_db)):
    turma_existente = db.query(TurmaDB).filter(TurmaDB.nome == req.nome).first()
    if turma_existente:
        raise HTTPException(status_code=400, detail="Já existe uma turma com este nome.")
    
    nova_turma = TurmaDB(nome=req.nome)
    
    db.add(nova_turma )
    db.commit()
    db.refresh(nova_turma )

    return {"status": "SUCCESS", "message": "Turma criada com sucesso", "turma_id": nova_turma.id }

@app.get("/api/turmas")
def listar_turmas(db=Depends(get_db)):
    turmas =  db.query(TurmaDB).all()
    return {"status": "SUCCESS", "turmas": [{"id": turma.id, "nome": turma.nome} for turma in turmas] }


@app.get("/api/utilizadores/turma/{turma_id}")
def listar_utilizadores_turma(turma_id: int, db=Depends(get_db)):
    utilizadores = db.query(UtilizadorDB).filter(UtilizadorDB.turma_id == turma_id).all()
    return {
        "status": "SUCCESS",
        "utilizadores": [{"id": u.id, "nome": u.nome, "numero": u.numero} for u in utilizadores]
    }
# VOTAÇÕES DELEGADO

@app.post("/api/votacoes/delegado")
def criar_votacao_delegado(req: VotacaoDelegadoRequest, db=Depends(get_db)) :
    novo_votacao_delegado = Votacao_delegadoDB(
        turma_id=req.turma_id,
        titulo=req.titulo,
        start_date=req.start_date,
        end_date=req.end_date,
    )

    db.add(novo_votacao_delegado)
    db.commit()
    db.refresh(novo_votacao_delegado)

    return {"status": "SUCCESS", "message":  "Votação de delegado registered", "votacao_id": novo_votacao_delegado.id}

@app.get("/api/votacoes/delegado")
def listar_votacoes_delegado(db=Depends(get_db)):
    votacoes = db.query(Votacao_delegadoDB).all()
    return {
        "status": "SUCCESS",
        "votacoes": [
            {
                "id": v.id,
                "titulo": v.titulo,
                "turma_id": v.turma_id,
                "start_date": v.start_date,
                "end_date": v.end_date,
            }
            for v in votacoes
        ],
    }

@app.delete("/api/votacoes/delegado/{votacao_id}")
def deletar_votacao_delegado(votacao_id: int, utilizador_id: int, db=Depends(get_db)):
    require_admin(utilizador_id, db)
    votacao = db.query(Votacao_delegadoDB).filter(Votacao_delegadoDB.id == votacao_id).first()
    if not votacao:
        raise HTTPException(status_code=404, detail="Votação não encontrada.")
    db.query(Voto_utilizador_delegadoDB).filter(Voto_utilizador_delegadoDB.votacao_delegado_id == votacao_id).delete()
    db.query(Candidato_delegado_utilizadorDB).filter(Candidato_delegado_utilizadorDB.votacao_delegado_id  == votacao_id).delete()
    db.delete(votacao)
    db.commit()
    return {"status": "SUCCESS", "message": "Votação eliminada." }

@app.post("/api/candidatos/delegado")
def registrar_candidato_delegado(req: CandidatoDelegadoRequest, db=Depends(get_db)):
    utilizador = db.query(UtilizadorDB).filter(UtilizadorDB.id == req.utilizador_id).first()
    if not utilizador:
        raise HTTPException(status_code=404, detail="utilizador não encontrado.")
    
    votacao = db.query(Votacao_delegadoDB).filter(Votacao_delegadoDB.id == req.votacao_id).first()
    if not votacao:
        raise HTTPException(status_code=404, detail="votacao não encontrado.")
    
    if utilizador.turma != votacao.turma:
        raise HTTPException(status_code=400, detail="Não podes enlistar como candidato nesta votação.")

    candidato_existente = db.query(Candidato_delegado_utilizadorDB).filter(
        Candidato_delegado_utilizadorDB.utilizador_id == utilizador.id,
        Candidato_delegado_utilizadorDB.votacao_delegado_id == votacao.id
    ).first()

    if candidato_existente:
        raise HTTPException(status_code=400, detail="Já estás registado como candidato nesta votação.")
    
    novo_candidato = Candidato_delegado_utilizadorDB(
        utilizador_id=utilizador.id,
        votacao_delegado_id=votacao.id
    )
    
    db.add(novo_candidato)
    db.commit()
    db.refresh(novo_candidato)

    return {"status": "SUCCESS", "message": "Candidato registado com sucesso", "utilizador_id": novo_candidato.utilizador_id, "votacao_id": novo_candidato.votacao_delegado_id}

@app.get("/api/candidatos/delegado/{votacao_id}")
def listar_candidatos_delegado(votacao_id: int, db=Depends(get_db)):
    candidatos = (
        db.query(Candidato_delegado_utilizadorDB)
        .filter(Candidato_delegado_utilizadorDB.votacao_delegado_id == votacao_id)
        .all()
    )
    return {
        "status": "SUCCESS",
        "candidatos": [
            {
                "id": c.id,
                "utilizador_id": c.utilizador_id,
                "votacao_delegado_id": c.votacao_delegado_id,
                "nome": c.utilizador.nome,
                "descricao": c.descricao,
            }
            for c in candidatos
        ],
    }

@app.get("/api/candidatos/lista/{votacao_id}")
def listar_candidatos_lista(votacao_id: int, db=Depends(get_db)):
    candidatos = (
        db.query(Candidato_listaDB)
        .filter(Candidato_listaDB.votacao_lista_id == votacao_id)
        .all()
    )
    return {
        "status": "SUCCESS",
        "candidatos": [
            {
                "id": c.id,
                "titulo": c.titulo,
                "votacao_lista_id": c.votacao_lista_id,
                "descricao": c.descricao,
            }
            for c in candidatos
        ],
    }

@app.post("/api/votos/delegado")
def votar_delegado(req: VotoDelegadoRequest, db=Depends(get_db)):
    utilizador = db.query(UtilizadorDB).filter(UtilizadorDB.id == req.utilizador_id).first()
    if not utilizador:
        raise HTTPException(status_code=404, detail="utilizador não encontrado.")
    
    votacao_delegado = db.query(Votacao_delegadoDB).filter(Votacao_delegadoDB.id == req.votacao_id).first()
    if not votacao_delegado:
            raise HTTPException(status_code=404, detail="votacao_turma não encontrado.")
    
    if utilizador.turma_id != votacao_delegado.turma_id:
        raise HTTPException(status_code=400, detail="Não podes votar nesta votação.")

    voto_existente = db.query(Voto_utilizador_delegadoDB).filter( Voto_utilizador_delegadoDB.utilizador_id == utilizador.id, Voto_utilizador_delegadoDB.votacao_delegado_id == votacao_delegado.id).first()

    if voto_existente:
        raise HTTPException(status_code=400, detail="Já votaste nesta votação.")
    
    candidato = db.query(Candidato_delegado_utilizadorDB).filter(Candidato_delegado_utilizadorDB.id == req.escolha).first()
    if not candidato:
        raise HTTPException(status_code=404, detail="Escolha (candidato) não encontrado.")

    if candidato.votacao_delegado_id != votacao_delegado.id:
        raise HTTPException(status_code=400, detail="Escolha não pertence a esta votação.")

    novo_voto = Voto_utilizador_delegadoDB(
        utilizador_id=utilizador.id,
        votacao_delegado_id=votacao_delegado.id,
        escolha=candidato.id,
    )

    try:
        db.add(novo_voto)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao registar voto. Verifique a integridade dos dados.")

    return {"status": "SUCCESS", "message": "Vote registered"}

@app.get("/api/resultados/delegado")
def resultados_delegado(votacao_id: int, db=Depends(get_db)):
    resultados = (
        db.query(
            Candidato_delegado_utilizadorDB.id,
            UtilizadorDB.nome,
            func.count(Voto_utilizador_delegadoDB.escolha).label("votos")
        )
        .join(UtilizadorDB, UtilizadorDB.id == Candidato_delegado_utilizadorDB.utilizador_id)
        .outerjoin(Voto_utilizador_delegadoDB, Voto_utilizador_delegadoDB.escolha == Candidato_delegado_utilizadorDB.id)
        .filter(Candidato_delegado_utilizadorDB.votacao_delegado_id == votacao_id)
        .group_by(Candidato_delegado_utilizadorDB.id, UtilizadorDB.nome)
        .all()
    )
    return {
        "status": "SUCCESS",
        "resultados": [{"candidato_id": r.id, "nome": r.nome, "votos": r.votos} for r in resultados]
    }


# VOTAÇÕES DE LISTA

@app.post("/api/votacoes/lista")
def criar_votacao_lista(req: VotacaoListaRequest, db=Depends(get_db)):
    novo_votacao_lista = Votacao_listaDB(
        titulo=req.titulo,
        start_date=req.start_date,
        end_date=req.end_date,
    )

    db.add(novo_votacao_lista)
    db.commit()
    db.refresh(novo_votacao_lista)

    return {"status": "SUCCESS", "message": "Votação de lista registered", "votacao_id": novo_votacao_lista.id}

@app.get("/api/votacoes/lista")
def listar_votacoes_lista(db=Depends(get_db)):
    votacoes = db.query(Votacao_listaDB).all()
    return {
        "status": "SUCCESS",
        "votacoes": [
            {
                "id": v.id,
                "titulo": v.titulo,
                "start_date": v.start_date,
                "end_date": v.end_date,
            }
            for v in votacoes
        ],
    }

@app.delete("/api/votacoes/lista/{votacao_id}")
def deletar_votacao_lista(votacao_id: int, utilizador_id: int, db=Depends(get_db)):
    require_admin(utilizador_id, db)
    votacao = db.query(Votacao_listaDB).filter(Votacao_listaDB.id == votacao_id).first()
    if not votacao:
        raise HTTPException(status_code=404, detail="Votação não encontrada.")
    db.query(Voto_utilizador_listaDB).filter(Voto_utilizador_listaDB.votacao_lista_id == votacao_id).delete()
    db.query(Candidato_listaDB).filter(Candidato_listaDB.votacao_lista_id == votacao_id).delete()
    db.delete(votacao)
    db.commit()
    return {"status": "SUCCESS", "message": "Votação eliminada."}

@app.post("/api/candidatos/lista")
def registrar_candidato_lista(req: CandidatoListaRequest, db=Depends(get_db)):
    
    votacao = db.query(Votacao_listaDB).filter(Votacao_listaDB.id == req.votacao_id).first()
    if not votacao:
        raise HTTPException(status_code=404, detail="votacao não encontrado.")
    
    candidato_existente = db.query(Candidato_listaDB).filter(
        Candidato_listaDB.titulo == req.titulo,
    ).first()

    if candidato_existente:
        raise HTTPException(status_code=400, detail="Já estás registado como candidato nesta votação.")
    
    novo_candidato = Candidato_listaDB(
        votacao_lista_id=votacao.id,
        titulo=req.titulo,
        descricao=req.descricao
    )
    
    db.add(novo_candidato)
    db.commit()
    db.refresh(novo_candidato)

    return {"status": "SUCCESS", "message": "Candidato registado com sucesso", "votacao_id": novo_candidato.votacao_lista_id}


@app.post("/api/votos/lista")
def votar_lista(req: VotoListaRequest, db=Depends(get_db)):
    utilizador = db.query(UtilizadorDB).filter(UtilizadorDB.id == req.utilizador_id).first()
    if not utilizador:
        raise HTTPException(status_code=404, detail="utilizador não encontrado.")
    
    votacao_lista = db.query(Votacao_listaDB).filter(Votacao_listaDB.id == req.votacao_id).first()
    if not votacao_lista:
            raise HTTPException(status_code=404, detail="votacao_turma não encontrado.")
    voto_existente = db.query(Voto_utilizador_listaDB).filter(
        Voto_utilizador_listaDB.utilizador_id == utilizador.id,
        Voto_utilizador_listaDB.votacao_lista_id == votacao_lista.id,
    ).first()

    if voto_existente:
        raise HTTPException(status_code=400, detail="Já votaste nesta votação.")

    candidato = db.query(Candidato_listaDB).filter(Candidato_listaDB.id == req.escolha).first()
    if not candidato:
        raise HTTPException(status_code=404, detail="Escolha (candidato) não encontrado.")

    novo_voto = Voto_utilizador_listaDB(
        utilizador_id=utilizador.id,
        votacao_lista_id=votacao_lista.id,
        escolha=candidato.id,
    )

    try:
        db.add(novo_voto)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao registar voto na lista.")

    return {"status": "SUCCESS", "message": "Vote registered"}

@app.get("/api/resultados/lista")
def resultados_lista(votacao_id: int, db=Depends(get_db)):
    resultados = (
        db.query(
            Candidato_listaDB.id,
            Candidato_listaDB.titulo,
            func.count(Voto_utilizador_listaDB.escolha).label("votos")
        )
        .outerjoin(Voto_utilizador_listaDB, Voto_utilizador_listaDB.escolha == Candidato_listaDB.id)
        .filter(Candidato_listaDB.votacao_lista_id == votacao_id)
        .group_by(Candidato_listaDB.id, Candidato_listaDB.titulo)
        .all()
    )
    return {
        "status": "SUCCESS",
        "resultados": [{"candidato_id": r.id, "titulo": r.titulo, "votos": r.votos} for r in resultados]
    }

#VERIFICAÇÕES
@app.get("/api/votos/delegado/verificar")
def verificar_voto_delegado(utilizador_id: int, votacao_id: int, db=Depends(get_db)):
    utilizador = db.query(UtilizadorDB).filter(UtilizadorDB.id == utilizador_id).first()
    votacao = db.query(Votacao_delegadoDB).filter(Votacao_delegadoDB.id == votacao_id).first()

    turma_errada = utilizador and votacao and utilizador.turma_id != votacao.turma_id
    ja_votou = db.query(Voto_utilizador_delegadoDB).filter(
        Voto_utilizador_delegadoDB.utilizador_id == utilizador_id,
        Voto_utilizador_delegadoDB.votacao_delegado_id == votacao_id
    ).first() is not None

    return {"ja_votou": ja_votou, "turma_errada": turma_errada}

@app.get("/api/votos/lista/verificar")
def verificar_voto_lista(utilizador_id: int, votacao_id: int, db=Depends(get_db)):
    ja_votou = db.query(Voto_utilizador_listaDB).filter(
        Voto_utilizador_listaDB.utilizador_id == utilizador_id,
        Voto_utilizador_listaDB.votacao_lista_id == votacao_id
    ).first() is not None

    return {"ja_votou": ja_votou, "turma_errada": False}

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    seed_database()