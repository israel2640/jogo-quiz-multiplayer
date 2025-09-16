import asyncio
import json
import random
import database
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    database.init_db()

class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, client_id: str):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        self.rooms[room_id][client_id] = websocket

    def disconnect(self, room_id: str, client_id: str):
        if room_id in self.rooms and client_id in self.rooms[room_id]:
            del self.rooms[room_id][client_id]
            if not self.rooms[room_id]:
                del self.rooms[room_id]

    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.rooms:
            connections = list(self.rooms[room_id].values())
            for connection in connections:
                await connection.send_text(json.dumps(message))

manager = ConnectionManager()

# --- Estado e Perguntas do Jogo ---
game_states: Dict[str, Dict[str, Any]] = {}
default_questions: List[Dict] = [
    # --- NÍVEL BÁSICO ---
    { "question": "Qual o nome da classe que representa o aluno e seus dados?", "options": ["AlunoService", "Aluno.java", "AlunoView", "AlunoRepository"], "correctAnswer": "Aluno.java", "difficulty": "Básico" },
    { "question": "Os atributos da classe Aluno, como 'nome' e 'cpf', são definidos como 'public' ou 'private'?", "options": ["public", "private", "protected", "static"], "correctAnswer": "private", "difficulty": "Básico" },
    { "question": "Qual classe é responsável por exibir o menu e interagir com o usuário no console?", "options": ["Main.java", "Aluno.java", "AlunoView.java", "Validador.java"], "correctAnswer": "AlunoView.java", "difficulty": "Básico" },
    { "question": "Na classe Main.java, qual objeto é usado para ler a entrada do usuário?", "options": ["System.in", "FileReader", "BufferedReader", "Scanner"], "correctAnswer": "Scanner", "difficulty": "Básico" },
    { "question": "Qual método é o ponto de entrada da aplicação, onde a execução começa?", "options": ["start()", "run()", "main()", "execute()"], "correctAnswer": "main()", "difficulty": "Básico" },
    { "question": "O que a interface 'AlunoRepository' define?", "options": ["A lógica de negócios", "A aparência da interface", "Um contrato para operações de dados", "As regras de validação"], "correctAnswer": "Um contrato para operações de dados", "difficulty": "Básico" },
    { "question": "Qual classe contém a lógica de negócios, como as regras para cadastrar um aluno?", "options": ["AlunoService.java", "AlunoRepository.java", "AlunoView.java", "Main.java"], "correctAnswer": "AlunoService.java", "difficulty": "Básico" },
    { "question": "Qual o valor inicial da variável 'opcao' no método 'mostrarMenu' da AlunoView?", "options": ["1", "0", "-1", "null"], "correctAnswer": "-1", "difficulty": "Básico" },
    { "question": "No menu principal da classe Main, qual número o usuário digita para escolher o armazenamento em Lista (ArrayList)?", "options": ["1", "0", "2", "3"], "correctAnswer": "2", "difficulty": "Básico" },
    { "question": "Qual o nome do método na classe Validador que verifica se um e-mail tem formato válido?", "options": ["isEmail", "validaEmail", "isEmailValido", "checkEmail"], "correctAnswer": "isEmailValido", "difficulty": "Básico" },

    # --- NÍVEL MÉDIO ---
    { "question": "Qual a principal diferença entre 'AlunoRepositoryLista' e 'AlunoRepositoryVetor'?", "options": ["Um usa List e o outro Set", "Um tem tamanho dinâmico e outro tamanho fixo", "Um ordena por nome e o outro por ID", "Não há diferença"], "correctAnswer": "Um tem tamanho dinâmico e outro tamanho fixo", "difficulty": "Médio" },
    { "question": "O que a anotação '@Override' indica antes de um método?", "options": ["Que o método é obsoleto", "Que o método está sobrescrevendo um da superclasse/interface", "Que o método é privado", "Que o método deve ser otimizado"], "correctAnswer": "Que o método está sobrescrevendo um da superclasse/interface", "difficulty": "Médio" },
    { "question": "Qual a finalidade de usar 'Optional<Aluno>' como tipo de retorno nos métodos de busca?", "options": ["Para retornar sempre uma lista de alunos", "Para indicar que um erro pode ocorrer", "Para representar um valor que pode ou não estar presente", "Para criar uma classe de alunos obrigatória"], "correctAnswer": "Para representar um valor que pode ou não estar presente", "difficulty": "Médio" },
    { "question": "Na classe AlunoService, qual verificação é feita para impedir o cadastro de matrículas duplicadas?", "options": ["Verifica o nome do aluno", "Usa o método 'buscarPorMatricula'", "Compara todos os CPFs", "Verifica o ID do aluno"], "correctAnswer": "Usa o método 'buscarPorMatricula'", "difficulty": "Médio" },
    { "question": "Como o método 'listarTodos' em AlunoRepositoryLista ordena os alunos antes de retorná-los?", "options": ["Pela matrícula", "Pelo ID", "Pelo nome", "Pela data de cadastro"], "correctAnswer": "Pelo nome", "difficulty": "Médio" },
    { "question": "Por que a linha 'scanner.nextLine();' é usada após 'scanner.nextInt()' na classe AlunoView?", "options": ["Para pular duas linhas", "Para limpar o buffer do scanner", "Para converter o número em texto", "Para aguardar o usuário pressionar Enter"], "correctAnswer": "Para limpar o buffer do scanner", "difficulty": "Médio" },
    { "question": "Que tipo de exceção o bloco 'try-catch' na classe Main.java é projetado para capturar?", "options": ["NullPointerException", "IOException", "NumberFormatException", "ArrayIndexOutOfBoundsException"], "correctAnswer": "NumberFormatException", "difficulty": "Médio" },
    { "question": "Por que os métodos da classe Validador, como 'isNumeric', são declarados como 'static'?", "options": ["Para economizar memória", "Porque são funções utilitárias que não dependem de um estado de objeto", "Para serem mais rápidos", "Porque a interface exige"], "correctAnswer": "Porque são funções utilitárias que não dependem de um estado de objeto", "difficulty": "Médio" },
    { "question": "No método 'atualizarAluno' do AlunoService, o que acontece se um ID de aluno não for encontrado?", "options": ["O programa trava", "Um novo aluno é criado", "Retorna uma mensagem de erro", "Atualiza o aluno mais próximo"], "correctAnswer": "Retorna uma mensagem de erro", "difficulty": "Médio" },
    { "question": "Qual a expressão regular (regex) usada para validar o formato do CPF na classe Validador?", "options": ["^\\d{11}$", "^\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}$", "^[0-9]{3}.[0-9]{3}.[0-9]{3}-[0-9]{2}$", "^[A-Z]{3}-\\d{4}$"], "correctAnswer": "^\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}$", "difficulty": "Médio" },

    # --- NÍVEL DIFÍCIL ---
    { "question": "No método 'remover' de AlunoRepositoryVetor, como o espaço vazio no array é tratado após a remoção?", "options": ["É preenchido com 'null'", "O tamanho do array é diminuído", "Os elementos seguintes são movidos para a esquerda", "O programa ignora o espaço vazio"], "correctAnswer": "Os elementos seguintes são movidos para a esquerda", "difficulty": "Difícil" },
    { "question": "Explique o funcionamento da linha 'alunos.removelf(aluno -> aluno.getId() == id);' em AlunoRepositoryLista.", "options": ["Usa uma expressão lambda para remover o aluno se o ID corresponder", "Usa um loop 'for' para encontrar e remover o aluno", "Cria uma nova lista sem o aluno com o ID correspondente", "Ordena a lista e depois remove o aluno pelo índice"], "correctAnswer": "Usa uma expressão lambda para remover o aluno se o ID corresponder", "difficulty": "Difícil" },
    { "question": "Qual a função do método 'ifPresent()' usado com um Optional no método 'atualizar' de AlunoRepositoryLista?", "options": ["Executa uma ação apenas se o Optional não estiver vazio", "Lança uma exceção se o Optional estiver vazio", "Retorna 'true' se o Optional estiver presente", "Converte o Optional para uma String"], "correctAnswer": "Executa uma ação apenas se o Optional não estiver vazio", "difficulty": "Difícil" },
    { "question": "Na classe Main, por que a variável 'alunoRepository' é usada na condição de um loop 'while'?", "options": ["Para contar o número de jogadores", "Para garantir que o usuário escolha uma opção de armazenamento válida antes de continuar", "Para limitar o tempo de escolha do usuário", "Para carregar os dados de um arquivo"], "correctAnswer": "Para garantir que o usuário escolha uma opção de armazenamento válida antes de continuar", "difficulty": "Difícil" },
    { "question": "Na classe AlunoService, ao atualizar um aluno, como o código impede que a nova matrícula seja igual à de um OUTRO aluno já existente?", "options": ["Ele não impede, permitindo matrículas duplicadas", "Ele busca pela nova matrícula e verifica se o ID do aluno encontrado é diferente do ID do aluno que está sendo atualizado", "Ele compara a nova matrícula com a matrícula antiga do mesmo aluno", "Ele deleta o aluno antigo e cria um novo com os dados atualizados"], "correctAnswer": "Ele busca pela nova matrícula e verifica se o ID do aluno encontrado é diferente do ID do aluno que está sendo atualizado", "difficulty": "Difícil" }
]
TIME_PER_QUESTION = 30
WINNING_SCORE = 100
PENALTY_POINTS = 5

