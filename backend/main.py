from fastapi import FastAPI

app = FastAPI(title="SVE - API Básica")

@app.get("/")
def raiz():
    return {"status": "Sucesso", "mensagem": "O backend do teu SVE está a rodar no Docker!"}