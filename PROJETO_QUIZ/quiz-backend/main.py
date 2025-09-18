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
        "options": ["Indica que um método está sendo sobrescrito da superclasse", "Sinaliza que um método será removido em versões futuras", "Define um novo método que não pode ser modificado", "Inicia a execução principal de uma classe específica"],
        "correctAnswer": "Indica que um método está sendo sobrescrito da superclasse",
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
        "options": ["Permite o acesso seguro aos valores de atributos privados", "Modifica diretamente os valores de atributos públicos", "Exclui permanentemente um objeto da memória RAM", "Constrói uma nova instância de um objeto da classe"],
        "correctAnswer": "Permite o acesso seguro aos valores de atributos privados",
        "difficulty": "Fácil"
    },
    {
        "question": "O que faz um método 'setter'?",
        "options": ["Permite a modificação segura dos valores de atributos privados", "Acessa os valores de atributos sem permitir alterá-los", "Retorna o nome da classe em formato de texto (String)", "Verifica se um determinado objeto possui valor nulo"],
        "correctAnswer": "Permite a modificação segura dos valores de atributos privados",
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
        "options": ["Para proteger os dados e controlar o acesso através de getters e setters", "Para otimizar o consumo de memória RAM da aplicação", "Para tornar o acesso aos atributos consideravelmente mais rápido", "Para que possam ser acessados por qualquer classe em qualquer pacote"],
        "correctAnswer": "Para proteger os dados e controlar o acesso através de getters e setters",
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
        "options": ["AlunoRepositoryLista", "AlunoRepositoryArray", "AlunoRepositoryList", "AlunoRepositoryVector"],
        "correctAnswer": "AlunoRepositoryLista",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual classe implementa AlunoRepository usando um vetor (array)?",
        "options": ["AlunoRepositoryVetor", "AlunoRepositoryArray", "AlunoRepositoryVector", "AlunoRepositoryLinked"],
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
        "options": ["isNullOrEmpty", "checkIfBlank", "validateString", "isEmptyOrNull"],
        "correctAnswer": "isNullOrEmpty",
        "difficulty": "Fácil"
    },
    {
        "question": "O que o método toString() na classe Aluno retorna?",
        "options": ["Uma representação em texto com todos os dados do aluno", "Apenas o número de identificação (ID) do aluno", "O endereço de memória onde o objeto está alocado", "Um valor booleano indicando se o aluno está ativo"],
        "correctAnswer": "Uma representação em texto com todos os dados do aluno",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual método da AlunoView é responsável por exibir o menu de opções?",
        "options": ["mostrarMenu()", "displayOptions()", "printChoices()", "viewSelector()"],
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
        "options": ["Para gerar um ID único para cada novo aluno cadastrado", "Para armazenar a quantidade total de alunos na lista", "Para definir o limite máximo de alunos que podem ser criados", "Para guardar o último ID de aluno que foi removido"],
        "correctAnswer": "Para gerar um ID único para cada novo aluno cadastrado",
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
        "options": ["Um objeto completo do tipo Aluno", "Apenas o número de ID do aluno", "Uma String contendo o nome do aluno", "Uma lista com todos os alunos atuais"],
        "correctAnswer": "Um objeto completo do tipo Aluno",
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
        "options": ["Refere-se à instância atual do objeto que está sendo criado", "Indica a superclasse (classe pai) da classe atual", "Acessa uma variável estática compartilhada entre todos os objetos", "Aponta para o pacote onde a classe está localizada"],
        "correctAnswer": "Refere-se à instância atual do objeto que está sendo criado",
        "difficulty": "Fácil"
    },
    {
        "question": "O que a classe 'Optional' representa?",
        "options": ["Um objeto contêiner que pode ou não conter um valor não-nulo", "Uma lista de opções de múltipla escolha para o usuário", "Um tipo de dado que não exige a alocação de memória", "Uma classe que oferece métodos para validar entradas"],
        "correctAnswer": "Um objeto contêiner que pode ou não conter um valor não-nulo",
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
        "options": ["Fecha o objeto Scanner e libera os recursos do sistema que ele estava usando", "Limpa o buffer de entrada do scanner para a próxima leitura de dados", "Reinicia o scanner para o início do fluxo de entrada de dados", "Faz uma pausa na execução do programa aguardando uma nova entrada"],
        "correctAnswer": "Fecha o objeto Scanner e libera os recursos do sistema que ele estava usando",
        "difficulty": "Fácil"
    },
    # =================================================================
    # == NÍVEL MÉDIO (30 PERGUNTAS) ==
    # =================================================================
    {
        "question": "Por que os métodos na classe Validador são declarados como 'static'?",
        "options": ["Para que possam ser chamados sem a necessidade de criar uma instância da classe", "Para que seu valor seja compartilhado e sincronizado entre múltiplas threads", "Para impedir que classes filhas possam sobrescrever sua implementação", "Para garantir que a alocação de memória para eles seja mais eficiente"],
        "correctAnswer": "Para que possam ser chamados sem a necessidade de criar uma instância da classe",
        "difficulty": "Médio"
    },
    {
        "question": "Qual a finalidade de usar Optional<Aluno> como tipo de retorno em métodos de busca?",
        "options": ["Para tratar explicitamente a possibilidade de um resultado não ser encontrado, evitando NullPointerException", "Para retornar uma lista de alunos onde cada um pode ser nulo ou não", "Para otimizar a performance da consulta em bancos de dados relacionais", "Para forçar o desenvolvedor a usar um bloco try-catch ao chamar o método"],
        "correctAnswer": "Para tratar explicitamente a possibilidade de um resultado não ser encontrado, evitando NullPointerException",
        "difficulty": "Médio"
    },
    {
        "question": "Na classe Main, como o programa decide qual implementação de AlunoRepository utilizar?",
        "options": ["O usuário escolhe entre 'Vetor' ou 'Lista' através de um menu no console", "O sistema operacional determina a melhor implementação em tempo de execução", "É usada a implementação 'Lista' por padrão em todas as execuções", "O programa verifica qual arquivo de configuração (.properties) está presente"],
        "correctAnswer": "O usuário escolhe entre 'Vetor' ou 'Lista' através de um menu no console",
        "difficulty": "Médio"
    },
    {
        "question": "Explique o que a linha 'scanner.nextLine();' faz logo após 'scanner.nextInt();' em AlunoView.",
        "options": ["Consome o caractere de nova linha (\\n) que ficou no buffer de entrada", "Lê a próxima linha de texto completa que o usuário digitar", "Ignora a entrada atual e avança para a próxima solicitação de dados", "Causa uma pausa de um segundo antes de prosseguir com a execução"],
        "correctAnswer": "Consome o caractere de nova linha (\\n) que ficou no buffer de entrada",
        "difficulty": "Médio"
    },
    {
        "question": "Como o método 'salvar' da AlunoRepositoryLista garante que cada aluno tenha um ID único?",
        "options": ["Incrementando uma variável de controle ('proximoId') a cada nova inserção", "Gerando um número de ID aleatório e verificando se ele já existe na lista", "Solicitando que o próprio usuário digite um número de ID que seja único", "Utilizando o hash do objeto Aluno como seu identificador único na lista"],
        "correctAnswer": "Incrementando uma variável de controle ('proximoId') a cada nova inserção",
        "difficulty": "Médio"
    },
    {
        "question": "No método listarTodos de AlunoRepositoryLista, em que ordem os alunos são retornados?",
        "options": ["São retornados em ordem alfabética, com base no nome", "São retornados na mesma ordem em que foram inseridos", "São retornados em ordem crescente, com base no ID", "São retornados em uma ordem completamente aleatória"],
        "correctAnswer": "São retornados em ordem alfabética, com base no nome",
        "difficulty": "Médio"
    },
    {
        "question": "No AlunoRepositoryVetor, o que acontece se o método 'salvar' for chamado quando o vetor já estiver cheio?",
        "options": ["Uma mensagem de erro é exibida e o aluno não é adicionado", "O tamanho do vetor é automaticamente dobrado para comportar mais alunos", "O aluno mais antigo da lista é substituído pelo novo aluno", "Uma exceção do tipo 'ArrayIndexOutOfBoundsException' é lançada"],
        "correctAnswer": "Uma mensagem de erro é exibida e o aluno não é adicionado",
        "difficulty": "Médio"
    },
    {
        "question": "Qual tecnologia é usada na classe Validador para verificar os formatos de CPF e e-mail?",
        "options": ["Expressões Regulares (Regex)", "Algoritmos de Inteligência Artificial", "Funções de Hash criptográficas", "Comparações de String simples e diretas"],
        "correctAnswer": "Expressões Regulares (Regex)",
        "difficulty": "Médio"
    },
    {
        "question": "O que a expressão 'alunos.stream()' faz nas implementações de AlunoRepository?",
        "options": ["Cria um fluxo de dados (Stream) a partir da coleção para realizar operações", "Inicia a transmissão dos dados dos alunos através de uma conexão de rede", "Gera um arquivo de log com os detalhes de cada aluno da coleção", "Comprime a lista de alunos em um formato mais compacto para economizar espaço"],
        "correctAnswer": "Cria um fluxo de dados (Stream) a partir da coleção para realizar operações",
        "difficulty": "Médio"
    },
    {
        "question": "Como o método 'remover' da classe AlunoRepositoryLista funciona?",
        "options": ["Usa o método 'removeIf' da coleção para apagar o aluno com o ID correspondente", "Percorre a lista com um laço 'for' e remove o elemento pelo seu índice numérico", "Cria uma nova lista contendo todos os alunos, exceto aquele a ser removido", "Marca o aluno com um status 'removido' sem de fato tirá-lo da lista"],
        "correctAnswer": "Usa o método 'removeIf' da coleção para apagar o aluno com o ID correspondente",
        "difficulty": "Médio"
    },
    {
        "question": "No método cadastrarAluno do AlunoService, qual verificação é feita imediatamente após validar os campos?",
        "options": ["Verifica se a matrícula informada já está em uso por outro aluno", "Verifica se o nome do aluno já existe no repositório", "Confere se a idade do aluno está dentro de um limite permitido", "Salva o aluno no repositório antes de qualquer outra verificação"],
        "correctAnswer": "Verifica se a matrícula informada já está em uso por outro aluno",
        "difficulty": "Médio"
    },
    {
        "question": "Qual o propósito do bloco 'switch' dentro do método mostrarMenu da AlunoView?",
        "options": ["Direcionar o fluxo do programa para a ação escolhida pelo usuário", "Validar se a entrada do usuário é um número inteiro válido", "Alternar entre as implementações de repositório (Vetor ou Lista)", "Mudar a formatação visual do texto exibido no console"],
        "correctAnswer": "Direcionar o fluxo do programa para a ação escolhida pelo usuário",
        "difficulty": "Médio"
    },
    {
        "question": "Qual a diferença na forma como 'buscarPorId' é implementado em AlunoRepositoryLista e AlunoRepositoryVetor?",
        "options": ["A versão 'Lista' usa a API de Streams e filter, enquanto a 'Vetor' usa um laço 'for'", "A versão 'Lista' é mais rápida para poucos dados e a 'Vetor' para muitos", "Ambas as classes utilizam exatamente a mesma implementação com laço 'for'", "A 'Lista' usa busca binária, que é mais eficiente que a busca linear do 'Vetor'"],
        "correctAnswer": "A versão 'Lista' usa a API de Streams e filter, enquanto a 'Vetor' usa um laço 'for'",
        "difficulty": "Médio"
    },
    {
        "question": "No método removerAluno de AlunoService, como ele informa à AlunoView se a operação foi bem-sucedida?",
        "options": ["Retornando uma String com uma mensagem de sucesso ou de erro", "Retornando um valor booleano, 'true' para sucesso e 'false' para falha", "Lançando uma exceção customizada em caso de falha na remoção", "Imprimindo o resultado da operação diretamente no console"],
        "correctAnswer": "Retornando uma String com uma mensagem de sucesso ou de erro",
        "difficulty": "Médio"
    },
    {
        "question": "Qual é o papel da classe ArrayList importada em AlunoRepositoryLista?",
        "options": ["Fornecer uma estrutura de dados de lista com tamanho dinâmico", "Oferecer métodos estáticos para ordenação de arrays e listas", "Permitir a conversão de uma lista para um vetor (array) de tamanho fixo", "Servir como uma classe de utilitários para operações em listas"],
        "correctAnswer": "Fornecer uma estrutura de dados de lista com tamanho dinâmico",
        "difficulty": "Médio"
    },
    {
        "question": "O que a expressão 'Comparator.comparing(Aluno::getNome)' faz?",
        "options": ["Cria um critério de comparação para ordenar objetos Aluno pelo nome", "Verifica se os nomes de dois objetos Aluno são exatamente iguais", "Converte o nome de um Aluno para letras maiúsculas para comparação", "Remove da lista todos os Alunos que possuem nomes duplicados"],
        "correctAnswer": "Cria um critério de comparação para ordenar objetos Aluno pelo nome",
        "difficulty": "Médio"
    },
    {
        "question": "Como o método listarTodos em AlunoRepositoryVetor lida com as posições vazias (nulas) do array?",
        "options": ["Cria um stream apenas da parte preenchida do vetor, ignorando o resto", "Percorre o vetor inteiro e adiciona uma verificação para pular elementos nulos", "Lança uma NullPointerException se um elemento nulo for encontrado", "Preenche as posições nulas com objetos Aluno vazios antes de retornar"],
        "correctAnswer": "Cria um stream apenas da parte preenchida do vetor, ignorando o resto",
        "difficulty": "Médio"
    },
    {
        "question": "O que o método 'valor.trim().isEmpty()' na classe Validador faz?",
        "options": ["Remove espaços no início/fim e depois verifica se a string resultante está vazia", "Verifica se a string original contém apenas caracteres de espaço em branco", "Corta a string pela metade e verifica se a primeira parte dela está vazia", "Remove todos os espaços da string, inclusive os do meio, e a valida"],
        "correctAnswer": "Remove espaços no início/fim e depois verifica se a string resultante está vazia",
        "difficulty": "Médio"
    },
    {
        "question": "Por que a classe AlunoService recebe um AlunoRepository em seu construtor?",
        "options": ["Para aplicar injeção de dependência e desacoplar a lógica da persistência", "Para garantir que a mesma instância de repositório seja usada em toda a aplicação", "Para criar uma nova tabela no banco de dados quando a classe é instanciada", "Para inicializar o repositório com uma lista de alunos padrão para testes"],
        "correctAnswer": "Para aplicar injeção de dependência e desacoplar a lógica da persistência",
        "difficulty": "Médio"
    },
    {
        "question": "No método 'buscarPorMatricula' de AlunoRepositoryLista, o que 'equalsIgnoreCase' faz?",
        "options": ["Compara duas strings de texto ignorando se as letras são maiúsculas ou minúsculas", "Verifica se duas strings são exatamente idênticas, incluindo maiúsculas/minúsculas", "Testa se a string de matrícula possui um formato de caracteres válido", "Converte a string de matrícula para letras minúsculas antes de comparar"],
        "correctAnswer": "Compara duas strings de texto ignorando se as letras são maiúsculas ou minúsculas",
        "difficulty": "Médio"
    },
    {
        "question": "Qual a primeira validação feita no método 'cadastrarAluno' da AlunoService?",
        "options": ["Verifica se algum campo obrigatório (nome, matrícula, etc.) é nulo ou vazio", "Verifica se o campo de matrícula contém apenas caracteres numéricos", "Valida se o formato do CPF inserido segue o padrão correto", "Confere no repositório se a matrícula informada já existe"],
        "correctAnswer": "Verifica se algum campo obrigatório (nome, matrícula, etc.) é nulo ou vazio",
        "difficulty": "Médio"
    },
    {
        "question": "O que o método 'Integer.parseInt(scanner.nextLine())' na classe Main tenta fazer?",
        "options": ["Converter a linha de texto lida do console em um número do tipo inteiro", "Transformar um número inteiro em uma representação de texto (String)", "Verificar se a linha de texto lida do console contém apenas dígitos", "Formatar um número inteiro com separadores de milhar para exibição"],
        "correctAnswer": "Converter a linha de texto lida do console em um número do tipo inteiro",
        "difficulty": "Médio"
    },
    {
        "question": "Qual a função do 'return Optional.empty()'?",
        "options": ["Indicar que uma busca terminou sem encontrar um resultado válido", "Retornar um erro explícito de 'valor não encontrado' para o chamador", "Devolver uma string de texto vazia como resultado padrão", "Retornar o valor nulo (null) de forma segura e explícita"],
        "correctAnswer": "Indicar que uma busca terminou sem encontrar um resultado válido",
        "difficulty": "Médio"
    },
    {
        "question": "O que a expressão 'Collectors.toList()' faz?",
        "options": ["Agrupa os elementos de um Stream em uma nova instância de List", "Realiza a conversão de um vetor (array) para uma estrutura de List", "Aplica um filtro para remover elementos indesejados de uma List", "Imprime no console cada um dos elementos contidos em uma List"],
        "correctAnswer": "Agrupa os elementos de um Stream em uma nova instância de List",
        "difficulty": "Médio"
    },
    {
        "question": "No método 'atualizar' de AlunoRepositoryLista, o que 'ifPresent' faz?",
        "options": ["Executa um trecho de código somente se o Optional contiver um valor", "Verifica se o aluno está fisicamente presente na instituição", "Apresenta os dados formatados do aluno em uma caixa de diálogo", "Define o status de presença do aluno como verdadeiro no sistema"],
        "correctAnswer": "Executa um trecho de código somente se o Optional contiver um valor",
        "difficulty": "Médio"
    },
    {
        "question": "Por que o método 'remover' de AlunoRepositoryVetor precisa de um segundo laço 'for'?",
        "options": ["Para deslocar os elementos posteriores à posição removida, preenchendo o espaço", "Para confirmar se o aluno foi de fato removido da estrutura do vetor", "Para localizar o índice exato do aluno que precisa ser removido", "Para reordenar todos os elementos do vetor após a operação de remoção"],
        "correctAnswer": "Para deslocar os elementos posteriores à posição removida, preenchendo o espaço",
        "difficulty": "Médio"
    },
    {
        "question": "No método 'atualizarAluno' da AlunoService, qual a primeira coisa que ele faz após validar os novos dados?",
        "options": ["Verifica se o aluno com o ID informado realmente existe no repositório", "Salva as novas informações diretamente no repositório de dados", "Cria um novo objeto Aluno com os dados que foram atualizados", "Confere se a nova matrícula informada já não está em uso por outro aluno"],
        "correctAnswer": "Verifica se o aluno com o ID informado realmente existe no repositório",
        "difficulty": "Médio"
    },
    {
        "question": "O que significa 'implements AlunoRepository' na declaração de uma classe?",
        "options": ["Que a classe assume um 'contrato' de implementar todos os métodos da interface", "Que a classe está herdando todos os atributos e métodos da AlunoRepository", "Que a classe só pode ser instanciada a partir de uma AlunoRepository", "Que a classe está importando os pacotes da interface AlunoRepository"],
        "correctAnswer": "Que a classe assume um 'contrato' de implementar todos os métodos da interface",
        "difficulty": "Médio"
    },
    {
        "question": "Qual o propósito da variável 'totalAlunos' em AlunoRepositoryVetor?",
        "options": ["Manter o controle do número de alunos atualmente no vetor", "Definir a capacidade máxima de alunos que o vetor pode armazenar", "Armazenar o valor do próximo ID de aluno a ser utilizado", "Calcular a média de notas de todos os alunos armazenados"],
        "correctAnswer": "Manter o controle do número de alunos atualmente no vetor",
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
    # (As perguntas de nível Difícil e Extremamente Difícil já possuem um bom equilíbrio no tamanho das alternativas)
    # ... (O resto das perguntas permanece o mesmo) ...
]

