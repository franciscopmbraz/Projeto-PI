from database import engine, SessionLocal, Base
from crud import (
    create_turma,
    create_utilizador,
    create_admin,
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
        if db.query(TurmaDB).first():
            admin = db.query(UtilizadorDB).filter(UtilizadorDB.numero == "admin").first()
            if not admin:
                create_admin(db, numero="admin", nome="Administrador", senha="admin")
                print("Admin criado.")
            print("Database already seeded, skipping.")
            return

        turmas = {}
        for nome in ["DSA", "TOT", "PI"]:
            turmas[nome] = create_turma(db, nome)

        estudantes = [
            {"numero": "1001", "nome": "Ana Silva",        "turma": "DSA"},
            {"numero": "1002", "nome": "Beatriz Lima",     "turma": "DSA"},
            {"numero": "1003", "nome": "Carlos Sousa",     "turma": "DSA"},
            {"numero": "1004", "nome": "Diana Fernandes",  "turma": "DSA"},
            {"numero": "1005", "nome": "Eduardo Costa",    "turma": "DSA"},
            {"numero": "1006", "nome": "Fabio Almeida",    "turma": "DSA"},
            {"numero": "1007", "nome": "Gabriela Martins", "turma": "DSA"},
            {"numero": "1008", "nome": "Hugo Pereira",     "turma": "DSA"},
            {"numero": "1101", "nome": "Ines Rocha",       "turma": "TOT"},
            {"numero": "1102", "nome": "Joao Teixeira",    "turma": "TOT"},
            {"numero": "1103", "nome": "Katia Nunes",      "turma": "TOT"},
            {"numero": "1104", "nome": "Luis Carvalho",    "turma": "TOT"},
            {"numero": "1105", "nome": "Marta Lopes",      "turma": "TOT"},
            {"numero": "1106", "nome": "Nuno Gomes",       "turma": "TOT"},
            {"numero": "1107", "nome": "Olga Pinto",       "turma": "TOT"},
            {"numero": "1108", "nome": "Paulo Santos",     "turma": "TOT"},
            {"numero": "1201", "nome": "Rita Ferreira",    "turma": "PI"},
            {"numero": "1202", "nome": "Sara Rodrigues",   "turma": "PI"},
            {"numero": "1203", "nome": "Tiago Machado",    "turma": "PI"},
            {"numero": "1204", "nome": "Vera Cardoso",     "turma": "PI"},
            {"numero": "1205", "nome": "Walter Almeida",   "turma": "PI"},
            {"numero": "1206", "nome": "Xavier Santos",    "turma": "PI"},
            {"numero": "1207", "nome": "Yara Silva",       "turma": "PI"},
            {"numero": "1208", "nome": "Zoe Monteiro",     "turma": "PI"},
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

        create_admin(db, numero="admin", nome="Administrador", senha="admin")

        now = datetime.utcnow()
        week = timedelta(days=7)
        past = now - timedelta(days=14)

        vDSA = create_votacao_delegado(db, turmas["DSA"].id, "Delegado DSA", start_date=now, end_date=now + week)
        vTOT = create_votacao_delegado(db, turmas["TOT"].id, "Delegado TOT", start_date=now, end_date=now + week)

        cDSA = [
            create_candidato_delegado(db, utilizadores["1001"].id, vDSA.id, descricao="Quero melhorar a comunicação entre a turma e os professores."),
            create_candidato_delegado(db, utilizadores["1002"].id, vDSA.id, descricao="Vou defender os interesses dos alunos da DSA."),
            create_candidato_delegado(db, utilizadores["1003"].id, vDSA.id, descricao="Organização e responsabilidade são as minhas prioridades."),
        ]
        cTOT = [
            create_candidato_delegado(db, utilizadores["1101"].id, vTOT.id, descricao="Representar a turma com dedicação e honestidade."),
            create_candidato_delegado(db, utilizadores["1102"].id, vTOT.id, descricao="Quero ser a voz da TOT junto da direção."),
            create_candidato_delegado(db, utilizadores["1103"].id, vTOT.id, descricao="Focada em resolver os problemas do dia a dia da turma."),
        ]

        for numero, escolha in [("1004", cDSA[0].id), ("1005", cDSA[0].id), ("1006", cDSA[1].id), ("1007", cDSA[2].id), ("1008", cDSA[0].id)]:
            create_voto_delegado(db, utilizadores[numero].id, vDSA.id, escolha)

        for numero, escolha in [("1104", cTOT[1].id), ("1105", cTOT[2].id), ("1106", cTOT[2].id), ("1107", cTOT[0].id), ("1108", cTOT[2].id)]:
            create_voto_delegado(db, utilizadores[numero].id, vTOT.id, escolha)

        vPI_old = create_votacao_delegado(db, turmas["PI"].id, "Delegado PI", start_date=past - week, end_date=past)

        cPI = [
            create_candidato_delegado(db, utilizadores["1201"].id, vPI_old.id, descricao="Candidata ao cargo de delegada."),
            create_candidato_delegado(db, utilizadores["1202"].id, vPI_old.id, descricao="Candidato ao cargo de delegado."),
        ]

        for numero, escolha in [("1203", cPI[0].id), ("1204", cPI[0].id), ("1205", cPI[1].id), ("1206", cPI[1].id), ("1207", cPI[1].id), ("1208", cPI[1].id)]:
            create_voto_delegado(db, utilizadores[numero].id, vPI_old.id, escolha)

        vl_active = create_votacao_lista(db, "Associação de Estudantes 2025", start_date=now, end_date=now + week)
        cl_active = [
            create_candidato_lista(db, vl_active.id, "Lista Azul",   descricao="Melhoria dos espaços comuns e representação estudantil."),
            create_candidato_lista(db, vl_active.id, "Lista Verde",  descricao="Sustentabilidade e bem-estar dos alunos."),
            create_candidato_lista(db, vl_active.id, "Lista Unida",  descricao="União de todos os estudantes para uma escola melhor."),
        ]

        for numero, escolha in [("1001", cl_active[0].id), ("1002", cl_active[1].id), ("1003", cl_active[2].id), ("1004", cl_active[0].id), ("1005", cl_active[1].id)]:
            create_voto_lista(db, utilizadores[numero].id, vl_active.id, escolha)

        vl_old = create_votacao_lista(db, "Associação de Estudantes 2024", start_date=past - week, end_date=past)
        cl_old = [
            create_candidato_lista(db, vl_old.id, "Lista A", descricao="Lista A."),
            create_candidato_lista(db, vl_old.id, "Lista B", descricao="Lista B."),
        ]

        for numero, escolha in [("1101", cl_old[0].id), ("1102", cl_old[1].id), ("1103", cl_old[0].id), ("1104", cl_old[1].id), ("1105", cl_old[0].id), ("1106", cl_old[0].id), ("1201", cl_old[1].id), ("1202", cl_old[0].id)]:
            create_voto_lista(db, utilizadores[numero].id, vl_old.id, escolha)

        print("Seed completo.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()