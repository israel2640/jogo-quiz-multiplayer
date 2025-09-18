# main.py (Versão com correção do erro 404)
import asyncio
import json
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any
import database

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

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

class Question(BaseModel):
    question_text: str
    correct_answer: str
    incorrect_answers: List[str]
    difficulty: str

@app.get("/questions/{player_name}", response_model=List[Dict])
def get_player_questions(player_name: str):
    return database.get_questions_by_player(player_name)
@app.post("/questions/{player_name}", status_code=201)
def create_question_for_player(player_name: str, question: Question):
    if len(question.incorrect_answers) != 3: raise HTTPException(status_code=400, detail="É necessário fornecer 3 respostas incorretas.")
    new_id = database.add_question(question.dict(), player_name)
    return {"message": "Pergunta criada com sucesso", "id": new_id}
@app.put("/questions/{question_id}/{player_name}")
def update_player_question(question_id: int, player_name: str, question: Question):
    if len(question.incorrect_answers) != 3: raise HTTPException(status_code=400, detail="É necessário fornecer 3 respostas incorretas.")
    database.update_question(question_id, question.dict(), player_name)
    return {"message": f"Pergunta {question_id} atualizada com sucesso"}
@app.delete("/questions/{question_id}/{player_name}")
def delete_player_question(question_id: int, player_name: str):
    database.delete_question(question_id, player_name)
    return {"message": f"Pergunta {question_id} deletada com sucesso"}

@app.get("/ranking/{host_name}")
def get_ranking_data(host_name: str):
    return database.get_ranking(host_name)

class ConnectionManager:
    def __init__(self): self.rooms: Dict[str, Dict[str, WebSocket]] = {}
    async def connect(self, websocket: WebSocket, room_id: str, client_id: str):
        await websocket.accept()
        if room_id not in self.rooms: self.rooms[room_id] = {}
        self.rooms[room_id][client_id] = websocket
    def disconnect(self, room_id: str, client_id: str):
        if room_id in self.rooms and client_id in self.rooms[room_id]:
            del self.rooms[room_id][client_id]
            if not self.rooms[room_id]: del self.rooms[room_id]
    async def broadcast(self, room_id: str, message: dict):
        state = game_states.get(room_id)
        if state and room_id in self.rooms:
            connections = list(self.rooms[room_id].values())
            for connection in connections: await connection.send_text(json.dumps(message))

