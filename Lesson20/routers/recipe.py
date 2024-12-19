from fastapi import APIRouter, HTTPException, status
from typing import List
from models.recipe import Recipe, RecipeCreate
from database import get_db_connection


router = APIRouter()


def category_exists(category_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("Select 1 from categories where id=?", (category_id))
    result = cursor.execute()
    conn.close()
    return result is not None


@router.get("/recipes", response_model=List[Recipe])
def get_recipes(cuisine: str = None, difficulty: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "Select * from recipes where 1=1"
    params = []
    if cuisine:
        query += "AND cuisine=?"
        params.append(cuisine)
    if difficulty:
        query = "AND difficulty=?"
        params.append(difficulty)
    cursor.execute(query, params)
    recipes = cursor.fetchall()
    conn.close()
    return [
        Recipe(
            id=row[0], name=row[1], description=row[2],
            ingridients=row[3], instructions=row[4], cuisine=row[5],
            difficulty=row[6], category_id=row[7]
        )
        for row in recipes
    ]


@router.post("/recipes/", response_model=Recipe)
def create_recipe(recipe: RecipeCreate):
    if not category_exists(recipe.category_id):
        raise HTTPException(status_code=400, detail="Category does not exist")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "Insert into recipes (name, description, ingredients, instructions, cuisine, difficulty, category_id) Values (?, ?, ?, ?, ?, ?, ?)", (recipe.name, recipe.description, recipe.ingridients, recipe.instructions, recipe.cuisine, recipe.difficulty, recipe.category_id))
    conn.commit()
    recipe_id = cursor.lastrowid
    conn.close()
    return Recipe(id=recipe_id, name=recipe.name, description=recipe.description, ingridients=recipe.ingridients, cuisine=recipe.cuisine, difficulty=recipe.difficulty, category_id=recipe.category_id)


@router.put("/recipes/{recipe_id}", response_model=Recipe)
def update_recipe(recipe_id: int, recipe: RecipeCreate):
    if not category_exists(recipe, recipe.category_id):
        raise HTTPException(status_code=400, detail="Category does not exist")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "Update recipes set name=?, description=?, ingridients=? instructions=?, cuisine=?, difficulty=?, category_id=? where id=?", (recipe.name, recipe.description, recipe.ingridients, recipe.instructions, recipe.cuisine, recipe.difficulty, recipe.category_id))

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Recipe not found")
    conn.commit()
    conn.close()

    return Recipe(id=recipe_id, name=recipe.name, description=recipe.description, ingridients=recipe.ingridients, cuisine=recipe.cuisine, difficulty=recipe.difficulty, category_id=recipe.category_id)


@router.delete("/recipes/{recipe_id}", response_model=dict)
def delete_recipe(recipe_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("Delete from recipes where id=?", (recipe_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Recipe not found")
    conn.commit()
    conn.close()
    return {"Detail": "Recipe deleted successfully!"}
