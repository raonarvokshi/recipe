import sqlite3
from typing import List
from models.category import CategoryBase, Category, CategoryCreate
from database import get_db_connection
from fastapi import APIRouter, HTTPException, status


router = APIRouter()


@router.get("/categories", response_model=List[Category])
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("Select if, name from categories")
    categories = cursor.fetchall()
    conn.close()
    category_list = [{"id": cat[0], "name": cat[1]} for cat in categories]
    return category_list


@router.post("/categories", response_model=Category)
def create_category(category: CategoryCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "insert into categories (name) values (?)", (category.name))
        conn.commit()
        category_id = cursor.lastrowid
        return Category(id=category_id, name=category.name)

    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"The category {category.name} already exists")

    except Exception as e:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error is occurred: {e}")

    finally:
        conn.close()


@router.put("/categories/{category_id}", response_model=Category)
def update_category(category_id: int, category: CategoryCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("Update categories set name=? where id=?",
                   (category.name, category_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Category not found")
    conn.commit()
    conn.close()
    return Category(id=category_id, name=category.name)


@router.delete("/categories/{category_id}", response_model=dict)
def delete_category(category_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("Delete from categories where id=?", (category_id))

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404, detail=f"Category with id: {category_id} not found!")

    conn.commit()
    conn.close()
    return {"details": "Category deleted successfully!"}