# Adicionando as perguntas extras que você forneceu, também revisadas
default_questions.extend([
    {
        "question": "O que o método getIdade() em Aluno.java retorna?",
        "options": ["O valor do atributo idade do aluno", "Um booleano indicando se o aluno é maior de idade", "A data de nascimento formatada do aluno", "Converte a idade do aluno de inteiro para String"],
        "correctAnswer": "O valor do atributo idade do aluno",
        "difficulty": "Fácil"
    },
    {
        "question": "No trecho this.nome = nome; o que o 'this' representa?",
        "options": ["O atributo 'nome' da instância atual da classe", "Um novo objeto que está sendo passado como parâmetro", "Uma chamada a um método estático da própria classe", "O valor do parâmetro 'nome' recebido pelo método"],
        "correctAnswer": "O atributo 'nome' da instância atual da classe",
        "difficulty": "Fácil"
    },
    {
        "question": "Qual o papel da anotação @Override em um método de repositório?",
        "options": ["Indica que o método está implementando um requisito da interface", "Define uma consulta SQL que será executada automaticamente", "Cria um método vazio que deve ser preenchido posteriormente", "Executa o método de forma assíncrona em uma nova thread"],
        "correctAnswer": "Indica que o método está implementando um requisito da interface",
        "difficulty": "Fácil"
    },
    {
        "question": "O construtor AlunoRepositoryVetor(int tamanho) faz o quê?",
        "options": ["Inicializa o vetor de alunos com um tamanho fixo predefinido", "Cria uma lista de alunos que cresce dinamicamente", "Converte um vetor de alunos em uma String formatada", "Gera automaticamente IDs para um número 'tamanho' de alunos"],
        "correctAnswer": "Inicializa o vetor de alunos com um tamanho fixo predefinido",
        "difficulty": "Fácil"
    },
    {
        "question": "O atributo private int indice = 0 em AlunoRepositoryVetor serve para?",
        "options": ["Controlar em qual posição do vetor o próximo aluno será inserido", "Guardar a idade do último aluno que foi cadastrado no sistema", "Definir o tamanho máximo de alunos que o vetor pode comportar", "Contar quantos alunos foram aprovados ou reprovados na disciplina"],
        "correctAnswer": "Controlar em qual posição do vetor o próximo aluno será inserido",
        "difficulty": "Fácil"
    },
    {
        "question": "O que acontece se o nome não for válido em AlunoService?",
        "options": ["O aluno não é adicionado e uma mensagem de erro é retornada", "O aluno é adicionado ao sistema com um nome padrão 'sem nome'", "O aluno inválido é removido de uma lista de pré-cadastro", "A lista de alunos é ordenada para facilitar a busca manual"],
        "correctAnswer": "O aluno não é adicionado e uma mensagem de erro é retornada",
        "difficulty": "Fácil"
    },
    {
        "question": "O que verifica !nome.trim().isEmpty() no Validador?",
        "options": ["Verifica se o nome, após remover espaços, não está vazio", "Confere se o nome é composto apenas por caracteres numéricos", "Testa se o valor da variável 'nome' é estritamente nulo", "Analisa se o nome contém algum tipo de caractere numérico"],
        "correctAnswer": "Verifica se o nome, após remover espaços, não está vazio",
        "difficulty": "Fácil"
    },
    {
        "question": "System.out.println('1 - Cadastrar aluno'); em AlunoView faz o quê?",
        "options": ["Exibe a opção '1 - Cadastrar aluno' no menu do console", "Executa a função para cadastrar um novo aluno no sistema", "Lê os dados do aluno que serão digitados a seguir", "Finaliza a execução do programa com código de saída 1"],
        "correctAnswer": "Exibe a opção '1 - Cadastrar aluno' no menu do console",
        "difficulty": "Fácil"
    },
    {
        "question": "int idade = sc.nextInt(); lê qual tipo de dado?",
        "options": ["Lê o próximo número inteiro da entrada do console", "Lê uma linha inteira de texto (String) do console", "Fecha a conexão do objeto Scanner com a entrada", "Verifica se a próxima entrada é um número ou texto"],
        "correctAnswer": "Lê o próximo número inteiro da entrada do console",
        "difficulty": "Fácil"
    },
    {
        "question": "List<Aluno> alunos = service.listarAlunos(); obtém o quê?",
        "options": ["Uma lista com todos os alunos cadastrados no sistema", "Um novo objeto Aluno com os dados preenchidos", "Um valor booleano indicando se a remoção foi bem-sucedida", "Uma validação dos nomes de todos os alunos na lista"],
        "correctAnswer": "Uma lista com todos os alunos cadastrados no sistema",
        "difficulty": "Fácil"
    },
    {
        "question": "O laço for (Aluno a : alunos) { ... } em AlunoView faz o quê?",
        "options": ["Percorre a lista de alunos para imprimir o nome e a idade de cada um", "Remove da lista todos os alunos que atendem a um critério específico", "Cria novos objetos Aluno com base em uma lista de nomes e idades", "Ordena a lista de alunos em ordem alfabética antes de exibi-la"],
        "correctAnswer": "Percorre a lista de alunos para imprimir o nome e a idade de cada um",
        "difficulty": "Fácil"
    },
    {
        "question": "O comando alunos.add(aluno) faz o quê?",
        "options": ["Adiciona um novo objeto aluno ao final da lista 'alunos'", "Remove um objeto aluno específico da lista 'alunos'", "Substitui toda a lista 'alunos' por uma nova coleção", "Retorna o número total de alunos presentes na lista"],
        "correctAnswer": "Adiciona um novo objeto aluno ao final da lista 'alunos'",
        "difficulty": "Fácil"
    },
    {
        "question": "O comando indice++; faz o quê?",
        "options": ["Avança o valor da variável 'indice' em uma unidade", "Zera o valor do vetor a partir da posição 'indice'", "Cria uma nova instância a partir da classe 'indice'", "Remove um aluno da lista na posição 'indice'"],
        "correctAnswer": "Avança o valor da variável 'indice' em uma unidade",
        "difficulty": "Fácil"
    },
    {
        "question": "No switch de AlunoView, o case 2 chama qual função?",
        "options": ["A função para listar todos os alunos cadastrados", "A função para finalizar a execução do programa", "A função para remover um aluno com base no nome", "A função para cadastrar um novo aluno no sistema"],
        "correctAnswer": "A função para listar todos os alunos cadastrados",
        "difficulty": "Fácil"
    },
    {
        "question": "repository = new AlunoRepositoryLista(); define o quê?",
        "options": ["Que a persistência de dados usará uma lista de tamanho dinâmico", "Que será criado um vetor com um tamanho fixo para os dados", "Que todos os alunos serão removidos da base de dados atual", "Que um aluno padrão será criado para testes da aplicação"],
        "correctAnswer": "Que a persistência de dados usará uma lista de tamanho dinâmico",
        "difficulty": "Fácil"
    },
    {
        "question": "repository = new AlunoRepositoryVetor(10); cria o quê?",
        "options": ["Um repositório que armazena os alunos em um vetor de 10 posições", "Uma lista de alunos que pode crescer até o limite de 10 mil", "Um arquivo de texto chamado 'alunos.txt' com 10 linhas", "Uma conexão com um banco de dados SQL com um pool de 10 conexões"],
        "correctAnswer": "Um repositório que armazena os alunos em um vetor de 10 posições",
        "difficulty": "Fácil"
    },
    {
        "question": "O bloco default em um switch faz o quê?",
        "options": ["É executado se nenhuma das outras opções (case) for atendida", "Define o valor padrão para todas as variáveis dentro do switch", "Sempre repete a última ação executada pelo usuário no menu", "Cria uma variável temporária para armazenar a opção do usuário"],
        "correctAnswer": "É executado se nenhuma das outras opções (case) for atendida",
        "difficulty": "Fácil"
    },
    {
        "question": "new AlunoView().menu(); em Main.java faz o quê?",
        "options": ["Cria uma nova instância de AlunoView e chama o método menu", "Finaliza o programa e exibe o menu de opções de saída", "Cria um novo aluno e o adiciona ao menu de visualização", "Valida a idade de todos os alunos antes de exibir o menu"],
        "correctAnswer": "Cria uma nova instância de AlunoView e chama o método menu",
        "difficulty": "Fácil"
    },
    {
        "question": "O método adicionar em AlunoRepositoryVetor faz o quê?",
        "options": ["Insere um aluno na próxima posição livre e incrementa o índice", "Remove um aluno do vetor e reorganiza os elementos restantes", "Ordena todos os alunos no vetor com base no nome ou no ID", "Cria uma lista dinâmica a partir do conteúdo do vetor atual"],
        "correctAnswer": "Insere um aluno na próxima posição livre e incrementa o índice",
        "difficulty": "Fácil"
    },
    {
        "question": "boolean continuar = true em AlunoView significa?",
        "options": ["É uma variável de controle para manter o loop do menu em execução", "Conta o número de alunos que continuam ativos no sistema", "Cria um novo aluno com o status de 'continuar' como verdadeiro", "Declara um índice para percorrer a lista de alunos no menu"],
        "correctAnswer": "É uma variável de controle para manter o loop do menu em execução",
        "difficulty": "Fácil"
    },
    {
        "question": "O laço while (continuar) faz o quê?",
        "options": ["Executa o bloco de código repetidamente enquanto 'continuar' for verdadeiro", "Executa o bloco de código apenas uma única vez e depois para", "Nunca executa o bloco de código, pois a condição é sempre falsa", "Encerra o programa se a variável 'continuar' for verdadeira"],
        "correctAnswer": "Executa o bloco de código repetidamente enquanto 'continuar' for verdadeiro",
        "difficulty": "Fácil"
    },
    {
        "question": "O contrato Aluno buscarPorNome(String nome); define o quê?",
        "options": ["Um método que deve buscar e retornar um aluno com base no nome", "Um método que remove um aluno do repositório usando o nome", "Um método que retorna sempre uma lista vazia de alunos", "Um método que converte o nome de um aluno para maiúsculas"],
        "correctAnswer": "Um método que deve buscar e retornar um aluno com base no nome",
        "difficulty": "Fácil"
    },
    {
        "question": "O método buscarAlunoPorNome em Service retorna?",
        "options": ["O objeto Aluno correspondente ao nome buscado, se existir", "Um valor booleano indicando se a remoção foi bem-sucedida", "Um novo objeto Aluno com o nome e a idade padrão", "Uma validação se a idade do aluno encontrado é válida"],
        "correctAnswer": "O objeto Aluno correspondente ao nome buscado, se existir",
        "difficulty": "Fácil"
    },
    {
        "question": "System.out.println('Digite o nome para buscar:'); faz o quê?",
        "options": ["Exibe uma mensagem no console instruindo o usuário", "Lê o nome que o usuário digitará em seguida no console", "Busca automaticamente por um aluno com o nome 'buscar'", "Finaliza o programa e exibe uma mensagem de despedida"],
        "correctAnswer": "Exibe uma mensagem no console instruindo o usuário",
        "difficulty": "Fácil"
    },
    {
        "question": "service.buscarAlunoPorNome(nome); faz o quê?",
        "options": ["Chama a camada de serviço para procurar um aluno pelo nome", "Remove um aluno do serviço usando o nome como critério", "Cria uma nova lista de alunos a partir do serviço", "Zera a idade de um aluno encontrado através do serviço"],
        "correctAnswer": "Chama a camada de serviço para procurar um aluno pelo nome",
        "difficulty": "Fácil"
    },
    {
        "question": "O if (encontrado != null) faz o quê?",
        "options": ["Executa um bloco de código apenas se um aluno foi encontrado", "Sempre imprime os dados do aluno, mesmo que seja nulo", "Remove o aluno se ele foi encontrado na base de dados", "Cria um novo aluno se a busca não retornar resultado"],
        "correctAnswer": "Executa um bloco de código apenas se um aluno foi encontrado",
        "difficulty": "Fácil"
    },
    {
        "question": "O laço for em AlunoRepositoryLista com equals(nome) faz o quê?",
        "options": ["Percorre a lista e retorna o aluno cujo nome corresponde ao buscado", "Cria um novo aluno na lista com o nome passado como parâmetro", "Remove da lista todos os alunos que não possuem o nome buscado", "Ordena a lista de alunos com base no nome fornecido"],
        "correctAnswer": "Percorre a lista e retorna o aluno cujo nome corresponde ao buscado",
        "difficulty": "Fácil"
    },
    {
        "question": "O for em AlunoRepositoryVetor até indice faz o quê?",
        "options": ["Percorre as posições preenchidas do vetor em busca de um aluno", "Adiciona um novo aluno em cada posição do vetor até o índice", "Apaga todos os elementos do vetor até a posição 'indice'", "Cria uma nova lista a partir dos elementos do vetor"],
        "correctAnswer": "Percorre as posições preenchidas do vetor em busca de um aluno",
        "difficulty": "Fácil"
    },
    {
        "question": "O case 3 em AlunoView executa?",
        "options": ["A funcionalidade de buscar um aluno pelo seu nome", "A funcionalidade de remover um aluno do sistema", "A funcionalidade de listar todos os alunos cadastrados", "A opção de sair do sistema e encerrar a aplicação"],
        "correctAnswer": "A funcionalidade de buscar um aluno pelo seu nome",
        "difficulty": "Fácil"
    },
    {
        "question": "O case 0 em AlunoView faz?",
        "options": ["Altera a variável de controle para encerrar o loop do menu", "Reinicia o menu principal, mostrando as opções novamente", "Executa a funcionalidade de cadastrar um novo aluno", "Chama o método para listar todos os alunos cadastrados"],
        "correctAnswer": "Altera a variável de controle para encerrar o loop do menu",
        "difficulty": "Fácil"
    }
])
TIME_PER_QUESTION, WINNING_SCORE, PENALTY_POINTS = 30, 120, 5

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