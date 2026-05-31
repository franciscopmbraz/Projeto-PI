from sqlalchemy.exc import IntegrityError

from database import SessionLocal
from models import (
    TurmaDB,
    UtilizadorDB,
    Votacao_delegadoDB,
    Candidato_delegado_utilizadorDB,
    Voto_utilizador_delegadoDB,
    Votacao_listaDB,
    Candidato_listaDB,
    Voto_utilizador_listaDB,
)

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_turma(db, nome: str):
    turma = db.query(TurmaDB).filter(TurmaDB.nome == nome).first()
    if turma:
        return turma

    turma = TurmaDB(nome=nome)
    db.add(turma)
    db.commit()
    db.refresh(turma)
    return turma


def create_utilizador(db, numero: str, nome: str, turma_id: int, senha: str):
    utilizador = db.query(UtilizadorDB).filter(UtilizadorDB.numero == numero).first()
    if utilizador:
        return utilizador

    senha_hash = pwd_context.hash(senha)
    utilizador = UtilizadorDB(numero=numero, nome=nome, turma_id=turma_id, is_admin=False, senha=senha_hash)
    db.add(utilizador)
    db.commit()
    db.refresh(utilizador)
    return utilizador

def create_admin(db, numero: str, nome: str, senha: str):
    existente = db.query(UtilizadorDB).filter(UtilizadorDB.numero == numero).first()
    if existente:
        return existente

    senha_hash = pwd_context.hash(senha)
    admin = UtilizadorDB(numero=numero, nome=nome, senha=senha_hash, is_admin=True, turma_id=None)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

def create_votacao_delegado(db, turma_id: int, titulo: str, start_date=None, end_date=None):
    votacao = (
        db.query(Votacao_delegadoDB)
        .filter(Votacao_delegadoDB.turma_id == turma_id, Votacao_delegadoDB.titulo == titulo)
        .first()
    )
    if votacao:
        return votacao

    votacao = Votacao_delegadoDB(turma_id=turma_id, titulo=titulo, start_date=start_date, end_date=end_date)
    db.add(votacao)
    db.commit()
    db.refresh(votacao)
    return votacao


def create_candidato_delegado(db, utilizador_id: int, votacao_delegado_id: int, descricao: str = None):
    candidato = (
        db.query(Candidato_delegado_utilizadorDB)
        .filter(
            Candidato_delegado_utilizadorDB.utilizador_id == utilizador_id,
            Candidato_delegado_utilizadorDB.votacao_delegado_id == votacao_delegado_id,
        )
        .first()
    )
    if candidato:
        return candidato

    candidato = Candidato_delegado_utilizadorDB(
        utilizador_id=utilizador_id,
        votacao_delegado_id=votacao_delegado_id,
        descricao=descricao,
    )
    db.add(candidato)
    db.commit()
    db.refresh(candidato)
    return candidato


def create_voto_delegado(db, utilizador_id: int, votacao_delegado_id: int, escolha_id: int):
    voto = (
        db.query(Voto_utilizador_delegadoDB)
        .filter(
            Voto_utilizador_delegadoDB.utilizador_id == utilizador_id,
            Voto_utilizador_delegadoDB.votacao_delegado_id == votacao_delegado_id,
        )
        .first()
    )
    if voto:
        return voto

    voto = Voto_utilizador_delegadoDB(
        utilizador_id=utilizador_id,
        votacao_delegado_id=votacao_delegado_id,
        escolha=escolha_id,
    )
    db.add(voto)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(voto)
    return voto


def create_votacao_lista(db, titulo: str, start_date=None, end_date=None):
    votacao = db.query(Votacao_listaDB).filter(Votacao_listaDB.titulo == titulo).first()
    if votacao:
        return votacao

    votacao = Votacao_listaDB(titulo=titulo, start_date=start_date, end_date=end_date)
    db.add(votacao)
    db.commit()
    db.refresh(votacao)
    return votacao


def create_candidato_lista(db, votacao_lista_id: int, titulo: str, descricao: str = None):
    candidato = (
        db.query(Candidato_listaDB)
        .filter(
            Candidato_listaDB.votacao_lista_id == votacao_lista_id,
            Candidato_listaDB.titulo == titulo,
        )
        .first()
    )
    if candidato:
        return candidato

    candidato = Candidato_listaDB(votacao_lista_id=votacao_lista_id, titulo=titulo, descricao=descricao)
    db.add(candidato)
    db.commit()
    db.refresh(candidato)
    return candidato


def create_voto_lista(db, utilizador_id: int, votacao_lista_id: int, escolha_id: int):
    voto = (
        db.query(Voto_utilizador_listaDB)
        .filter(
            Voto_utilizador_listaDB.utilizador_id == utilizador_id,
            Voto_utilizador_listaDB.votacao_lista_id == votacao_lista_id,
        )
        .first()
    )
    if voto:
        return voto

    voto = Voto_utilizador_listaDB(
        utilizador_id=utilizador_id,
        votacao_lista_id=votacao_lista_id,
        escolha=escolha_id,
    )
    db.add(voto)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(voto)
    return voto