# --- Funções Auxiliares do Jogo ---
def create_new_game_state(room_id: str):
    if room_id not in game_states:
        game_states[room_id] = {
            "players": {}, "scores": {}, "questions": list(default_questions),
            "custom_questions_pool": [], "current_question": None, "current_player_index": 0,
            "timer_task": None, "game_started": False
        }

async def start_game(room_id: str):
    state = game_states[room_id]
    if not state["game_started"] and len(state["players"]) >= 2:
        state["game_started"] = True
        await next_turn(room_id, new_game=True)

async def end_game_and_save_scores(room_id: str, winner: str):
    """Finaliza o jogo, salva os scores e avisa os jogadores."""
    state = game_states.get(room_id)
    if not state: return

    print(f"Fim de jogo na sala {room_id}. Salvando pontuações...")
    for player_id, score in state["scores"].items():
        if score > 0:
            database.update_player_score(player_id, score)

    await manager.broadcast(room_id, {"type": "gameOver", "winner": winner})
    if room_id in game_states:
        if game_states[room_id].get("timer_task"):
            game_states[room_id]["timer_task"].cancel()
        del game_states[room_id]

async def next_turn(room_id: str, new_game: bool = False):
    if room_id not in game_states: return
    state = game_states[room_id]
    
    if state["timer_task"]: state["timer_task"].cancel()

    for player_id, score in state["scores"].items():
        if score >= WINNING_SCORE:
            await end_game_and_save_scores(room_id, player_id)
            return

    if not new_game:
        state["current_player_index"] = (state["current_player_index"] + 1) % len(state["players"])
    
    if not state["questions"]:
        print(f"Sala {room_id}: Recarregando perguntas...")
        state["questions"] = list(default_questions) + list(state["custom_questions_pool"])
        
    state["current_question"] = state["questions"].pop(random.randrange(len(state["questions"])))
    state["timeRemaining"] = TIME_PER_QUESTION
    
    await manager.broadcast(room_id, {"type": "gameStateUpdate", "state": get_public_state(room_id)})
    
    state["timer_task"] = asyncio.create_task(timer(room_id))

