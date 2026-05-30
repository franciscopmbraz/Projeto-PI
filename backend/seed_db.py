from database import engine, SessionLocal, Base
from crud import (
    create_turma,
    create_utilizador,
    create_votacao_delegado,
    create_candidato_delegado,
    create_voto_delegado,
    create_votacao_lista,
    create_candidato_lista,
    create_voto_lista,
)

from models import TurmaDB, UtilizadorDB
from datetime import datetime, timedelta


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        turmas = {}
        for nome in ["10A", "10B", "10C"]:
            turmas[nome] = create_turma(db, nome)

        estudantes = [
            {"numero": "1001", "nome": "Ana Silva", "turma": "10A"},
            {"numero": "1002", "nome": "Beatriz Lima", "turma": "10A"},
            {"numero": "1003", "nome": "Carlos Sousa", "turma": "10A"},
            {"numero": "1004", "nome": "Diana Fernandes", "turma": "10A"},
            {"numero": "1005", "nome": "Eduardo Costa", "turma": "10A"},
            {"numero": "1006", "nome": "Fabio Almeida", "turma": "10A"},
            {"numero": "1007", "nome": "Gabriela Martins", "turma": "10A"},
            {"numero": "1008", "nome": "Hugo Pereira", "turma": "10A"},
            {"numero": "1101", "nome": "Ines Rocha", "turma": "10B"},
            {"numero": "1102", "nome": "Joao Teixeira", "turma": "10B"},
            {"numero": "1103", "nome": "Katia Nunes", "turma": "10B"},
            {"numero": "1104", "nome": "Luis Carvalho", "turma": "10B"},
            {"numero": "1105", "nome": "Marta Lopes", "turma": "10B"},
            {"numero": "1106", "nome": "Nuno Gomes", "turma": "10B"},
            {"numero": "1107", "nome": "Olga Pinto", "turma": "10B"},
            {"numero": "1108", "nome": "Paulo Santos", "turma": "10B"},
            {"numero": "1201", "nome": "Rita Ferreira", "turma": "10C"},
            {"numero": "1202", "nome": "Sara Rodrigues", "turma": "10C"},
            {"numero": "1203", "nome": "Tiago Machado", "turma": "10C"},
            {"numero": "1204", "nome": "Vera Cardoso", "turma": "10C"},
            {"numero": "1205", "nome": "Walter Almeida", "turma": "10C"},
            {"numero": "1206", "nome": "Xavier Santos", "turma": "10C"},
            {"numero": "1207", "nome": "Yara Silva", "turma": "10C"},
            {"numero": "1208", "nome": "Zoe Monteiro", "turma": "10C"},
        ]

        utilizadores = {}
        for aluno in estudantes:
            user = create_utilizador(
                db,
                numero=aluno["numero"],
                nome=aluno["nome"],
                turma_id=turmas[aluno["turma"]].id,
                senha="senha123",
            )
            utilizadores[aluno["numero"]] = user

        delegados = {}
        now = datetime.utcnow()
        week = timedelta(days=7)
        v10a = create_votacao_delegado(db, turmas["10A"].id, "Delegado 10A", start_date=now, end_date=now+week)
        v10b = create_votacao_delegado(db, turmas["10B"].id, "Delegado 10B", start_date=now, end_date=now+week)
        delegados["10A"] = v10a
        delegados["10B"] = v10b

        candidatos_10a = [
            create_candidato_delegado(db, utilizadores["1001"].id, v10a.id, descricao="Aluno 1001 - candidato 10A"),
            create_candidato_delegado(db, utilizadores["1002"].id, v10a.id, descricao="Aluno 1002 - candidato 10A"),
            create_candidato_delegado(db, utilizadores["1003"].id, v10a.id, descricao="Aluno 1003 - candidato 10A"),
        ]
        candidatos_10b = [
            create_candidato_delegado(db, utilizadores["1101"].id, v10b.id, descricao="Aluno 1101 - candidato 10B"),
            create_candidato_delegado(db, utilizadores["1102"].id, v10b.id, descricao="Aluno 1102 - candidato 10B"),
            create_candidato_delegado(db, utilizadores["1103"].id, v10b.id, descricao="Aluno 1103 - candidato 10B"),
        ]

        votos_10a = [
            ("1004", candidatos_10a[0].id),
            ("1005", candidatos_10a[1].id),
            ("1006", candidatos_10a[1].id),
            ("1007", candidatos_10a[2].id),
            ("1008", candidatos_10a[0].id),
        ]

        votos_10b = [
            ("1104", candidatos_10b[1].id),
            ("1105", candidatos_10b[2].id),
            ("1106", candidatos_10b[0].id),
            ("1107", candidatos_10b[0].id),
            ("1108", candidatos_10b[2].id),
        ]

        for numero, escolha_id in votos_10a:
            create_voto_delegado(db, utilizadores[numero].id, v10a.id, escolha_id)

        for numero, escolha_id in votos_10b:
            create_voto_delegado(db, utilizadores[numero].id, v10b.id, escolha_id)

        votacao_lista = create_votacao_lista(db, "Votação de Lista Escolar", start_date=now, end_date=now+week)
        candidatos_lista = [
            create_candidato_lista(db, votacao_lista.id, "Lista A", descricao="Lista A descrição"),
            create_candidato_lista(db, votacao_lista.id, "Lista B", descricao="Lista B descrição"),
            create_candidato_lista(db, votacao_lista.id, "Lista C", descricao="Lista C descrição"),
        ]

        votos_lista = [
            ("1001", candidatos_lista[0].id),
            ("1002", candidatos_lista[1].id),
            ("1003", candidatos_lista[2].id),
            ("1004", candidatos_lista[0].id),
            ("1005", candidatos_lista[1].id),
            ("1006", candidatos_lista[2].id),
            ("1101", candidatos_lista[0].id),
            ("1102", candidatos_lista[1].id),
            ("1201", candidatos_lista[2].id),
            ("1202", candidatos_lista[0].id),
        ]

        for numero, escolha_id in votos_lista:
            create_voto_lista(db, utilizadores[numero].id, votacao_lista.id, escolha_id)

        print("Seed completo: 24 utilizadores, 3 turmas, 2 votacoes delegado, 3 candidatos por votacao e 10 votos de lista.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
