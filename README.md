# Presentation
Experiment on FastAPI.
Simple backend serving Marvel characters.

## init project
In a virtual env:
```bash
pip install -r requirements.txt
```

Then fill the db:
```bash
sqlite3 data.db < init-data.sql
```

## Launch server

```bash
uvicorn main:app --reload
```
Go to http://localhost:8000/