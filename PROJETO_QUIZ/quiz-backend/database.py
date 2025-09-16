# database.py
import sqlite3

DATABASE_FILE = "ranking.db"

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Cria a tabela de ranking se ela não existir."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL UNIQUE,
            total_score INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    print("Banco de dados 'ranking.db' inicializado com sucesso.")

def update_player_score(player_name: str, score_to_add: int):
    """Adiciona pontos a um jogador ou cria um novo se ele não existir."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verifica se o jogador já existe
    cursor.execute("SELECT * FROM ranking WHERE player_name = ?", (player_name,))
    player = cursor.fetchone()
    
    if player:
        # Se existe, atualiza a pontuação
        new_score = player["total_score"] + score_to_add
        cursor.execute(
            "UPDATE ranking SET total_score = ? WHERE player_name = ?",
            (new_score, player_name)
        )
    else:
        # Se não existe, insere um novo registro
        cursor.execute(
            "INSERT INTO ranking (player_name, total_score) VALUES (?, ?)",
            (player_name, score_to_add)
        )
        
    conn.commit()
    conn.close()
    print(f"Pontuação de '{player_name}' atualizada com {score_to_add} pontos.")

def get_ranking(limit: int = 10):
    """Retorna os top 10 jogadores do ranking."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT player_name, total_score FROM ranking ORDER BY total_score DESC LIMIT ?",
        (limit,)
    )
    ranking = cursor.fetchall()
    conn.close()
    # Converte o resultado para uma lista de dicionários
    return [{"name": row["player_name"], "score": row["total_score"]} for row in ranking]