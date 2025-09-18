# database.py (Versão para Supabase/PostgreSQL)
import os
import psycopg2
from psycopg2.extras import DictCursor
from typing import Dict, List

# Pega a URL do banco de dados das variáveis de ambiente da Render
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Cria e retorna uma nova conexão com o banco de dados PostgreSQL."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    """Inicializa as tabelas do banco de dados se elas não existirem."""
    conn = get_db_connection()
    # Usar DictCursor permite acessar colunas pelo nome (ex: row['player_name'])
    cur = conn.cursor(cursor_factory=DictCursor)
    
    # Sintaxe do PostgreSQL para auto-incremento é SERIAL PRIMARY KEY
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ranking (
            id SERIAL PRIMARY KEY,
            player_name TEXT NOT NULL,
            total_score INTEGER NOT NULL DEFAULT 0,
            host_name TEXT NOT NULL,
            UNIQUE(player_name, host_name)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS custom_questions (
            id SERIAL PRIMARY KEY,
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
    cur.close()
    conn.close()
    print("Banco de dados PostgreSQL inicializado com sucesso.")

def update_player_score(player_name: str, score_to_add: int, host_name: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    
    # A sintaxe do PostgreSQL para parâmetros é %s em vez de ?
    cur.execute("SELECT * FROM ranking WHERE player_name = %s AND host_name = %s", (player_name, host_name))
    player = cur.fetchone()
    
    if player:
        new_score = player["total_score"] + score_to_add
        cur.execute("UPDATE ranking SET total_score = %s WHERE player_name = %s AND host_name = %s", (new_score, player_name, host_name))
    else:
        # ON CONFLICT ... DO NOTHING lida com a restrição UNIQUE de forma segura
        cur.execute("""
            INSERT INTO ranking (player_name, total_score, host_name) 
            VALUES (%s, %s, %s)
            ON CONFLICT (player_name, host_name) DO NOTHING
        """, (player_name, score_to_add, host_name))
        
    conn.commit()
    cur.close()
    conn.close()
    print(f"Ranking de '{host_name}': Pontuação de '{player_name}' atualizada.")

def get_ranking(host_name: str, limit: int = 10) -> List[Dict]:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT player_name, total_score FROM ranking WHERE host_name = %s ORDER BY total_score DESC LIMIT %s", (host_name, limit))
    ranking_data = cur.fetchall()
    cur.close()
    conn.close()
    return [{"name": row["player_name"], "score": row["total_score"]} for row in ranking_data]

def add_question(question_data: Dict, player_name: str) -> int:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(
        """
        INSERT INTO custom_questions 
        (question_text, correct_answer, incorrect_answer_1, incorrect_answer_2, incorrect_answer_3, difficulty, created_by) 
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """,
        (
            question_data["question_text"], question_data["correct_answer"],
            question_data["incorrect_answers"][0], question_data["incorrect_answers"][1],
            question_data["incorrect_answers"][2], question_data["difficulty"],
            player_name
        )
    )
    new_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return new_id

def get_questions_by_player(player_name: str) -> List[Dict]:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM custom_questions WHERE created_by = %s", (player_name,))
    questions_data = cur.fetchall()
    cur.close()
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
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(
        """
        UPDATE custom_questions SET 
        question_text = %s, correct_answer = %s, incorrect_answer_1 = %s, 
        incorrect_answer_2 = %s, incorrect_answer_3 = %s, difficulty = %s 
        WHERE id = %s AND created_by = %s
        """,
        (
            question_data["question_text"], question_data["correct_answer"],
            question_data["incorrect_answers"][0], question_data["incorrect_answers"][1],
            question_data["incorrect_answers"][2], question_data["difficulty"],
            question_id, player_name
        )
    )
    conn.commit()
    cur.close()
    conn.close()

def delete_question(question_id: int, player_name: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("DELETE FROM custom_questions WHERE id = %s AND created_by = %s", (question_id, player_name))
    conn.commit()
    cur.close()
    conn.close()