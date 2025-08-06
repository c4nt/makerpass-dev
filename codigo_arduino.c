#include <SoftwareSerial.h>
#include <Adafruit_Fingerprint.h>
#include <EEPROM.h>

// ==============================================
// CONFIGURAÇÕES DE HARDWARE E MEMÓRIA
// ==============================================
#define BUTTON_PIN        4
#define RELAY_PIN         8
#define MAX_USERS         25
#define MATRICULA_LENGTH  20
#define NOME_LENGTH       20

#define ADDR_MATRICULAS   0
#define ADDR_NOMES        (ADDR_MATRICULAS + (MAX_USERS * MATRICULA_LENGTH))
#define ADDR_ACTIONS      (ADDR_NOMES + (MAX_USERS * NOME_LENGTH))
#define ADDR_NEXT_ID      (ADDR_ACTIONS + (MAX_USERS / 8) + 1)

SoftwareSerial fingerSerial(2, 3);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&fingerSerial);
int nextID = 1;

// ==============================================
// PROTÓTIPOS DE FUNÇÃO
// ==============================================
void abrirPorta();
void cadastrarDigital();
void listarAcessos();
void menuAlteracao(int id); // ALTERADO: Função principal para alterações
void removerAcesso(int id);
void apagarTodosOsAcessos();

// EEPROM
void salvarMatricula(int id, const String &matricula);
String getMatricula(int id);
void salvarNome(int id, const String &nome);
String getNome(int id);
void salvarUltimoID(int id);
void carregarUltimoID();
bool getLastAction(int id);
void saveLastAction(int id, bool action);
uint8_t getFingerprintEnroll(int id);
int getFingerprintID();

// ==============================================
// SETUP INICIAL
// ==============================================
void setup() {
  Serial.begin(115200);
  fingerSerial.begin(57600);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  Serial.println("Iniciando sensor biometrico...");
  if (finger.verifyPassword()) {
    Serial.println("✅ Sensor encontrado!");
  } else {
    Serial.println("⚠️ ERRO: Sensor NAO encontrado!");
    while (1);
  }

  carregarUltimoID();
  Serial.println("Comandos via Serial:");
  Serial.println("  cadastrar       -> cadastra nova digital");
  Serial.println("  banco de dados  -> lista todos os cadastros");
  Serial.println("  alterar id N    -> altera dados do ID N"); // ALTERADO: Descrição do comando
  Serial.println("  apagar id N     -> apaga acesso do ID N");
  Serial.println("  apagar          -> apaga TUDO");
}

// ==============================================
// LOOP PRINCIPAL
// ==============================================
void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.equalsIgnoreCase("apagar")) {
      apagarTodosOsAcessos();
    } else if (cmd.equalsIgnoreCase("banco de dados")) {
      listarAcessos();
    } else if (cmd.startsWith("apagar id ")) {
      int idCmd = cmd.substring(10).toInt();
      if (idCmd > 0 && idCmd <= MAX_USERS) removerAcesso(idCmd);
      else Serial.println("⚠️ ID invalido!");
    } else if (cmd.startsWith("alterar id ")) { // ALTERADO: Chama o novo menu
      int idCmd = cmd.substring(11).toInt();
      if (idCmd > 0 && idCmd <= MAX_USERS) menuAlteracao(idCmd);
      else Serial.println("⚠️ ID invalido!");
    } else if (cmd.equalsIgnoreCase("cadastrar")) {
      cadastrarDigital();
    }
  }

  int id = getFingerprintID();
  if (id > 0) {
    String matricula = getMatricula(id);
    if (matricula.length() == 0) {
      Serial.println("🔒 Digital desconhecida");
    } else {
      Serial.print("MATRICULA:");
      Serial.println(matricula);
      abrirPorta();
      bool lastAction = getLastAction(id);
      saveLastAction(id, !lastAction);
    }
    delay(2000);
  }
}

// ==============================================
// FUNÇÕES DE COMANDOS E ALTERAÇÃO
// ==============================================