manager = ConnectionManager()
game_states: Dict[str, Dict[str, Any]] = {}
# Em main.py, substitua a sua lista 'default_questions' por esta:
default_questions = [
    # =================================================================
    # == NÍVEL FÁCIL (30 PERGUNTAS) ==
    # =================================================================
    {
        "question": "Qual é o nome da classe que representa o modelo de um aluno?",
        "options": ["Aluno.java", "AlunoService.java", "AlunoView.java", "AlunoModel.java"],
        "correctAnswer": "Aluno.java",
        "difficulty": "Fácil"
    },
    {
        "question": "Para que serve a anotação @Override?",
        "options": ["Indica que um método está sendo sobrescrito", "Indica um método obsoleto", "Inicia um novo método", "Importa uma biblioteca"],
        "correctAnswer": "Indica que um método está sendo sobrescrito",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual classe é responsável pela interface e interação com o usuário no console?",
        "options": ["AlunoView", "AlunoService", "Main", "AlunoRepository"],
        "correctAnswer": "AlunoView",
        "difficulty": "Fácil"
    },
    {
        "question": "No menu principal em AlunoView, qual número o usuário deve digitar para sair do sistema?",
        "options": ["0", "1", "9", "-1"],
        "correctAnswer": "0",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual classe Java é importada em AlunoView para ler a entrada do usuário?",
        "options": ["java.util.Scanner", "java.io.Reader", "java.util.Input", "java.console.Reader"],
        "correctAnswer": "java.util.Scanner",
        "difficulty": "Fácil"
    },
    {
        "question": "O que faz um método 'getter'?",
        "options": ["Acessar os valores dos atributos privados", "Modificar os valores dos atributos privados", "Deletar um objeto", "Criar um novo objeto"],
        "correctAnswer": "Acessar os valores dos atributos privados",
        "difficulty": "Fácil"
    },
    {
        "question": "O que faz um método 'setter'?",
        "options": ["Modificar os valores dos atributos privados", "Acessar os valores dos atributos privados", "Retornar o nome da classe", "Verificar se um objeto é nulo"],
        "correctAnswer": "Modificar os valores dos atributos privados",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual o nome da interface que define o contrato para as operações de persistência de dados do aluno?",
        "options": ["AlunoRepository", "AlunoPersistence", "AlunoContract", "AlunoData"],
        "correctAnswer": "AlunoRepository",
        "difficulty": "Fácil"
    },
    {
        "question": "Na classe Aluno, por que os atributos são declarados como 'private'?",
        "options": ["Para não poderem ser acessados diretamente de fora da classe", "Para economizar memória", "Para serem mais rápidos", "Para serem acessíveis a todos os pacotes"],
        "correctAnswer": "Para não poderem ser acessados diretamente de fora da classe",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual o nome da classe que contém o ponto de entrada da aplicação (método main)?",
        "options": ["Main", "App", "Start", "Program"],
        "correctAnswer": "Main",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual o nome da classe utilitária que contém métodos de validação?",
        "options": ["Validador", "Validator", "Utils", "Helper"],
        "correctAnswer": "Validador",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual classe implementa AlunoRepository usando um ArrayList?",
        "options": ["AlunoRepositoryLista", "AlunoRepositoryArray", "AlunoRepositoryList", "AlunoRepositoryArrayList"],
        "correctAnswer": "AlunoRepositoryLista",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual classe implementa AlunoRepository usando um vetor (array)?",
        "options": ["AlunoRepositoryVetor", "AlunoRepositoryArray", "AlunoRepositoryVector", "AlunoRepositoryFixed"],
        "correctAnswer": "AlunoRepositoryVetor",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual é o tamanho máximo de alunos que AlunoRepositoryVetor pode armazenar?",
        "options": ["100", "50", "1000", "Ilimitado"],
        "correctAnswer": "100",
        "difficulty": "Fácil"
    },
    {
        "question": "No Validador, qual método verifica se uma string é nula ou vazia?",
        "options": ["isNullOrEmpty", "checkEmpty", "validateString", "isEmpty"],
        "correctAnswer": "isNullOrEmpty",
        "difficulty": "Fácil"
    },
    {
        "question": "O que o método toString() na classe Aluno retorna?",
        "options": ["Uma string formatada com todos os atributos do aluno", "O ID do aluno", "O nome da classe", "Um valor nulo"],
        "correctAnswer": "Uma string formatada com todos os atributos do aluno",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual método da AlunoView é responsável por exibir o menu de opções?",
        "options": ["mostrarMenu()", "displayMenu()", "printMenu()", "viewMenu()"],
        "correctAnswer": "mostrarMenu()",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual classe contém a lógica de negócios e as validações para as operações de alunos?",
        "options": ["AlunoService", "AlunoController", "AlunoBusiness", "AlunoLogic"],
        "correctAnswer": "AlunoService",
        "difficulty": "Fácil"
    },
    {
        "question": "No menu principal, qual opção permite ao usuário cadastrar um novo aluno?",
        "options": ["1", "2", "C", "A"],
        "correctAnswer": "1",
        "difficulty": "Fácil"
    },
    {
        "question": "Para que serve a variável 'proximoId' na classe AlunoRepositoryLista?",
        "options": ["Para rastrear o próximo ID a ser atribuído a um novo aluno", "Para contar o total de alunos", "Para definir o limite de alunos", "Para armazenar o último ID usado"],
        "correctAnswer": "Para rastrear o próximo ID a ser atribuído a um novo aluno",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual método na classe Validador é usado para verificar se uma string contém apenas números?",
        "options": ["isNumeric", "isNumber", "onlyDigits", "hasNumbers"],
        "correctAnswer": "isNumeric",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual o nome do pacote da classe Aluno?",
        "options": ["br.com.escola.projeto.models", "br.com.escola.projeto.services", "br.com.escola.projeto.views", "br.com.escola.projeto.repositories"],
        "correctAnswer": "br.com.escola.projeto.models",
        "difficulty": "Fácil"
    },
    {
        "question": "O que o método 'salvar' da interface AlunoRepository recebe como parâmetro?",
        "options": ["Um objeto do tipo Aluno", "Um número de ID", "Uma string com o nome", "Uma lista de Alunos"],
        "correctAnswer": "Um objeto do tipo Aluno",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual o tipo de retorno do método 'remover' na interface AlunoRepository?",
        "options": ["boolean", "void", "int", "String"],
        "correctAnswer": "boolean",
        "difficulty": "Fácil"
    },
    {
        "question": "O que a palavra-chave 'this' refere-se dentro de um construtor?",
        "options": ["Ao objeto atual da classe", "À classe pai", "A uma variável estática", "Ao pacote atual"],
        "correctAnswer": "Ao objeto atual da classe",
        "difficulty": "Fácil"
    },
    {
        "question": "O que a classe 'Optional' representa?",
        "options": ["Um contêiner que pode ou não conter um valor", "Uma lista de opções para o usuário", "Um tipo de dado opcional", "Uma classe de validação"],
        "correctAnswer": "Um contêiner que pode ou não conter um valor",
        "difficulty": "Fácil"
    },
    {
        "question": "No menu de AlunoView, qual opção busca um aluno pela matrícula?",
        "options": ["4", "3", "5", "6"],
        "correctAnswer": "4",
        "difficulty": "Fácil"
    },
    {
        "question": "Que tipo de exceção é capturada no método 'main' se o usuário digitar um texto em vez de um número?",
        "options": ["NumberFormatException", "IllegalArgumentException", "IOException", "NullPointerException"],
        "correctAnswer": "NumberFormatException",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual método é chamado no objeto 'alunoView' dentro do 'main' para iniciar a interação com o usuário?",
        "options": ["mostrarMenu()", "start()", "run()", "init()"],
        "correctAnswer": "mostrarMenu()",
        "difficulty": "Fácil"
    },
    {
        "question": "O que o método 'scanner.close()' faz?",
        "options": ["Fecha o scanner, liberando os recursos associados a ele", "Limpa o buffer do scanner", "Reinicia o scanner", "Pausa a leitura do scanner"],
        "correctAnswer": "Fecha o scanner, liberando os recursos associados a ele",
        "difficulty": "Fácil"
    },
    # =================================================================
    # == NÍVEL MÉDIO (30 PERGUNTAS) ==
    # =================================================================
    {
        "question": "Por que os métodos na classe Validador são declarados como 'static'?",
        "options": ["Para serem chamados diretamente pela classe, sem precisar criar um objeto", "Para economizar memória", "Para serem compartilhados entre threads", "Para não poderem ser sobrescritos"],
        "correctAnswer": "Para serem chamados diretamente pela classe, sem precisar criar um objeto",
        "difficulty": "Médio"
    },
    {
        "question": "Qual a finalidade de usar Optional<Aluno> como tipo de retorno em métodos de busca?",
        "options": ["Para representar um valor que pode ou não estar presente, evitando NullPointerException", "Para retornar uma lista de alunos opcionais", "Para otimizar a busca no banco de dados", "Para obrigar o uso de um bloco try-catch"],
        "correctAnswer": "Para representar um valor que pode ou não estar presente, evitando NullPointerException",
        "difficulty": "Médio"
    },
    {
        "question": "Na classe Main, como o programa decide qual implementação de AlunoRepository utilizar?",
        "options": ["Através de um menu de escolha para o usuário no console", "É definido aleatoriamente na execução", "Usa sempre a implementação 'Lista' por padrão", "Verifica qual arquivo de configuração existe"],
        "correctAnswer": "Através de um menu de escolha para o usuário no console",
        "difficulty": "Médio"
    },
    {
        "question": "Explique o que a linha 'scanner.nextLine();' faz logo após 'scanner.nextInt();' em AlunoView.",
        "options": ["Limpa o buffer do scanner, consumindo o caractere de nova linha", "Lê a próxima linha de texto digitada pelo usuário", "Pula para a próxima opção do menu", "Causa uma pausa de 1 segundo no programa"],
        "correctAnswer": "Limpa o buffer do scanner, consumindo o caractere de nova linha",
        "difficulty": "Médio"
    },
    {
        "question": "Como o método 'salvar' da AlunoRepositoryLista garante que cada aluno tenha um ID único?",
        "options": ["Usa uma variável 'proximoId' que é incrementada a cada novo aluno", "Gera um número aleatório para o ID", "Verifica o último ID na lista e soma 1", "Pede para o usuário digitar um ID único"],
        "correctAnswer": "Usa uma variável 'proximoId' que é incrementada a cada novo aluno",
        "difficulty": "Médio"
    },
    {
        "question": "No método listarTodos de AlunoRepositoryLista, em que ordem os alunos são retornados?",
        "options": ["Ordenados pelo nome", "Na ordem em que foram inseridos", "Ordenados pelo ID", "Em ordem aleatória"],
        "correctAnswer": "Ordenados pelo nome",
        "difficulty": "Médio"
    },
    {
        "question": "No AlunoRepositoryVetor, o que acontece se o método 'salvar' for chamado quando o vetor já estiver cheio?",
        "options": ["Imprime uma mensagem de erro e não salva o aluno", "Aumenta o tamanho do vetor dinamicamente", "Substitui o aluno mais antigo", "Lança uma exceção do tipo 'ArrayIndexOutOfBoundsException'"],
        "correctAnswer": "Imprime uma mensagem de erro e não salva o aluno",
        "difficulty": "Médio"
    },
    {
        "question": "Qual tecnologia é usada na classe Validador para verificar os formatos de CPF e e-mail?",
        "options": ["Expressões Regulares (Regex)", "Inteligência Artificial", "Algoritmos de Hash", "Comparações de String simples"],
        "correctAnswer": "Expressões Regulares (Regex)",
        "difficulty": "Médio"
    },
    {
        "question": "O que a expressão 'alunos.stream()' faz nas implementações de AlunoRepository?",
        "options": ["Converte a coleção de alunos em um fluxo de dados para operações declarativas", "Transmite os dados dos alunos pela rede", "Cria um arquivo de log com os dados dos alunos", "Compacta a lista de alunos para economizar espaço"],
        "correctAnswer": "Converte a coleção de alunos em um fluxo de dados para operações declarativas",
        "difficulty": "Médio"
    },
    {
        "question": "Como o método 'remover' da classe AlunoRepositoryLista funciona?",
        "options": ["Usa o método 'removeIf' para remover o aluno com o ID correspondente", "Percorre a lista com um laço 'for' e remove pelo índice", "Cria uma nova lista sem o aluno a ser removido", "Marca o aluno como 'removido' sem tirá-lo da lista"],
        "correctAnswer": "Usa o método 'removeIf' para remover o aluno com o ID correspondente",
        "difficulty": "Médio"
    },
    {
        "question": "No método cadastrarAluno do AlunoService, qual verificação é feita imediatamente após validar os campos?",
        "options": ["Verifica se já existe um aluno com a mesma matrícula", "Verifica se o nome do aluno é único", "Verifica a idade do aluno", "Salva o aluno no repositório"],
        "correctAnswer": "Verifica se já existe um aluno com a mesma matrícula",
        "difficulty": "Médio"
    },
    {
        "question": "Qual o propósito do bloco 'switch' dentro do método mostrarMenu da AlunoView?",
        "options": ["Executar a ação correspondente à opção escolhida pelo usuário", "Validar a entrada do usuário", "Trocar o repositório de dados em tempo de execução", "Mudar a cor do texto no console"],
        "correctAnswer": "Executar a ação correspondente à opção escolhida pelo usuário",
        "difficulty": "Médio"
    },
    {
        "question": "Qual a diferença na forma como 'buscarPorId' é implementado em AlunoRepositoryLista e AlunoRepositoryVetor?",
        "options": ["'Lista' usa a API de Streams, enquanto 'Vetor' usa um laço 'for' tradicional", "'Lista' é mais rápido para poucos dados, 'Vetor' é mais rápido para muitos", "Ambos usam a mesma implementação com laço 'for'", "'Lista' usa busca binária e 'Vetor' usa busca linear"],
        "correctAnswer": "'Lista' usa a API de Streams, enquanto 'Vetor' usa um laço 'for' tradicional",
        "difficulty": "Médio"
    },
    {
        "question": "No método removerAluno de AlunoService, como ele informa à AlunoView se a operação foi bem-sucedida?",
        "options": ["Retornando uma string com a mensagem de sucesso ou erro", "Retornando um valor booleano 'true' ou 'false'", "Lançando uma exceção em caso de erro", "Imprimindo o resultado diretamente no console"],
        "correctAnswer": "Retornando uma string com a mensagem de sucesso ou erro",
        "difficulty": "Médio"
    },
    {
        "question": "Qual é o papel da classe ArrayList importada em AlunoRepositoryLista?",
        "options": ["É uma implementação de List que armazena objetos de forma dinâmica", "É uma classe para ordenar arrays", "É uma classe para converter listas em vetores", "É uma classe de utilitários para listas"],
        "correctAnswer": "É uma implementação de List que armazena objetos de forma dinâmica",
        "difficulty": "Médio"
    },
    {
        "question": "O que a expressão 'Comparator.comparing(Aluno::getNome)' faz?",
        "options": ["Cria um comparador que ordena objetos Aluno com base no seu nome", "Compara se dois alunos têm o mesmo nome", "Converte o nome do aluno para letras maiúsculas", "Remove alunos com nomes duplicados"],
        "correctAnswer": "Cria um comparador que ordena objetos Aluno com base no seu nome",
        "difficulty": "Médio"
    },
    {
        "question": "Como o método listarTodos em AlunoRepositoryVetor lida com as posições vazias (nulas) do array?",
        "options": ["Converte para stream apenas a porção preenchida do vetor (de 0 a totalAlunos)", "Percorre o vetor inteiro e ignora os elementos nulos", "Lança uma NullPointerException se encontrar um valor nulo", "Preenche as posições nulas com objetos Aluno vazios"],
        "correctAnswer": "Converte para stream apenas a porção preenchida do vetor (de 0 a totalAlunos)",
        "difficulty": "Médio"
    },
    {
        "question": "O que o método 'valor.trim().isEmpty()' na classe Validador faz?",
        "options": ["Remove espaços em branco no início e fim da string e verifica se ela está vazia", "Verifica se a string contém apenas espaços em branco", "Corta a string pela metade e verifica se a primeira parte está vazia", "Remove todos os espaços da string e verifica se ela está vazia"],
        "correctAnswer": "Remove espaços em branco no início e fim da string e verifica se ela está vazia",
        "difficulty": "Médio"
    },
    {
        "question": "Por que a classe AlunoService recebe um AlunoRepository em seu construtor?",
        "options": ["Para desacoplar a lógica de negócios da implementação de persistência de dados", "Para garantir que apenas um repositório seja usado em toda a aplicação", "Para criar uma nova tabela no banco de dados", "Para inicializar a lista de alunos com dados de teste"],
        "correctAnswer": "Para desacoplar a lógica de negócios da implementação de persistência de dados",
        "difficulty": "Médio"
    },
    {
        "question": "No método 'buscarPorMatricula' de AlunoRepositoryLista, o que 'equalsIgnoreCase' faz?",
        "options": ["Compara duas strings ignorando se as letras são maiúsculas ou minúsculas", "Compara se duas strings são exatamente iguais", "Verifica se a matrícula tem um formato válido", "Converte a matrícula para letras minúsculas"],
        "correctAnswer": "Compara duas strings ignorando se as letras são maiúsculas ou minúsculas",
        "difficulty": "Médio"
    },
    {
        "question": "Qual a primeira validação feita no método 'cadastrarAluno' da AlunoService?",
        "options": ["Verifica se algum dos campos obrigatórios é nulo ou vazio", "Verifica se a matrícula contém apenas números", "Verifica se o formato do CPF é válido", "Verifica se a matrícula já existe"],
        "correctAnswer": "Verifica se algum dos campos obrigatórios é nulo ou vazio",
        "difficulty": "Médio"
    },
    {
        "question": "O que o método 'Integer.parseInt(scanner.nextLine())' na classe Main tenta fazer?",
        "options": ["Lê uma linha de texto do usuário e a converte para um número inteiro", "Converte um número para texto", "Verifica se o usuário digitou um número", "Formata um número com separador de milhares"],
        "correctAnswer": "Lê uma linha de texto do usuário e a converte para um número inteiro",
        "difficulty": "Médio"
    },
    {
        "question": "Qual a função do 'return Optional.empty()'?",
        "options": ["Retornar um Optional vazio para indicar que nenhum valor foi encontrado", "Retornar um erro de 'valor não encontrado'", "Retornar uma string vazia", "Retornar o valor nulo (null)"],
        "correctAnswer": "Retornar um Optional vazio para indicar que nenhum valor foi encontrado",
        "difficulty": "Médio"
    },
    {
        "question": "O que a expressão 'Collectors.toList()' faz?",
        "options": ["Coleta os elementos de um stream em uma nova lista", "Converte um vetor em uma lista", "Filtra os elementos de uma lista", "Imprime os elementos de uma lista no console"],
        "correctAnswer": "Coleta os elementos de um stream em uma nova lista",
        "difficulty": "Médio"
    },
    {
        "question": "No método 'atualizar' de AlunoRepositoryLista, o que 'ifPresent' faz?",
        "options": ["Executa um bloco de código apenas se o Optional retornado pela busca contiver um valor", "Verifica se o aluno está presente na sala de aula", "Apresenta os dados do aluno na tela", "Define a presença do aluno como verdadeira"],
        "correctAnswer": "Executa um bloco de código apenas se o Optional retornado pela busca contiver um valor",
        "difficulty": "Médio"
    },
    {
        "question": "Por que o método 'remover' de AlunoRepositoryVetor precisa de um segundo laço 'for'?",
        "options": ["Para mover todos os elementos seguintes uma posição para a esquerda, preenchendo o espaço vazio", "Para verificar se o aluno foi realmente removido", "Para encontrar o índice do aluno a ser removido", "Para ordenar o vetor após a remoção"],
        "correctAnswer": "Para mover todos os elementos seguintes uma posição para a esquerda, preenchendo o espaço vazio",
        "difficulty": "Médio"
    },
    {
        "question": "No método 'atualizarAluno' da AlunoService, qual a primeira coisa que ele faz após validar os novos dados?",
        "options": ["Busca o aluno pelo ID para verificar se ele existe", "Salva as alterações no repositório", "Cria um novo objeto Aluno com os dados atualizados", "Verifica se a nova matrícula já está em uso"],
        "correctAnswer": "Busca o aluno pelo ID para verificar se ele existe",
        "difficulty": "Médio"
    },
    {
        "question": "O que significa 'implements AlunoRepository' na declaração de uma classe?",
        "options": ["Que a classe se compromete a fornecer uma implementação para todos os métodos da interface AlunoRepository", "Que a classe herda todos os atributos da AlunoRepository", "Que a classe é uma instância de AlunoRepository", "Que a classe importa a AlunoRepository"],
        "correctAnswer": "Que a classe se compromete a fornecer uma implementação para todos os métodos da interface AlunoRepository",
        "difficulty": "Médio"
    },
    {
        "question": "Qual o propósito da variável 'totalAlunos' em AlunoRepositoryVetor?",
        "options": ["Contabilizar a quantidade de alunos realmente armazenados no vetor", "Definir o tamanho máximo do vetor", "Armazenar o próximo ID a ser usado", "Calcular a média de notas dos alunos"],
        "correctAnswer": "Contabilizar a quantidade de alunos realmente armazenados no vetor",
        "difficulty": "Médio"
    },
    {
        "question": "O que a expressão 'a -> a.getId() == id' é chamada em Java?",
        "options": ["Uma expressão lambda", "Uma função anônima", "Um método aninhado", "Uma declaração de variável"],
        "correctAnswer": "Uma expressão lambda",
        "difficulty": "Médio"
    },
    # =================================================================
    # == NÍVEL DIFÍCIL (30 PERGUNTAS) ==
    # =================================================================
    {
        "question": "Na AlunoService, por que o método 'atualizarAluno' verifica se a nova matrícula já está em uso por *outro* aluno (usando `alunoComMesmaMatricula.get().getId() != id`)?",
        "options": ["Para permitir que o aluno mantenha sua própria matrícula ao atualizar outros dados", "Para impedir que a matrícula de um aluno seja atribuída a outro", "Para forçar que toda atualização de aluno exija uma nova matrícula", "É uma verificação redundante sem efeito prático"],
        "correctAnswer": "Para permitir que o aluno mantenha sua própria matrícula ao atualizar outros dados",
        "difficulty": "Difícil"
    },
    {
        "question": "No método 'remover' de AlunoRepositoryVetor, qual é o propósito da linha 'alunos[totalAlunos - 1] = null;'?",
        "options": ["Para liberar a referência ao objeto duplicado no final do vetor e permitir que ele seja coletado pelo Garbage Collector", "Para marcar o final do vetor com um valor nulo", "Para evitar um 'ArrayIndexOutOfBoundsException' na próxima inserção", "Para limpar o último elemento do vetor antes de redimensioná-lo"],
        "correctAnswer": "Para liberar a referência ao objeto duplicado no final do vetor e permitir que ele seja coletado pelo Garbage Collector",
        "difficulty": "Difícil"
    },
    {
        "question": "Se a classe AlunoService não recebesse AlunoRepository via injeção de dependência no construtor, que princípio de design de software seria violado?",
        "options": ["Inversão de Dependência (SOLID)", "Responsabilidade Única (SOLID)", "Aberto/Fechado (SOLID)", "Segregação de Interface (SOLID)"],
        "correctAnswer": "Inversão de Dependência (SOLID)",
        "difficulty": "Difícil"
    },
    {
        "question": "Qual a principal desvantagem da implementação AlunoRepositoryVetor em comparação com AlunoRepositoryLista?",
        "options": ["Possui um tamanho fixo e não pode crescer dinamicamente, desperdiçando memória ou limitando o número de alunos", "A operação de busca por ID é significativamente mais lenta", "A complexidade para adicionar um novo elemento é maior", "Não é possível ordenar os alunos por nome"],
        "correctAnswer": "Possui um tamanho fixo e não pode crescer dinamicamente, desperdiçando memória ou limitando o número de alunos",
        "difficulty": "Difícil"
    },
    {
        "question": "No método 'atualizar' de AlunoRepositoryLista, o que aconteceria se o aluno com o ID fornecido não existisse na lista?",
        "options": ["Absolutamente nada, pois o código dentro do '.ifPresent()' não seria executado", "Lançaria uma 'NullPointerException'", "O programa entraria em um loop infinito", "Um novo aluno seria adicionado à lista"],
        "correctAnswer": "Absolutamente nada, pois o código dentro do '.ifPresent()' não seria executado",
        "difficulty": "Difícil"
    },
    {
        "question": "A expressão 'Aluno::getNome' é conhecida como:",
        "options": ["Method Reference", "Lambda Expression", "Anonymous Function", "Getter Invocation"],
        "correctAnswer": "Method Reference",
        "difficulty": "Difícil"
    },
    {
        "question": "Se você removesse a linha 'scanner.nextLine()' após 'scanner.nextInt()' em AlunoView, qual seria o comportamento anômalo?",
        "options": ["Na próxima leitura de uma String (ex: nome do aluno), o programa leria uma linha vazia e pularia a entrada do usuário", "O programa lançaria uma 'InputMismatchException'", "O menu seria exibido duas vezes seguidas", "O programa ficaria travado esperando por uma nova entrada"],
        "correctAnswer": "Na próxima leitura de uma String (ex: nome do aluno), o programa leria uma linha vazia e pularia a entrada do usuário",
        "difficulty": "Difícil"
    },
    {
        "question": "Qual a complexidade de tempo (Big O) da operação 'remover' na implementação AlunoRepositoryVetor?",
        "options": ["O(n), porque no pior caso é preciso percorrer o vetor para encontrar o elemento e depois deslocar os restantes", "O(1), porque a remoção é instantânea", "O(log n), porque utiliza busca binária para encontrar o elemento", "O(n²), porque utiliza dois laços aninhados para a remoção"],
        "correctAnswer": "O(n), porque no pior caso é preciso percorrer o vetor para encontrar o elemento e depois deslocar os restantes",
        "difficulty": "Difícil"
    },
    {
        "question": "Qual a complexidade de tempo (Big O) da operação 'buscarPorId' na implementação AlunoRepositoryLista?",
        "options": ["O(n), porque o stream precisa percorrer os elementos para encontrar o correspondente", "O(1), porque o acesso pelo ID é direto", "O(log n), porque a lista está sempre ordenada", "O(n log n), por causa da complexidade do stream"],
        "correctAnswer": "O(n), porque o stream precisa percorrer os elementos para encontrar o correspondente",
        "difficulty": "Difícil"
    },
    {
        "question": "Por que a validação de formato de CPF e e-mail é feita na AlunoService e não na classe Aluno?",
        "options": ["Para manter a classe Aluno como um simples objeto de dados (POJO) e centralizar a lógica de negócios na camada de serviço", "Porque a classe Aluno não pode ter métodos com lógica complexa", "Para permitir que a validação seja alterada sem recompilar a classe Aluno", "Porque a classe Validador só pode ser acessada pela AlunoService"],
        "correctAnswer": "Para manter a classe Aluno como um simples objeto de dados (POJO) e centralizar a lógica de negócios na camada de serviço",
        "difficulty": "Difícil"
    },
    {
        "question": "O que o método 'findFirst()' da API de Streams faz?",
        "options": ["Retorna um Optional descrevendo o primeiro elemento do stream, ou um Optional vazio se o stream estiver vazio", "Encontra o primeiro elemento que corresponde ao filtro e o retorna diretamente", "Retorna o primeiro elemento do stream, lançando uma exceção se o stream estiver vazio", "Verifica se o primeiro elemento é válido"],
        "correctAnswer": "Retorna um Optional descrevendo o primeiro elemento do stream, ou um Optional vazio se o stream estiver vazio",
        "difficulty": "Difícil"
    },
    {
        "question": "Na classe Main, por que a variável 'alunoRepository' é declarada como o tipo da interface e não da classe concreta?",
        "options": ["Para programar para uma interface, permitindo que a implementação concreta (Vetor ou Lista) seja decidida em tempo de execução", "Porque interfaces consomem menos memória que classes", "É uma convenção de estilo do Java sem impacto funcional", "Para impedir que métodos específicos da classe concreta sejam chamados"],
        "correctAnswer": "Para programar para uma interface, permitindo que a implementação concreta (Vetor ou Lista) seja decidida em tempo de execução",
        "difficulty": "Difícil"
    },
    {
        "question": "Se o método 'remover' em AlunoRepositoryVetor não decrementasse 'totalAlunos', qual seria a consequência?",
        "options": ["A posição do último aluno conteria uma referência nula, causando NullPointerException em operações futuras como 'listarTodos'", "O aluno removido ainda seria considerado no total, ocupando espaço desnecessariamente", "A remoção falharia silenciosamente", "O programa lançaria uma exceção de consistência de dados"],
        "correctAnswer": "A posição do último aluno conteria uma referência nula, causando NullPointerException em operações futuras como 'listarTodos'",
        "difficulty": "Difícil"
    },
    {
        "question": "Qual seria uma desvantagem de usar 'System.out.println' para mensagens de erro dentro de AlunoRepositoryVetor, como é feito?",
        "options": ["Acola a camada de repositório à saída do console, dificultando a reutilização em uma aplicação web ou móvel", "Mensagens de erro no console são ineficientes e lentas", "Isso impede que o erro seja tratado pela camada de serviço", "O console só pode exibir um número limitado de mensagens de erro"],
        "correctAnswer": "Acola a camada de repositório à saída do console, dificultando a reutilização em uma aplicação web ou móvel",
        "difficulty": "Difícil"
    },
    {
        "question": "O que aconteceria se a classe Aluno não sobrescrevesse o método 'toString()'?",
        "options": ["A impressão de um objeto Aluno exibiria o nome da classe seguido de um código hash (ex: Aluno@1f32e575)", "O compilador Java apresentaria um erro", "Seria impossível obter os dados de um objeto Aluno", "O método 'listarAlunos' da AlunoView lançaria uma exceção"],
        "correctAnswer": "A impressão de um objeto Aluno exibiria o nome da classe seguido de um código hash (ex: Aluno@1f32e575)",
        "difficulty": "Difícil"
    },
    {
        "question": "Qual padrão de projeto está sendo implicitamente utilizado pela combinação da interface AlunoRepository e suas duas implementações?",
        "options": ["Strategy", "Singleton", "Factory", "Observer"],
        "correctAnswer": "Strategy",
        "difficulty": "Difícil"
    },
    {
        "question": "No método 'atualizar' de AlunoRepositoryLista, por que é necessário buscar o 'alunoExistente' para depois obter seu índice?",
        "options": ["Para garantir que o objeto na lista seja o mesmo antes de usar 'indexOf', pois a busca por ID é a fonte de verdade", "Porque o método 'indexOf' só funciona com o objeto exato que está na lista", "É uma forma de validar se o aluno existe antes de tentar obter o índice", "Para obter a referência de memória correta do objeto a ser substituído"],
        "correctAnswer": "Para garantir que o objeto na lista seja o mesmo antes de usar 'indexOf', pois a busca por ID é a fonte de verdade",
        "difficulty": "Difícil"
    },
    {
        "question": "Se o método 'main' não chamasse 'scanner.close()', qual seria a consequência?",
        "options": ["Um vazamento de recursos ('resource leak'), pois o stream de entrada do sistema não seria liberado", "Nenhuma consequência perceptível em aplicações de console simples", "O programa não conseguiria ser finalizado corretamente", "A próxima execução do programa falharia ao tentar usar o console"],
        "correctAnswer": "Um vazamento de recursos ('resource leak'), pois o stream de entrada do sistema não seria liberado",
        "difficulty": "Difícil"
    },
    {
        "question": "O uso de uma variável estática 'TAMANHO_MAXIMO' em AlunoRepositoryVetor implica que:",
        "options": ["Todos os objetos da classe AlunoRepositoryVetor compartilharão o mesmo limite de tamanho", "O tamanho máximo não pode ser alterado após a compilação", "A variável pertence à classe, não a uma instância específica", "Todas as alternativas estão corretas"],
        "correctAnswer": "Todas as alternativas estão corretas",
        "difficulty": "Difícil"
    },
    {
        "question": "Qual das seguintes validações NÃO está presente na classe AlunoService ao cadastrar um aluno?",
        "options": ["Validação da unicidade do CPF", "Validação se a matrícula contém apenas números", "Validação se o e-mail tem um formato válido", "Validação se todos os campos são obrigatórios"],
        "correctAnswer": "Validação da unicidade do CPF",
        "difficulty": "Difícil"
    },
    {
        "question": "O que aconteceria se o construtor da classe Aluno estivesse ausente?",
        "options": ["O Java forneceria um construtor padrão (sem argumentos), e a criação 'new Aluno(...)' com parâmetros falharia", "A classe não compilaria", "Os atributos da classe não poderiam ser inicializados", "Seria impossível criar objetos da classe Aluno"],
        "correctAnswer": "O Java forneceria um construtor padrão (sem argumentos), e a criação 'new Aluno(...)' com parâmetros falharia",
        "difficulty": "Difícil"
    },
    {
        "question": "A separação do código em pacotes como 'models', 'repositories', 'services' e 'views' é uma característica de qual arquitetura?",
        "options": ["Arquitetura em Camadas (Layered Architecture)", "Arquitetura de Microsserviços", "Arquitetura MVC (Model-View-Controller)", "Arquitetura Hexagonal"],
        "correctAnswer": "Arquitetura em Camadas (Layered Architecture)",
        "difficulty": "Difícil"
    },
    {
        "question": "Qual a principal limitação do método de remoção em AlunoRepositoryVetor em um cenário de alto desempenho?",
        "options": ["O deslocamento de elementos tem custo O(n), tornando-o ineficiente para vetores grandes", "O uso de dois laços 'for' aninhados aumenta a complexidade para O(n²)", "A busca pelo elemento a ser removido é sempre lenta", "A atribuição de 'null' ao final do vetor consome muito processamento"],
        "correctAnswer": "O deslocamento de elementos tem custo O(n), tornando-o ineficiente para vetores grandes",
        "difficulty": "Difícil"
    },
    {
        "question": "Se a classe AlunoService instanciasse 'new AlunoRepositoryLista()' diretamente em seu construtor, qual seria o principal problema?",
        "options": ["A classe ficaria fortemente acoplada à implementação com 'Lista', impedindo o uso da implementação com 'Vetor' sem alterar o código do serviço", "Isso causaria um erro de compilação", "O desempenho da aplicação seria degradado", "A memória consumida pela aplicação aumentaria significativamente"],
        "correctAnswer": "A classe ficaria fortemente acoplada à implementação com 'Lista', impedindo o uso da implementação com 'Vetor' sem alterar o código do serviço",
        "difficulty": "Difícil"
    },
    {
        "question": "O método 'matches' da classe Pattern, usado no Validador, verifica se:",
        "options": ["A string inteira corresponde à expressão regular", "Qualquer parte da string corresponde à expressão regular", "A string começa com a expressão regular", "A string termina com a expressão regular"],
        "correctAnswer": "A string inteira corresponde à expressão regular",
        "difficulty": "Difícil"
    },
    {
        "question": "A implementação 'buscarPorMatricula' em AlunoRepositoryVetor tem um bug sutil. Se 'totalAlunos' for 0, o que o método retorna?",
        "options": ["Optional.empty(), pois o laço 'for' não executa", "NullPointerException", "ArrayIndexOutOfBoundsException", "Optional contendo o último aluno cadastrado"],
        "correctAnswer": "Optional.empty(), pois o laço 'for' não executa",
        "difficulty": "Difícil"
    },
    {
        "question": "No método 'main', se o usuário digitar '2' e depois de cadastrar um aluno, rodar o programa de novo e digitar '1', o que acontecerá com os dados?",
        "options": ["Os dados cadastrados na primeira execução (Lista) serão perdidos, pois a persistência é em memória", "Os dados serão migrados da Lista para o Vetor", "O programa lembrará dos dados da execução anterior", "O programa lançará um erro de inconsistência de dados"],
        "correctAnswer": "Os dados cadastrados na primeira execução (Lista) serão perdidos, pois a persistência é em memória",
        "difficulty": "Difícil"
    },
    {
        "question": "A classe Validador usa o método 'valor.matches(\"\\\\d+\")'. O que as duas barras invertidas (\\\\) significam?",
        "options": ["A primeira barra 'escapa' a segunda, para que o compilador Java interprete '\\d' literalmente para a expressão regular", "Significa que a busca deve ser por dois dígitos", "É um erro de digitação que deveria ser apenas uma barra", "Indica que a expressão regular é do tipo 'double precision'"],
        "correctAnswer": "A primeira barra 'escapa' a segunda, para que o compilador Java interprete '\\d' literalmente para a expressão regular",
        "difficulty": "Difícil"
    },
    {
        "question": "Se a interface AlunoRepository fosse uma classe abstrata, qual seria a principal diferença?",
        "options": ["Ela poderia conter implementações de métodos padrão, além de métodos abstratos", "As classes filhas usariam a palavra-chave 'extends' em vez de 'implements'", "Ela poderia ter variáveis de instância (atributos)", "Todas as alternativas estão corretas"],
        "correctAnswer": "Todas as alternativas estão corretas",
        "difficulty": "Difícil"
    },
    {
        "question": "Por que o loop 'while (alunoRepository == null)' na classe Main é uma boa prática?",
        "options": ["Garante que a aplicação não prossiga com uma referência nula, forçando o usuário a fazer uma escolha válida de armazenamento", "Evita que o programa termine abruptamente se a primeira entrada for inválida", "Otimiza a performance da inicialização", "É a única maneira de ler a entrada do usuário em um loop"],
        "correctAnswer": "Garante que a aplicação não prossiga com uma referência nula, forçando o usuário a fazer uma escolha válida de armazenamento",
        "difficulty": "Difícil"
    },
    # =================================================================
    # == NÍVEL EXTREMAMENTE DIFÍCIL (30 PERGUNTAS) ==
    # =================================================================
    {
        "question": "Qual seria o impacto de mudar a coleção em AlunoRepositoryLista de 'List<Aluno>' para 'Map<Integer, Aluno>', usando o ID como chave?",
        "options": ["A busca por ID se tornaria O(1), mas a listagem ordenada por nome exigiria extrair os valores e ordená-los separadamente", "A inserção de novos alunos se tornaria mais lenta", "A busca por matrícula seria impossível de implementar", "O consumo de memória seria drasticamente reduzido"],
        "correctAnswer": "A busca por ID se tornaria O(1), mas a listagem ordenada por nome exigiria extrair os valores e ordená-los separadamente",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "O método 'atualizar' de AlunoRepositoryLista usa 'indexOf'. Se a classe Aluno não implementasse 'equals' e 'hashCode', 'indexOf' funcionaria?",
        "options": ["Sim, pois 'indexOf' usaria a comparação de referência (==), que funcionaria porque 'alunoExistente' é a mesma referência do objeto na lista", "Não, 'indexOf' sempre requer a implementação de 'equals' e 'hashCode'", "Sim, mas seria extremamente lento", "Lançaria uma 'UnsupportedOperationException'"],
        "correctAnswer": "Sim, pois 'indexOf' usaria a comparação de referência (==), que funcionaria porque 'alunoExistente' é a mesma referência do objeto na lista",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "O método 'remover' em AlunoRepositoryVetor é ineficiente. Uma alternativa seria trocar o elemento a ser removido com o último elemento e decrementar 'totalAlunos'. Qual a desvantagem dessa abordagem?",
        "options": ["Altera a ordem original de inserção dos elementos no vetor", "A complexidade de tempo ainda seria O(n)", "Exigiria a criação de um novo vetor a cada remoção", "Não funcionaria se o elemento a ser removido fosse o último"],
        "correctAnswer": "Altera a ordem original de inserção dos elementos no vetor",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "A expressão regular para CPF ( `^\\\\d{3}\\\\.\\\\d{3}\\\\.\\\\d{3}-\\\\d{2}$` ) valida apenas o formato. Como a AlunoService poderia ser melhorada para validar a autenticidade do CPF?",
        "options": ["Implementando o algoritmo de validação dos dígitos verificadores do CPF", "Verificando se o CPF existe em um banco de dados externo da Receita Federal", "A expressão regular já garante a autenticidade", "Adicionando uma validação para CPFs com todos os dígitos iguais"],
        "correctAnswer": "Implementando o algoritmo de validação dos dígitos verificadores do CPF",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "Se a aplicação precisasse ser multithread, qual implementação de AlunoRepository apresentaria problemas de condição de corrida (race condition) sem sincronização?",
        "options": ["Ambas, pois operações como 'proximoId++' e 'alunos.add' não são atômicas", "Apenas AlunoRepositoryLista", "Apenas AlunoRepositoryVetor", "Nenhuma, pois são inerentemente thread-safe"],
        "correctAnswer": "Ambas, pois operações como 'proximoId++' e 'alunos.add' não são atômicas",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "Considere o método 'remover' em AlunoRepositoryLista: 'alunos.removeIf(aluno -> aluno.getId() == id)'. Qual seria uma consequência de não usar a variável 'id' final ou efetivamente final dentro da lambda?",
        "options": ["O código não compilaria, pois lambdas só podem acessar variáveis locais que são finais ou efetivamente finais", "A condição de remoção se tornaria imprevisível", "Ocorreriam vazamentos de memória", "A performance da remoção seria degradada"],
        "correctAnswer": "O código não compilaria, pois lambdas só podem acessar variáveis locais que são finais ou efetivamente finais",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "Se o método 'listarTodos' de AlunoRepositoryLista retornasse a própria lista 'this.alunos' em vez de uma nova lista coletada do stream, que problema de encapsulamento isso criaria?",
        "options": ["O código cliente (ex: AlunoView) poderia modificar a lista interna do repositório diretamente, quebrando a integridade dos dados", "Ocorreriam problemas de concorrência", "O retorno seria mais lento", "Não haveria nenhum problema, seria uma otimização"],
        "correctAnswer": "O código cliente (ex: AlunoView) poderia modificar a lista interna do repositório diretamente, quebrando a integridade dos dados",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "A atual implementação do repositório é em memória. Para torná-la persistente entre execuções, qual seria a mudança mais impactante no projeto?",
        "options": ["Criar uma nova implementação de AlunoRepository (ex: AlunoRepositoryJDBC) que se comunique com um banco de dados", "Adicionar serialização de objetos para salvar a lista em um arquivo", "Usar variáveis de ambiente para armazenar os dados dos alunos", "Aumentar o tamanho do AlunoRepositoryVetor para um número muito grande"],
        "correctAnswer": "Criar uma nova implementação de AlunoRepository (ex: AlunoRepositoryJDBC) que se comunique com um banco de dados",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "O método 'buscarPorId' em AlunoRepositoryVetor tem uma falha lógica. Onde está o 'return Optional.empty()' e por que está incorreto?",
        "options": ["Está dentro do laço 'for'; deveria estar fora, pois ele retorna vazio após checar apenas o primeiro elemento", "Deveria ser 'return null;' em vez de 'Optional.empty()'", "Não há falha lógica, o código está correto", "Deveria estar antes do laço 'for' para inicializar a busca"],
        "correctAnswer": "Está dentro do laço 'for'; deveria estar fora, pois ele retorna vazio após checar apenas o primeiro elemento",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "Se a classe AlunoService precisasse realizar uma operação que envolvesse remover um aluno e adicionar outro atomicamente (ou ambos funcionam, ou nenhum), qual padrão de projeto seria mais adequado para o AlunoRepository?",
        "options": ["Padrão Unit of Work", "Padrão Memento", "Padrão Command", "Padrão Decorator"],
        "correctAnswer": "Padrão Unit of Work",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "A validação 'isNumeric' em Validador falharia para qual das seguintes entradas, que podem ser consideradas numéricas em outros contextos?",
        "options": ["Matrículas com números negativos (ex: '-123')", "Matrículas com ponto flutuante (ex: '123.45')", "Matrículas em notação científica (ex: '1.23e4')", "Todas as alternativas estão corretas"],
        "correctAnswer": "Todas as alternativas estão corretas",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "No AlunoRepositoryVetor, se dois alunos fossem removidos em sequência sem que a busca encontrasse o primeiro, o que aconteceria?",
        "options": ["O segundo aluno não seria removido, pois a busca continuaria a partir do índice onde parou, que estaria fora dos limites após o deslocamento", "O código funcionaria normalmente, removendo o segundo aluno", "Lançaria uma 'ConcurrentModificationException'", "O primeiro aluno seria removido na segunda chamada"],
        "correctAnswer": "O código funcionaria normalmente, removendo o segundo aluno",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "Qual é a principal razão para a classe 'Validador' estar no pacote 'utils' em vez de 'services'?",
        "options": ["Porque seus métodos são genéricos e reutilizáveis, não contendo lógica de negócio específica da aplicação", "Porque a classe não tem dependências com outras partes do sistema", "Por convenção de nomenclatura de pacotes em Java", "Porque o pacote 'services' é reservado para classes com estado"],
        "correctAnswer": "Porque seus métodos são genéricos e reutilizáveis, não contendo lógica de negócio específica da aplicação",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "Se o método 'salvar' em AlunoRepositoryLista não atribuísse um ID ('aluno.setId(...)'), qual método da mesma classe falharia primeiro ao tentar usar esse aluno salvo?",
        "options": ["'atualizar', pois 'buscarPorId' retornaria um Optional vazio, impedindo a atualização", "'remover', pois não conseguiria encontrar o aluno pelo ID para remoção", "'listarTodos', pois a ordenação por nome falharia", "'buscarPorMatricula', pois a busca por ID é mais comum"],
        "correctAnswer": "'atualizar', pois 'buscarPorId' retornaria um Optional vazio, impedindo a atualização",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "A classe Main usa um loop 'while' para garantir a escolha do repositório. Uma alternativa seria usar um loop 'do-while'. Qual seria a principal diferença no comportamento?",
        "options": ["O menu de escolha seria exibido pelo menos uma vez, mesmo que a condição do loop fosse falsa inicialmente", "O código seria menos legível", "A performance seria ligeiramente pior", "Não haveria nenhuma diferença de comportamento"],
        "correctAnswer": "O menu de escolha seria exibido pelo menos uma vez, mesmo que a condição do loop fosse falsa inicialmente",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "A validação de e-mail com a regex `^[A-Za-z0-9+_-]+@[A-Za-z0-9.-]+$` é simplista. Qual formato de e-mail válido ela rejeitaria incorretamente?",
        "options": ["email com apóstrofo no nome local (ex: 'o'reilly@example.com')", "email com subdomínio (ex: 'user@mail.example.com')", "email com domínio de nível superior longo (ex: 'user@example.company')", "email com hífen no domínio (ex: 'user@example-domain.com')"],
        "correctAnswer": "email com apóstrofo no nome local (ex: 'o'reilly@example.com')",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "Qual princípio do SOLID é mais beneficiado pela decisão de ter uma interface AlunoRepository e múltiplas implementações?",
        "options": ["Princípio Aberto/Fechado (Open/Closed Principle)", "Princípio da Responsabilidade Única (Single Responsibility Principle)", "Princípio da Substituição de Liskov (Liskov Substitution Principle)", "Princípio da Segregação de Interfaces (Interface Segregation Principle)"],
        "correctAnswer": "Princípio Aberto/Fechado (Open/Closed Principle)",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "Se o método 'listarTodos' em AlunoRepositoryVetor não especificasse os limites (0, totalAlunos) em 'Arrays.stream', o que aconteceria?",
        "options": ["Lançaria uma 'NullPointerException' ao tentar chamar 'getNome' em um elemento nulo do vetor durante a ordenação", "Funcionaria corretamente, mas seria menos eficiente", "O stream conteria apenas o primeiro elemento do vetor", "O código não compilaria"],
        "correctAnswer": "Lançaria uma 'NullPointerException' ao tentar chamar 'getNome' em um elemento nulo do vetor durante a ordenação",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "O método 'main' captura 'NumberFormatException'. O que aconteceria se o usuário digitasse um número fora do intervalo de um 'int', como 9999999999?",
        "options": ["Ocorrereria uma 'NumberFormatException', pois o número é muito grande para ser convertido para 'int'", "O número seria convertido para o valor máximo de 'int' (Integer.MAX_VALUE)", "O programa travaria sem lançar uma exceção", "A conversão funcionaria, mas o 'if' subsequente falharia"],
        "correctAnswer": "Ocorrereria uma 'NumberFormatException', pois o número é muito grande para ser convertido para 'int'",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "A atual estrutura de pacotes separa por funcionalidade técnica (models, views, services). Qual é o nome da abordagem alternativa que agrupa classes por funcionalidade de negócio (ex: pacote 'aluno' contendo Aluno.java, AlunoService.java, etc.)?",
        "options": ["Package by Feature", "Package by Layer", "Vertical Slicing", "Domain-Driven Design"],
        "correctAnswer": "Package by Feature",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "Imagine que AlunoRepositoryLista usa um 'CopyOnWriteArrayList'. Qual seria o principal efeito dessa mudança?",
        "options": ["A leitura (listarTodos) seria muito rápida e thread-safe sem bloqueios, mas a escrita (salvar, remover) seria cara, pois cria uma nova cópia do array", "Todas as operações se tornariam mais lentas", "A aplicação consumiria menos memória", "Não haveria efeito perceptível para esta aplicação"],
        "correctAnswer": "A leitura (listarTodos) seria muito rápida e thread-safe sem bloqueios, mas a escrita (salvar, remover) seria cara, pois cria uma nova cópia do array",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "A classe AlunoView depende concretamente de AlunoService. Como seria possível aplicar o Princípio da Inversão de Dependência também a essa relação?",
        "options": ["Criando uma interface 'AlunoServiceContract' que AlunoService implementaria, e AlunoView dependeria da interface", "Tornando os métodos de AlunoService estáticos", "Passando AlunoView como um parâmetro para o construtor de AlunoService", "Não é possível aplicar o princípio nesse caso"],
        "correctAnswer": "Criando uma interface 'AlunoServiceContract' que AlunoService implementaria, e AlunoView dependeria da interface",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "O método 'buscarPorId' em AlunoRepositoryVetor tem uma eficiência de O(n). Como ele poderia ser otimizado para O(log n)?",
        "options": ["Mantendo o vetor sempre ordenado por ID e utilizando busca binária (Arrays.binarySearch)", "Usando um laço 'for' paralelo", "Aumentando o tamanho máximo do vetor", "Não é possível otimizá-lo além de O(n) em um vetor não ordenado"],
        "correctAnswer": "Mantendo o vetor sempre ordenado por ID e utilizando busca binária (Arrays.binarySearch)",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "O que aconteceria se a variável 'proximoId' em AlunoRepositoryLista fosse declarada como 'static'?",
        "options": ["Todas as instâncias de AlunoRepositoryLista no programa compartilhariam o mesmo contador de ID, potencialmente causando IDs duplicados se usadas independentemente", "O código não compilaria", "Cada instância teria seu próprio contador de ID, como já acontece", "A performance de inserção melhoraria"],
        "correctAnswer": "Todas as instâncias de AlunoRepositoryLista no programa compartilhariam o mesmo contador de ID, potencialmente causando IDs duplicados se usadas independentemente",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "A dependência do sistema em 'System.in' e 'System.out' dificulta testes automatizados. Qual padrão de projeto resolveria isso?",
        "options": ["Injetar interfaces para entrada e saída de dados (ex: IUserInput, IUserOutput) na AlunoView", "Usar um framework de logging como Log4j", "Criar um arquivo de configuração para as mensagens do console", "Executar os testes em um contêiner Docker"],
        "correctAnswer": "Injetar interfaces para entrada e saída de dados (ex: IUserInput, IUserOutput) na AlunoView",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "O método 'remover' em AlunoRepositoryVetor não verifica se o ID existe antes de percorrer o vetor para remoção. Isso é um problema?",
        "options": ["Não, é eficiente. O laço 'for' já serve como a verificação; se não encontrar, nada acontece e retorna 'false'", "Sim, deveria haver uma busca prévia para evitar o processamento desnecessário do laço de remoção", "Sim, isso pode levar a uma 'ArrayIndexOutOfBoundsException'", "Sim, isso viola o princípio da responsabilidade única"],
        "correctAnswer": "Não, é eficiente. O laço 'for' já serve como a verificação; se não encontrar, nada acontece e retorna 'false'",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "A classe AlunoService retorna strings de erro, como 'Erro: Todos os campos são obrigatórios!'. Qual seria uma abordagem mais robusta para o tratamento de erros?",
        "options": ["Lançar exceções customizadas (ex: 'CamposObrigatoriosException') e tratá-las na AlunoView", "Retornar códigos de erro numéricos em vez de strings", "Gravar os erros em um arquivo de log e retornar 'null'", "Sempre retornar 'false' em caso de erro"],
        "correctAnswer": "Lançar exceções customizadas (ex: 'CamposObrigatoriosException') e tratá-las na AlunoView",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "O método 'main' instancia AlunoService e AlunoView. Qual padrão de projeto descreve a responsabilidade de criar e conectar esses objetos?",
        "options": ["Injeção de Dependência (usando um 'Composition Root' ou Container DI)", "Builder", "Factory Method", "Prototype"],
        "correctAnswer": "Injeção de Dependência (usando um 'Composition Root' ou Container DI)",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "O método 'atualizar' de AlunoRepositoryVetor tem complexidade O(n). Se a estrutura fosse uma 'HashMap<Integer, Aluno>', qual seria a complexidade?",
        "options": ["O(1) em média, pois a atualização seria feita diretamente pela chave (ID)", "Ainda seria O(n), pois a busca pela chave é linear", "O(log n), devido à estrutura da hash table", "O(n²), devido a colisões de hash"],
        "correctAnswer": "O(1) em média, pois a atualização seria feita diretamente pela chave (ID)",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "Se o método 'remover' de AlunoRepositoryLista fosse chamado com um ID que aparece duas vezes na lista (devido a um bug), o que 'removeIf' faria?",
        "options": ["Removeria todas as ocorrências que correspondem à condição", "Removeria apenas a primeira ocorrência", "Lançaria uma 'IllegalStateException'", "Entraria em um loop infinito"],
        "correctAnswer": "Removeria todas as ocorrências que correspondem à condição",
        "difficulty": "Extremamente Difícil"
    },
    {
        "question": "Qual é o nome da classe que representa o modelo de um aluno?",
        "options": ["Aluno.java", "AlunoService.java", "AlunoView.java", "AlunoModel.java"],
        "correctAnswer": "Aluno.java",
        "difficulty": "Fácil"
    },
    {
        "question": "Para que serve a anotação @Override?",
        "options": ["Indica que um método está sendo sobrescrito", "Indica um método obsoleto", "Inicia um novo método", "Importa uma biblioteca"],
        "correctAnswer": "Indica que um método está sendo sobrescrito",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual classe é responsável pela interface e interação com o usuário no console?",
        "options": ["AlunoView", "AlunoService", "Main", "AlunoRepository"],
        "correctAnswer": "AlunoView",
        "difficulty": "Fácil"
    },
    {
        "question": "No menu principal em AlunoView, qual número o usuário deve digitar para sair do sistema?",
        "options": ["0", "1", "9", "-1"],
        "correctAnswer": "0",
        "difficulty": "Fácil"
    },

    # =================================================================
    # == QUESTÕES EXTRAS (31–60) ==
    # =================================================================
    {
        "question": "O que o método getIdade() em Aluno.java retorna?",
        "options": ["Define a idade do aluno", "Retorna a idade do aluno", "Cria uma variável idade", "Converte idade em String"],
        "correctAnswer": "Retorna a idade do aluno",
        "difficulty": "Fácil"
    },
    {
        "question": "No trecho this.nome = nome; o que o 'this' representa?",
        "options": ["Cria novos objetos", "Refere-se ao atributo da classe atual", "Importa bibliotecas externas", "Remove valor de nome"],
        "correctAnswer": "Refere-se ao atributo da classe atual",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual o papel da anotação @Override em um método de repositório?",
        "options": ["Define uma constante", "Sobrescreve um método da interface", "Cria método vazio automaticamente", "Executa de forma assíncrona"],
        "correctAnswer": "Sobrescreve um método da interface",
        "difficulty": "Fácil"
    },
    {
        "question": "O construtor AlunoRepositoryVetor(int tamanho) faz o quê?",
        "options": ["Cria lista dinâmica", "Inicializa vetor de tamanho fixo", "Converte alunos em String", "Gera IDs automáticos"],
        "correctAnswer": "Inicializa vetor de tamanho fixo",
        "difficulty": "Fácil"
    },
    {
        "question": "O atributo private int indice = 0 em AlunoRepositoryVetor serve para?",
        "options": ["Guardar idade", "Definir máximo do vetor", "Controlar posição de inserção", "Contar alunos aprovados"],
        "correctAnswer": "Controlar posição de inserção",
        "difficulty": "Fácil"
    },
    {
        "question": "O que acontece se o nome não for válido em AlunoService?",
        "options": ["Adiciona aluno sempre", "Não adiciona aluno", "Remove aluno inválido", "Ordena alunos"],
        "correctAnswer": "Não adiciona aluno",
        "difficulty": "Fácil"
    },
    {
        "question": "O que verifica !nome.trim().isEmpty() no Validador?",
        "options": ["Nome é numérico", "Nome não está vazio", "Nome é nulo", "Nome contém números"],
        "correctAnswer": "Nome não está vazio",
        "difficulty": "Fácil"
    },
    {
        "question": "System.out.println('1 - Cadastrar aluno'); em AlunoView faz o quê?",
        "options": ["Cadastra aluno", "Exibe opção no menu", "Lê dados do aluno", "Finaliza programa"],
        "correctAnswer": "Exibe opção no menu",
        "difficulty": "Fácil"
    },
    {
        "question": "int idade = sc.nextInt(); lê qual tipo de dado?",
        "options": ["Texto", "Número inteiro", "Fecha scanner", "String"],
        "correctAnswer": "Número inteiro",
        "difficulty": "Fácil"
    },
    {
        "question": "List<Aluno> alunos = service.listarAlunos(); obtém o quê?",
        "options": ["Cria alunos", "Lista de alunos cadastrados", "Remove alunos", "Valida nomes"],
        "correctAnswer": "Lista de alunos cadastrados",
        "difficulty": "Fácil"
    },
    {
        "question": "O laço for (Aluno a : alunos) { ... } em AlunoView faz o quê?",
        "options": ["Remove alunos", "Imprime nome e idade", "Cria alunos", "Ordena alunos"],
        "correctAnswer": "Imprime nome e idade",
        "difficulty": "Fácil"
    },
    {
        "question": "O comando alunos.add(aluno) faz o quê?",
        "options": ["Remove aluno", "Adiciona aluno", "Substitui lista", "Conta alunos"],
        "correctAnswer": "Adiciona aluno",
        "difficulty": "Fácil"
    },
    {
        "question": "O comando indice++; faz o quê?",
        "options": ["Zera vetor", "Cria instância", "Avança índice", "Remove aluno"],
        "correctAnswer": "Avança índice",
        "difficulty": "Fácil"
    },
    {
        "question": "No switch de AlunoView, o case 2 chama qual função?",
        "options": ["Finalizar", "Listar alunos", "Remover aluno", "Cadastrar aluno"],
        "correctAnswer": "Listar alunos",
        "difficulty": "Fácil"
    },
    {
        "question": "repository = new AlunoRepositoryLista(); define o quê?",
        "options": ["Cria vetor fixo", "Usa lista dinâmica", "Remove alunos", "Cria aluno padrão"],
        "correctAnswer": "Usa lista dinâmica",
        "difficulty": "Fácil"
    },
    {
        "question": "repository = new AlunoRepositoryVetor(10); cria o quê?",
        "options": ["Lista infinita", "Repositório com vetor de tamanho 10", "Arquivo alunos", "Banco SQL"],
        "correctAnswer": "Repositório com vetor de tamanho 10",
        "difficulty": "Fácil"
    },
    {
        "question": "O bloco default em um switch faz o quê?",
        "options": ["Fecha programa", "Exibe opção inválida", "Repete ação", "Cria variável"],
        "correctAnswer": "Exibe opção inválida",
        "difficulty": "Fácil"
    },
    {
        "question": "new AlunoView().menu(); em Main.java faz o quê?",
        "options": ["Finaliza programa", "Chama menu", "Cria aluno", "Valida idade"],
        "correctAnswer": "Chama menu",
        "difficulty": "Fácil"
    },
    {
        "question": "O método adicionar em AlunoRepositoryVetor faz o quê?",
        "options": ["Remove aluno", "Insere aluno e incrementa índice", "Ordena alunos", "Cria lista dinâmica"],
        "correctAnswer": "Insere aluno e incrementa índice",
        "difficulty": "Fácil"
    },
    {
        "question": "boolean continuar = true em AlunoView significa?",
        "options": ["Conta alunos", "Controla execução do menu", "Cria aluno", "Declara índice"],
        "correctAnswer": "Controla execução do menu",
        "difficulty": "Fácil"
    },
    {
        "question": "O laço while (continuar) faz o quê?",
        "options": ["Executa 1 vez", "Executa enquanto continuar for verdadeiro", "Nunca executa", "Encerra"],
        "correctAnswer": "Executa enquanto continuar for verdadeiro",
        "difficulty": "Fácil"
    },
    {
        "question": "O contrato Aluno buscarPorNome(String nome); define o quê?",
        "options": ["Remove aluno", "Permite buscar aluno por nome", "Retorna lista vazia", "Converte aluno"],
        "correctAnswer": "Permite buscar aluno por nome",
        "difficulty": "Fácil"
    },
    {
        "question": "O método buscarAlunoPorNome em Service retorna?",
        "options": ["Remove aluno", "Aluno com base no nome", "Cria aluno", "Valida idade"],
        "correctAnswer": "Aluno com base no nome",
        "difficulty": "Fácil"
    },
    {
        "question": "System.out.println('Digite o nome para buscar:'); faz o quê?",
        "options": ["Lê nome", "Exibe mensagem", "Busca automaticamente", "Finaliza"],
        "correctAnswer": "Exibe mensagem",
        "difficulty": "Fácil"
    },
    {
        "question": "service.buscarAlunoPorNome(nome); faz o quê?",
        "options": ["Remove aluno", "Procura aluno pelo nome", "Cria lista", "Zera idade"],
        "correctAnswer": "Procura aluno pelo nome",
        "difficulty": "Fácil"
    },
    {
        "question": "O if (encontrado != null) faz o quê?",
        "options": ["Sempre imprime", "Imprime se encontrado", "Remove aluno", "Cria aluno"],
        "correctAnswer": "Imprime se encontrado",
        "difficulty": "Fácil"
    },
    {
        "question": "O laço for em AlunoRepositoryLista com equals(nome) faz o quê?",
        "options": ["Cria aluno", "Retorna aluno com nome igual", "Remove todos", "Ordena lista"],
        "correctAnswer": "Retorna aluno com nome igual",
        "difficulty": "Fácil"
    },
    {
        "question": "O for em AlunoRepositoryVetor até indice faz o quê?",
        "options": ["Adiciona aluno", "Busca aluno por nome", "Apaga vetor", "Cria lista"],
        "correctAnswer": "Busca aluno por nome",
        "difficulty": "Fácil"
    },
    {
        "question": "O case 3 em AlunoView executa?",
        "options": ["Remove aluno", "Buscar aluno por nome", "Listar alunos", "Sair"],
        "correctAnswer": "Buscar aluno por nome",
        "difficulty": "Fácil"
    },
    {
        "question": "O case 0 em AlunoView faz?",
        "options": ["Reinicia menu", "Sai do sistema", "Cadastra aluno", "Lista alunos"],
        "correctAnswer": "Sai do sistema",
        "difficulty": "Fácil"
    }


]
TIME_PER_QUESTION, WINNING_SCORE, PENALTY_POINTS = 30, 200, 5

