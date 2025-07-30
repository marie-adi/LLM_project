iniciar proyecto:
Crear el entorno virtual con venv:

Linux/Mac
```textplain
python3.10 -m venv .venv
```
Windows
```textplain
python -m venv .venv
```

Inicio el entorno virtual

Linux/Mac
```textplain
source .venv/bin/activate
```
Windows
```textplain
.venv\Scripts\activate
```
> [!IMPORTANT]
> instalar primero en el entorno virtual `python -m spacy download en_core_web_sm`

Instalar dependencias
```textplain
pip install -r requirements.txt
```


Abre 2 terminales:
Terminal backend:

```bash
uvicorn server.main:app --reload --port 8001
```

Terminal frontend:

Windows
```bash
cd client
python app.py 
```

Linux/Mac

```bash
cd client
python3 app.py 
```
