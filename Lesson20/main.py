from fastapi import FastAPI
from routers import recipe, category
import os
from dotenv import load_dotenv
from database import get_db_connection
import uvicorn

load_dotenv()

Database_Url = os.getenv("Database_url")

app = FastAPI()

app.include_router(recipe.router)
app.include_router(category.router)


@app.on_event("startup")
def startup():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        create table if not exists categories (
            id integer primary key autoincrement,
            name text unique not null
        )
    """)

    cursor.execute("""
        create table if not exists recipes (
            id integer primary key autoincrement,
            name text not null,
            description text,
            ingridients text,
            instructions text,
            cuisine text,
            difficulty text,
            category_id integer,
            foreign key (category_id) references categories (id)
        )
    """)

    conn.commit()
    conn.close()


@app.get("/")
def read_root():
    return {"message": "FastAPI with SQLite3 databae project"}


if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port="8000", reload=True)