async def timer(room_id: str):
    try:
        await asyncio.sleep(TIME_PER_QUESTION)
        if room_id in game_states:
            print(f"Sala {room_id}: Tempo esgotado! Próximo turno.")
            
            # <<< NOVA LÓGICA DE PENALIDADE POR TEMPO ESGOTADO >>>
            state = game_states[room_id]
            players_list = list(state["players"].keys())
            if players_list:
                current_player_id = players_list[state["current_player_index"]]
                # Garante que o placar não fique negativo
                state["scores"][current_player_id] = max(0, state["scores"][current_player_id] - PENALTY_POINTS)
            
            await next_turn(room_id)
    except asyncio.CancelledError:
        pass

def get_public_state(room_id: str):
    state = game_states.get(room_id, {})
    return {
        "players": state.get("players", {}), "scores": state.get("scores", {}),
        "current_question": state.get("current_question"), "current_player_index": state.get("current_player_index", 0),
        "timeRemaining": state.get("timeRemaining")
    }

@app.get("/ranking")
def get_ranking_data():
    """Endpoint HTTP para que o front-end possa buscar os dados do ranking."""
    return database.get_ranking()

@app.websocket("/ws/{room_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, client_id: str):
    await manager.connect(websocket, room_id, client_id)
    create_new_game_state(room_id)
    
    state = game_states[room_id]
    if client_id not in state["players"]:
        state["players"][client_id] = {"name": client_id}
        state["scores"][client_id] = 0

    print(f"Jogador {client_id} conectado à sala {room_id}. Jogadores totais: {len(state['players'])}")
    
    await start_game(room_id)
    await manager.broadcast(room_id, {"type": "gameStateUpdate", "state": get_public_state(room_id)})

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if room_id not in game_states: break
            state = game_states[room_id]
            
            if message["type"] == "addCustomQuestions":
                new_questions = message.get("questions", [])
                state["questions"].extend(new_questions)
                state["custom_questions_pool"].extend(new_questions)
                print(f"Adicionadas {len(new_questions)} perguntas customizadas à sala {room_id}")

            elif message["type"] == "submitAnswer":
                players_list = list(state["players"].keys())
                if not players_list: continue
                current_player_id = players_list[state["current_player_index"]]
                
                if client_id == current_player_id:
                    if message["answer"] == state["current_question"]["correctAnswer"]:
                        state["scores"][client_id] += 10
                    else:
                        # <<< NOVA LÓGICA DE PENALIDADE POR RESPOSTA ERRADA >>>
                        # Garante que o placar não fique negativo
                        state["scores"][client_id] = max(0, state["scores"][client_id] - PENALTY_POINTS)
                    
                    await next_turn(room_id)
                    
    except WebSocketDisconnect:
        print(f"Jogador {client_id} desconectado da sala {room_id}.")
        manager.disconnect(room_id, client_id)
        if room_id in game_states:
            state = game_states[room_id]
            if client_id in state["players"]: del state["players"][client_id]
            if client_id in state["scores"]: del state["scores"][client_id]

            if len(state["players"]) < 2 and state["game_started"]:
                 await end_game_and_save_scores(room_id, "Jogo encerrado por falta de jogadores")
            else:
                if state["players"]: state["current_player_index"] %= len(state["players"])
                await manager.broadcast(room_id, {"type": "gameStateUpdate", "state": get_public_state(room_id)})