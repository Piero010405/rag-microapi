# RAG MicroAPI

Micro API para pruebas y operación del módulo RAG del sistema de inspección PCB.

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -e .
cp .env.example .env
uvicorn app.main:app --reload