// NOVO: Menu interativo para alterar matrícula ou nome
void menuAlteracao(int id) {
  String matricula = getMatricula(id);
  if (matricula.length() == 0) {
    Serial.println("⚠️ Este ID nao possui cadastro.");
    return;
  }

  Serial.println("--------------------------");
  Serial.print("Editando ID: ");
  Serial.println(id);
  Serial.print("Matrícula Atual: ");
  Serial.println(matricula);
  Serial.print("Nome Atual: ");
  Serial.println(getNome(id));
  Serial.println("--------------------------");
  Serial.println("O que deseja alterar?");
  Serial.println("  [1] Matrícula");
  Serial.println("  [2] Nome");
  Serial.println("  [Qualquer outra tecla] Cancelar");

  // Espera pela resposta do usuário (1 ou 2)
  while (!Serial.available());
  char escolha = Serial.read();

  // ***** A CORREÇÃO ESTÁ AQUI *****
  // Limpa qualquer dado residual do buffer (como o '\n' do Enter)
  // antes de prosseguir para a próxima leitura.
  while (Serial.available()) {
    Serial.read();
  }
  // **********************************

  if (escolha == '1') {
    Serial.println("Digite a NOVA MATRICULA e pressione Enter:");
    // Agora o programa vai esperar por uma nova entrada
    while (!Serial.available());
    String novaMatricula = Serial.readStringUntil('\n');
    novaMatricula.trim();
    salvarMatricula(id, novaMatricula);
    Serial.println("✅ Matrícula alterada com sucesso!");

  } else if (escolha == '2') {
    Serial.println("Digite o NOVO NOME e pressione Enter:");
    // Agora o programa vai esperar por uma nova entrada
    while (!Serial.available());
    String novoNome = Serial.readStringUntil('\n');
    novoNome.trim();
    salvarNome(id, novoNome);
    Serial.println("✅ Nome alterado com sucesso!");

  } else {
    Serial.println("❌ Operação cancelada.");
  }
  Serial.println("--------------------------");
}

// NOVO: Função para encontrar o primeiro slot de ID vazio.
int encontrarProximoIdLivre() {
  for (int id = 1; id <= MAX_USERS; id++) {
    // Se a matrícula de um ID estiver vazia, significa que o slot está livre.
    if (getMatricula(id).length() == 0) {
      return id; // Retorna o primeiro ID livre encontrado.
    }
  }
  return -1; // Retorna -1 se não houver nenhum slot livre.
}

void cadastrarDigital() {
  
  nextID = encontrarProximoIdLivre();

  Serial.print("📌 Cadastrando ID: ");
  Serial.println(nextID);
  
  uint8_t res = getFingerprintEnroll(nextID);
  if (res != FINGERPRINT_OK) {
    Serial.println("❌ Falha no cadastro. Tente novamente.");
    return;
  }

  Serial.println("Digite a MATRICULA do usuario:");
  while (!Serial.available());
  String matricula = Serial.readStringUntil('\n');
  matricula.trim();
  if (matricula.length() == 0) matricula = "Matricula" + String(nextID);

  Serial.println("Digite o NOME do usuario:");
  while (!Serial.available());
  String nome = Serial.readStringUntil('\n');
  nome.trim();
  if (nome.length() == 0) nome = "Usuario " + String(nextID);

  salvarMatricula(nextID, matricula);
  salvarNome(nextID, nome);
  salvarUltimoID(nextID);

  Serial.println("✅ Cadastro concluido!");
  nextID++;
}


void listarAcessos() {
  Serial.println("--- BANCO DE DADOS ---");
  bool encontrouAlguem = false;
  for (int i = 1; i <= MAX_USERS; i++) {
    String matricula = getMatricula(i);
    if (matricula.length()) {
      encontrouAlguem = true;
      String nome = getNome(i);
      
      Serial.print("ID ");
      Serial.print(i);
      Serial.print(" | Matrícula: ");
      Serial.print(matricula);
      Serial.print(" | Nome: ");
      Serial.println(nome);
    }
  }
  if (!encontrouAlguem) {
    Serial.println("Nenhum usuario cadastrado.");
  }
  Serial.println("----------------------");
}

