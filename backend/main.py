import os
import uuid
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Column as DBColumn, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError


DB_USER = os.environ.get("DB_USER", "user_votacao")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "senha_segura")
DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("DB_NAME", "sve_db")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()


class AlunoDB(Base):
    __tablename__ = "alunos"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_aluno = Column(String(50), unique=True, index=True, nullable=False)
    ano_letivo = Column(String(20), nullable=True)
    senha = Column(String(100), nullable=False)
    voto_turma = Column(Boolean, default=False)
    voto_delegado = Column(Boolean, default=False)


class Votacao_turmaDB(Base):  
    __tablename__ = "votacao_turma"

    id = Column(Integer, primary_key=True, index=True)
    turma = Column(String(50), nullable=False)
    voto_delegado = Column(String(50), nullable=False)

class Votacao_listaDB(Base):
    __tablename__ = "votacao_lista"
    
    id = Column(Integer, primary_key=True, index=True)
    voto_lista = Column(String(50), nullable=False)


app = FastAPI(title="Sistema de Votação Eletrónica - API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SignupRequest(BaseModel):
    numero_aluno: str = Field(..., min_length=3)
    ano_letivo: str = Field(..., min_length=1)
    senha: str = Field(..., min_length=4)


@app.post("/auth/signup")
def signup(signup_request: SignupRequest, db: Session = Depends(get_db)):
    # Check if the student already exists
    existing_student = db.query(AlunoDB).filter(AlunoDB.numero_aluno == signup_request.numero_aluno).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Student already exists")

    # Create new student
    novo_aluno = AlunoDB(
        numero_aluno=signup_request.numero_aluno,
        ano_letivo=signup_request.ano_letivo,
        senha=signup_request.senha,
        voto_turma=False,
        voto_delegado=False
    )
    try:
        db.add(novo_aluno)
        db.commit()
        db.refresh(novo_aluno)
        return {"message": "Student registered successfully", "student_id": novo_aluno.id}
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, 
            detail=f"Erro de concorrência detetado. Transação abortada. (ID: {novo_aluno.id})"
        )
    
class LoginRequest(BaseModel):
    numero_aluno: str = Field(..., min_length=3)
    senha: str = Field(..., min_length=4)

@app.post("/auth/login")
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    #Procura o aluno na base de dados
    aluno = db.query(AlunoDB).filter(AlunoDB.numero_aluno == login_request.numero_aluno).first()
    
    #Verifica se o aluno existe e se a senha está correta
    if not aluno or aluno.senha != login_request.senha:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    
    # 3. Se estiver tudo bem, dá permissão para entrar
    return {
        "status": "sucesso", 
        "mensagem": "Autenticação efetuada com sucesso!",
        "voto_turma": aluno.voto_turma,
        "voto_delegado": aluno.voto_delegado
    }

class CandidatoDB(Base):
    __tablename__ = "candidatos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False) # 'lista' ou 'delegado'
    turma = Column(String(20), nullable=True) # Apenas usado se for 'delegado'



class VotoListaRequest(BaseModel):
    numero_aluno: str
    escolha: str

class VotoDelegadoRequest(BaseModel):
    numero_aluno: str
    escolha: str


@app.get("/api/candidatos/{numero_aluno}")
def obter_candidatos(numero_aluno: str, db: Session = Depends(get_db)):
    aluno = db.query(AlunoDB).filter(AlunoDB.numero_aluno == numero_aluno).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")
    
    # Obtém apenas os candidatos da turma dele
    listas = db.query(CandidatoDB).filter(CandidatoDB.tipo == "lista").all()
    delegados = db.query(CandidatoDB).filter(CandidatoDB.tipo == "delegado", CandidatoDB.turma == aluno.ano_letivo).all()
    
    return {
        "turma": aluno.ano_letivo,
        "listas": [{"id": c.nome.lower().replace(" ", "_"), "nome": c.nome} for c in listas],
        "delegados": [{"id": c.nome.lower().replace(" ", "_"), "nome": c.nome} for c in delegados],
        "ja_votou_lista": aluno.voto_turma,
        "ja_votou_delegado": aluno.voto_delegado
    }


@app.post("/api/votar/lista")
def votar_lista(req: VotoListaRequest, db: Session = Depends(get_db)):

    aluno = db.query(AlunoDB).filter(AlunoDB.numero_aluno == req.numero_aluno).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")
    if aluno.voto_turma:
        raise HTTPException(status_code=400, detail="Já votaste na Lista da Associação!")

    # Cria o voto sem número de aluno
    novo_voto = Votacao_listaDB(voto_lista=req.escolha)
    db.add(novo_voto)
    
    # Bloqueia o aluno para não votar mais nesta eleição
    aluno.voto_turma = True
    db.commit()
    
    return {"status": "sucesso", "mensagem": "Voto na Associação registado anonimamente!"}


@app.post("/api/votar/delegado")
def votar_delegado(req: VotoDelegadoRequest, db: Session = Depends(get_db)):
    aluno = db.query(AlunoDB).filter(AlunoDB.numero_aluno == req.numero_aluno).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")
    if aluno.voto_delegado:
        raise HTTPException(status_code=400, detail="Já votaste no Delegado de turma!")

    # Cria o voto anónimo mas guarda o ano/turma para sabermos a quem pertence o voto
    novo_voto = Votacao_turmaDB(turma=aluno.ano_letivo, voto_delegado=req.escolha)
    db.add(novo_voto)
    
    # Bloqueia o aluno nesta eleição
    aluno.voto_delegado = True
    db.commit()
    
    return {"status": "sucesso", "mensagem": "Voto no Delegado registado anonimamente!"}  


def popular_candidatos_iniciais(db: Session):
    # Verifica se a tabela já tem dados para não duplicar
    if db.query(CandidatoDB).first():
        return

    candidatos = [
        CandidatoDB(nome="Lista A - A Nossa Voz", tipo="lista"),
        CandidatoDB(nome="Lista B - Estudantes Unidos", tipo="lista"),
        CandidatoDB(nome="João Pedro", tipo="delegado", turma="10A"),
        CandidatoDB(nome="Maria Silva", tipo="delegado", turma="10A"),
        CandidatoDB(nome="Francisco Braz", tipo="delegado", turma="12D")
    ]
    db.add_all(candidatos)
    db.commit()
    

Base.metadata.create_all(bind=engine) 
db = SessionLocal()
popular_candidatos_iniciais(db)