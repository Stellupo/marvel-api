from contextlib import contextmanager

from fastapi import FastAPI, HTTPException
import sqlite3

from starlette.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@contextmanager
def get_cursor():
    conn = sqlite3.connect('data.db')
    try:
        yield conn.cursor()
    finally:
        conn.close()


def serialize_character(row, cols):
    row = {col[0]: value for col, value in zip(cols, row)}
    row["abilities"] = row["abilities"].split(",")
    row["groups"] = [] if row["groups"] is None else [int(group_id) for group_id in row["groups"].split(",")]
    return row


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/api/characters")
def get_characters(name: str = ""):
    with get_cursor() as cur:
        cur.execute("""
            SELECT c.id, c.name, c.story, c.abilities, c.img, c.header, GROUP_CONCAT(GroupMember.group_id) as groups 
            FROM Character as c LEFT OUTER JOIN GroupMember on c.id = GroupMember.character_id 
            WHERE c.name LIKE ?
            GROUP BY c.id;
        """, (f"%{name}%",))
        response = [serialize_character(row, cur.description) for row in cur.fetchall()]
    return response


@app.get("/api/characters/{item_id}")
def get_character(item_id: int):
    with get_cursor() as cur:
        cur.execute("""
            SELECT c.id, c.name, c.story, c.abilities, c.img, c.header, GROUP_CONCAT(GroupMember.group_id) as groups 
            FROM Character as c LEFT OUTER JOIN GroupMember on c.id = GroupMember.character_id 
            WHERE c.id = ?
            GROUP BY c.id;
        """, (item_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return serialize_character(row, cur.description)


def serialize_group(row, cols):
    row = {col[0]: value for col, value in zip(cols, row)}
    row["members"] = [] if row["members"] is None else [int(group_id) for group_id in row["members"].split(",")]
    return row


@app.get("/api/groups")
def get_groups(name: str = ""):
    with get_cursor() as cur:
        cur.execute("""
            SELECT g.id, g.name, g.story, g.img, g.header, GROUP_CONCAT(GroupMember.character_id) as members 
            FROM "Group" as g LEFT OUTER JOIN GroupMember on g.id = GroupMember.group_id 
            WHERE g.name LIKE ?
            GROUP BY g.id;
        """, (f"%{name}%",))
        response = [serialize_group(row, cur.description) for row in cur.fetchall()]
    return response


@app.get("/api/groups/{item_id}")
def get_group(item_id: int):
    with get_cursor() as cur:
        cur.execute("""
            SELECT g.id, g.name, g.story, g.img, g.header, GROUP_CONCAT(GroupMember.character_id) as members 
            FROM "Group" as g LEFT OUTER JOIN GroupMember on g.id = GroupMember.group_id 
            WHERE g.id = ?
            GROUP BY g.id;
        """, (item_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return serialize_group(row, cur.description)
