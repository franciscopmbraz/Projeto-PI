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
    ja_votou = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)

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
        senha=signup_request.senha 
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

