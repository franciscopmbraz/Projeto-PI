from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class UtilizadorDB(Base):
    __tablename__ = "utilizadores"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(50), unique=True, index=True, nullable=False)
    nome = Column(String(100), nullable=True)
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=True)
    senha = Column(String(100), nullable=False)
    
    votos = relationship("Voto_utilizador_delegadoDB", back_populates="utilizador")
    candidaturas = relationship("Candidato_delegado_utilizadorDB", back_populates="utilizador")

    turma = relationship("TurmaDB", back_populates="utilizadores")

class TurmaDB(Base):
    __tablename__ = "turmas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(20), unique=True, nullable=False)

    utilizadores = relationship("UtilizadorDB", back_populates="turma")
    votacao_delegado = relationship("Votacao_delegadoDB", back_populates="turma")

class Votacao_delegadoDB(Base):
    __tablename__ = "votacao_delegado"

    id = Column(Integer, primary_key=True, index=True)
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)
    titulo = Column(String(100), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    votos = relationship("Voto_utilizador_delegadoDB", back_populates="votacao")
    candidatos = relationship("Candidato_delegado_utilizadorDB", back_populates="votacao")

    turma = relationship(
        "TurmaDB",
        back_populates="votacao_delegado"
    )

class Candidato_delegado_utilizadorDB(Base):
    __tablename__ = "candidato_delegado_utilizador"

    id = Column(Integer, primary_key=True, index=True)
    utilizador_id = Column(Integer, ForeignKey("utilizadores.id"), nullable=False)
    votacao_delegado_id = Column(Integer, ForeignKey("votacao_delegado.id"), nullable=False)
    descricao = Column(String(255), nullable=True)
    votos = relationship("Voto_utilizador_delegadoDB", back_populates="escolha_rel")

    utilizador = relationship(
        "UtilizadorDB",
        back_populates="candidaturas"
    )

    votacao = relationship(
        "Votacao_delegadoDB",
        back_populates="candidatos"
    )

class Voto_utilizador_delegadoDB(Base):
    __tablename__ = "voto_utilizador_delegado"

    utilizador_id = Column(Integer, ForeignKey("utilizadores.id"), primary_key=True)
    votacao_delegado_id = Column(Integer, ForeignKey("votacao_delegado.id"), primary_key=True)
    escolha = Column(Integer, ForeignKey("candidato_delegado_utilizador.id"), nullable=False)

    utilizador = relationship(
        "UtilizadorDB",
        back_populates="votos",
        foreign_keys=[utilizador_id]
    )

    votacao = relationship(
        "Votacao_delegadoDB",
        back_populates="votos",
        foreign_keys=[votacao_delegado_id]
    )

    escolha_rel = relationship(
        "Candidato_delegado_utilizadorDB",
        back_populates="votos",
        foreign_keys=[escolha]
    )   

class Votacao_listaDB(Base):
    __tablename__ = "votacao_lista"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    candidatos = relationship("Candidato_listaDB", back_populates="votacao")  

class Candidato_listaDB(Base):
    __tablename__ = "candidato_lista"

    id = Column(Integer, primary_key=True, index=True)
    votacao_lista_id = Column(Integer, ForeignKey("votacao_lista.id"), nullable=False)
    titulo = Column(String(100), nullable=True)
    descricao = Column(String(255), nullable=True)

    escolhas = relationship("Voto_utilizador_listaDB", back_populates="escolha_rel")

    votacao = relationship(
        "Votacao_listaDB",
        back_populates="candidatos"
    )

class Voto_utilizador_listaDB(Base):
    __tablename__ = "voto_utilizador_lista"

    utilizador_id = Column(Integer, ForeignKey("utilizadores.id"), primary_key=True)
    votacao_lista_id = Column(Integer, ForeignKey("votacao_lista.id"), primary_key=True)
    escolha = Column(Integer, ForeignKey("candidato_lista.id"), nullable=False)

    utilizador = relationship(
        "UtilizadorDB", 
        foreign_keys=[utilizador_id]
    )
    votacao = relationship(
        "Votacao_listaDB",
        foreign_keys=[votacao_lista_id]
    )
    escolha_rel = relationship(
        "Candidato_listaDB",
        foreign_keys=[escolha]
    )

