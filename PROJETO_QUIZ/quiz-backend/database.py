# database.py
import sqlite3
from typing import Dict, List

DATABASE_FILE = "ranking.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            total_score INTEGER NOT NULL DEFAULT 0,
            host_name TEXT NOT NULL,
            UNIQUE(player_name, host_name)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            incorrect_answer_1 TEXT NOT NULL,
            incorrect_answer_2 TEXT NOT NULL,
            incorrect_answer_3 TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            created_by TEXT NOT NULL 
        )
    """)
    conn.commit()
    conn.close()
    print("Banco de dados 'ranking.db' inicializado com sucesso.")

def update_player_score(player_name: str, score_to_add: int, host_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ranking WHERE player_name = ? AND host_name = ?", (player_name, host_name))
    player = cursor.fetchone()
    if player:
        new_score = player["total_score"] + score_to_add
        cursor.execute("UPDATE ranking SET total_score = ? WHERE player_name = ? AND host_name = ?", (new_score, player_name, host_name))
    else:
        cursor.execute("INSERT INTO ranking (player_name, total_score, host_name) VALUES (?, ?, ?)", (player_name, score_to_add, host_name))
    conn.commit()
    conn.close()
    print(f"Ranking de '{host_name}': Pontuação de '{player_name}' atualizada com {score_to_add} pontos.")

def get_ranking(host_name: str, limit: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT player_name, total_score FROM ranking WHERE host_name = ? ORDER BY total_score DESC LIMIT ?", (host_name, limit))
    ranking_data = cursor.fetchall()
    conn.close()
    return [{"name": row["player_name"], "score": row["total_score"]} for row in ranking_data]

def add_question(question_data: Dict, player_name: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO custom_questions (question_text, correct_answer, incorrect_answer_1, incorrect_answer_2, incorrect_answer_3, difficulty, created_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            question_data["question_text"], question_data["correct_answer"],
            question_data["incorrect_answers"][0], question_data["incorrect_answers"][1],
            question_data["incorrect_answers"][2], question_data["difficulty"],
            player_name
        )
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_questions_by_player(player_name: str) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM custom_questions WHERE created_by = ?", (player_name,))
    questions_data = cursor.fetchall()
    conn.close()
    formatted_questions = []
    for row in questions_data:
        formatted_questions.append({
            "id": row["id"], "question": row["question_text"],
            "options": [row["correct_answer"], row["incorrect_answer_1"], row["incorrect_answer_2"], row["incorrect_answer_3"]],
            "correctAnswer": row["correct_answer"], "difficulty": row["difficulty"]
        })
    return formatted_questions

def update_question(question_id: int, question_data: Dict, player_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE custom_questions SET question_text = ?, correct_answer = ?, incorrect_answer_1 = ?, incorrect_answer_2 = ?, incorrect_answer_3 = ?, difficulty = ? WHERE id = ? AND created_by = ?",
        (
            question_data["question_text"], question_data["correct_answer"],
            question_data["incorrect_answers"][0], question_data["incorrect_answers"][1],
            question_data["incorrect_answers"][2], question_data["difficulty"],
            question_id, player_name
        )
    )
    conn.commit()
    conn.close()

def delete_question(question_id: int, player_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM custom_questions WHERE id = ? AND created_by = ?", (question_id, player_name))
    conn.commit()
    conn.close()