void removerAcesso(int id) {
  Serial.print("🗑️ Removendo ID ");
  Serial.print(id);
  Serial.println("...");
  if (finger.deleteModel(id) == FINGERPRINT_OK) {
    salvarMatricula(id, "");
    salvarNome(id, "");
    Serial.println("✅ Removido!");
  } else {
    Serial.println("⚠️ Erro ao remover.");
  }
}

void apagarTodosOsAcessos() {
  Serial.println("⚠️ Apagando TODOS os acessos...");
  for (int i = 1; i <= MAX_USERS; i++) {
    finger.deleteModel(i);
    salvarMatricula(i, "");
    salvarNome(i, "");
  }
  salvarUltimoID(1);
  Serial.println("✅ Todos os dados foram apagados!");
}

// ==============================================
// FUNÇÕES EEPROM
// ==============================================
void salvarNome(int id, const String &nome) {
  int addr = ADDR_NOMES + ((id - 1) * NOME_LENGTH);
  for (int i = 0; i < NOME_LENGTH; i++) {
    EEPROM.write(addr + i, i < nome.length() ? nome[i] : 0);
  }
}

String getNome(int id) {
  int addr = ADDR_NOMES + ((id - 1) * NOME_LENGTH);
  char buf[NOME_LENGTH];
  for (int i = 0; i < NOME_LENGTH; i++) {
    buf[i] = EEPROM.read(addr + i);
  }
  return String(buf);
}

void salvarMatricula(int id, const String &matricula) {
  int addr = ADDR_MATRICULAS + ((id - 1) * MATRICULA_LENGTH);
  for (int i = 0; i < MATRICULA_LENGTH; i++) {
    EEPROM.write(addr + i, i < matricula.length() ? matricula[i] : 0);
  }
}

String getMatricula(int id) {
  int addr = ADDR_MATRICULAS + ((id - 1) * MATRICULA_LENGTH);
  char buf[MATRICULA_LENGTH];
  for (int i = 0; i < MATRICULA_LENGTH; i++) {
    buf[i] = EEPROM.read(addr + i);
  }
  return String(buf);
}

void salvarUltimoID(int id) {
  EEPROM.write(ADDR_NEXT_ID, id);
}

void carregarUltimoID() {
  nextID = EEPROM.read(ADDR_NEXT_ID);
  if (nextID < 1 || nextID > MAX_USERS) nextID = 1;
}

bool getLastAction(int id) {
  int addr = ADDR_ACTIONS + ((id - 1) / 8);
  byte b = EEPROM.read(addr);
  return bitRead(b, (id - 1) % 8);
}

void saveLastAction(int id, bool action) {
  int addr = ADDR_ACTIONS + ((id - 1) / 8);
  byte b = EEPROM.read(addr);
  bitWrite(b, (id - 1) % 8, action);
  EEPROM.write(addr, b);
}

// --- Funções restantes (sem alterações) ---

void abrirPorta() {
  Serial.println("🚪 Acionando a porta...");
  digitalWrite(RELAY_PIN, HIGH);
  delay(500);
  digitalWrite(RELAY_PIN, LOW);
}

int getFingerprintID() {
  if (finger.getImage() != FINGERPRINT_OK) return -1;
  if (finger.image2Tz() != FINGERPRINT_OK) return -1;
  if (finger.fingerSearch() == FINGERPRINT_OK) {
    return finger.fingerID;
  }
  return -1;
}

uint8_t getFingerprintEnroll(int id) {
  int p;
  Serial.println("👉 Coloque o dedo...");
  while ((p = finger.getImage()) != FINGERPRINT_OK) {
    if (p == FINGERPRINT_NOFINGER) delay(100);
    else return p;
  }
  Serial.println("📸 Capturado!");
  if (finger.image2Tz(1) != FINGERPRINT_OK) return p;
  Serial.println("✋ Remova e reinsira o dedo...");
  delay(2000);
  while (finger.getImage() != FINGERPRINT_NOFINGER);
  while (finger.getImage() != FINGERPRINT_OK);
  if (finger.image2Tz(2) != FINGERPRINT_OK) return p;
  if (finger.createModel() != FINGERPRINT_OK) return p;
  return finger.storeModel(id);
}