def create_new_game_state(room_id: str, host_name: str):
    if room_id not in game_states:
        game_states[room_id] = {
            "host": host_name, "players": {}, "scores": {}, "questions": list(default_questions),
            "current_question": None, "current_player_index": 0, "timer_task": None, "game_started": False
        }

async def start_game(room_id: str):
    state = game_states.get(room_id)
    if not state or state["game_started"] or len(state["players"]) < 2: return
    for player_id in state["players"]:
        player_questions = database.get_questions_by_player(player_id)
        state["questions"].extend(player_questions)
    state["game_started"] = True
    await next_turn(room_id, new_game=True)

async def end_game_and_save_scores(room_id: str, winner: str):
    state = game_states.get(room_id)
    if not state: return
    host_name = state["host"]
    print(f"Fim de jogo na sala de '{host_name}'. Salvando pontuações...")
    for player_id, score in state["scores"].items():
        if score > 0: database.update_player_score(player_id, score, host_name)
    await manager.broadcast(room_id, {"type": "gameOver", "winner": winner})
    if room_id in game_states:
        if game_states[room_id].get("timer_task"): game_states[room_id]["timer_task"].cancel()
        del game_states[room_id]

async def next_turn(room_id: str, new_game: bool = False):
    state = game_states.get(room_id)
    if not state: return
    if state["timer_task"]: state["timer_task"].cancel()
    for player_id, score in state["scores"].items():
        if score >= WINNING_SCORE:
            await end_game_and_save_scores(room_id, player_id)
            return
    if not new_game:
        state["current_player_index"] = (state["current_player_index"] + 1) % len(state["players"])
    if not state["questions"]:
        winner = max(state["scores"], key=state["scores"].get) if state["scores"] else "Empate"
        await end_game_and_save_scores(room_id, winner)
        return
    state["current_question"] = state["questions"].pop(random.randrange(len(state["questions"])))
    state["timeRemaining"] = TIME_PER_QUESTION
    await manager.broadcast(room_id, {"type": "gameStateUpdate", "state": get_public_state(room_id)})
    state["timer_task"] = asyncio.create_task(timer(room_id))

