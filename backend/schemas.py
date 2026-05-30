from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SignupRequest(BaseModel):
    numero: str = Field(..., min_length=3)
    nome: Optional[str] = Field(None, min_length=1)
    turma_id: int = Field(..., gt=0)
    senha: str = Field(..., min_length=4)


class LoginRequest(BaseModel):
    numero: str = Field(..., min_length=3)
    senha: str = Field(..., min_length=4)


class VotacaoListaRequest(BaseModel):
    titulo: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class VotacaoDelegadoRequest(BaseModel):
    turma_id: int = Field(..., gt=0)
    titulo: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class VotoDelegadoRequest(BaseModel):
    utilizador_id: int
    votacao_id: int
    escolha: int


class VotoListaRequest(BaseModel):
    utilizador_id: int
    votacao_id: int
    escolha: int


class CandidatoDelegadoRequest(BaseModel):
    utilizador_id: int
    votacao_id: int
    descricao: Optional[str] = None


class CandidatoListaRequest(BaseModel):
    titulo: str
    votacao_id: int
    descricao: Optional[str] = None

class TurmaRequest(BaseModel):
    nome: str