async def timer(room_id: str):
    try:
        await asyncio.sleep(TIME_PER_QUESTION)
        state = game_states.get(room_id)
        if state:
            players_list = list(state["players"].keys())
            if players_list:
                current_player_id = players_list[state["current_player_index"]]
                state["scores"][current_player_id] = max(0, state["scores"][current_player_id] - PENALTY_POINTS)
            await next_turn(room_id)
    except asyncio.CancelledError: pass

def get_public_state(room_id: str):
    state = game_states.get(room_id, {})
    return {
        "players": state.get("players", {}), "scores": state.get("scores", {}),
        "current_question": state.get("current_question"), "current_player_index": state.get("current_player_index", 0),
        "timeRemaining": state.get("timeRemaining")
    }

@app.websocket("/ws/{room_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, client_id: str):
    await manager.connect(websocket, room_id, client_id)
    
    # Cria um novo estado de jogo se a sala for nova
    if room_id not in game_states:
        create_new_game_state(room_id, client_id)
    
    state = game_states[room_id]
    player_just_joined = False
    
    # Adiciona o novo jogador se ele não estiver na sala
    if client_id not in state["players"]:
        state["players"][client_id] = {"name": client_id}
        state["scores"][client_id] = 0
        player_just_joined = True

    # Se um jogador acabou de entrar e o jogo ainda não começou, atualiza o lobby
    if player_just_joined and not state["game_started"]:
        await manager.broadcast(room_id, {"type": "gameStateUpdate", "state": get_public_state(room_id)})

    # Tenta iniciar o jogo. A função só prosseguirá se houver 2 ou mais jogadores.
    await start_game(room_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            state = game_states.get(room_id)
            if not state: break
            
            if message["type"] == "submitAnswer":
                players_list = list(state["players"].keys())
                if not players_list: continue
                current_player_id = players_list[state["current_player_index"]]
                
                if client_id == current_player_id:
                    if state.get("timer_task"):
                        state["timer_task"].cancel()
                    is_correct = message["answer"] == state["current_question"]["correctAnswer"]
                    await manager.broadcast(room_id, {"type": "answerResult", "correctAnswer": state["current_question"]["correctAnswer"], "selectedAnswer": message["answer"]})
                    
                    if is_correct:
                        state["scores"][client_id] += 10
                    else:
                        state["scores"][client_id] = max(0, state["scores"][client_id] - PENALTY_POINTS)
                    
                    await asyncio.sleep(2)
                    await next_turn(room_id)

    except WebSocketDisconnect:
        # Lógica de desconexão aprimorada
        manager.disconnect(room_id, client_id)
        state = game_states.get(room_id)
        if not state:
            return

        # Verifica se o cliente desconectado era de fato um jogador
        if client_id in state["players"]:
            del state["players"][client_id]
            del state["scores"][client_id]

            # CONDIÇÃO 1: O jogo estava em andamento e agora não há jogadores suficientes.
            if state["game_started"] and len(state["players"]) < 2:
                if state.get("timer_task"):
                    state["timer_task"].cancel()
                await end_game_and_save_scores(room_id, "Jogo encerrado por desconexão")
                return  # Encerra o jogo e a função

            # CONDIÇÃO 2: O jogo continua (no lobby ou com jogadores suficientes).
            # Garante que o índice do jogador atual seja válido.
            if state["players"]:
                state["current_player_index"] %= len(state["players"])
            
            # Envia a atualização para os jogadores restantes.
            await manager.broadcast(room_id, {"type": "gameStateUpdate", "state": get_public_state(room_id)})