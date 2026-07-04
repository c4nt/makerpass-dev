
# makerpass 🚪🤖

> Sistema inteligente de controle de frequência e gerenciamento de acesso automatizado para o laboratório **CNATMAKER**.

---

## 📋 Sobre o Projeto

O **makerpass** é uma solução de hardware e software desenvolvida para automatizar o controle de acesso e monitorar a frequência dos usuários no laboratório **CNATMAKER**. Através de um ecossistema integrado baseado no framework Django e microcontroladores, o sistema garante segurança, rastreabilidade e praticidade no gerenciamento diário do espaço maker.

Atualmente, o projeto encontra-se em uma **fase ativa de modernização e atualização**, aprimorando suas funcionalidades legadas e preparando a infraestrutura para recursos avançados de automação e visão computacional.

---

## 🛠️ Arquitetura do Sistema e Hardware

O projeto utiliza uma abordagem híbrida, combinando o poder de processamento de um mini-computador com a eficiência de microcontroladores para o controle de periféricos físicos:

* **Servidor Central (Raspberry Pi 5):** Hospeda a aplicação web e API construídas em **Django**. É o cérebro do sistema, responsável pela lógica de negócios, persistência de dados, autenticação de requisições e fornecimento do painel administrativo.
* **Módulo de Autenticação (Sensor Biométrico):** Realiza a leitura e validação das impressões digitais dos usuários de forma local e rápida, enviando os dados de identificação para o servidor central.
* **Atuador de Acesso (Arduino):** Controla a parte física de automação do ambiente. Recebe os comandos validados vindos do Raspberry Pi para coordenar a abertura e o fechamento do motor elétrico da porta de acesso.

---

## 🚀 Tecnologias Utilizadas

### Software
* **Python 3** (Linguagem base)
* **Django Framework** (Camada de backend, ORM e painel administrativo)
* **SQLite / PostgreSQL** (Armazenamento de logs de acesso e perfis de usuários)

### Hardware & Firmware
* **Raspberry Pi 5** (Host de processamento e servidor local)
* **Arduino** (Interface de controle e acionamento de relés/motores)
* **Sensor Biométrico Óptico** (Leitura de impressões digitais)
* **C/C++ (Arduino Wiring)** (Programação de firmware dos microcontroladores)

---

## ✨ Funcionalidades Atuais

- [x] **Cadastro e Gestão de Usuários:** Interface administrativa intuitiva via Django Admin para gerenciar perfis, permissões e dados cadastrais.
- [x] **Validação Biométrica Dinâmica:** Identificação precisa de usuários cadastrados com tempos de resposta otimizados.
- [x] **Acionamento Físico de Portas:** Automação de travamento e destravamento da entrada por meio do motor controlado pelo Arduino.
- [x] **Registro de Frequência em Tempo Real:** Geração automática de logs de entrada e saída (timestamps) para relatórios de auditoria e ocupação do laboratório.

---

## 🗺️ Roadmap de Evolução (Próxima Fase)

O **makerpass** está sendo preparado para uma nova onda de inovação tecnológica. As metas estabelecidas para o próximo ciclo de desenvolvimento são:

- [ ] **Implementação de Reconhecimento Facial:** Integração de bibliotecas de visão computacional (como OpenCV e modelos de Deep Learning) para permitir um fluxo de acesso alternativo, seguro e *hands-free*.
- [ ] **Integração com Sistema de Gestão Geral:** Conectar a API do makerpass a uma plataforma de gestão institucional centralizada para unificar o banco de dados de membros e sincronizar relatórios de frequência.
- [ ] **Interface Web do Usuário (Dashboard):** Criação de um painel visual moderno para visualização de métricas de uso do laboratório, horários de pico e status dos dispositivos em tempo real.

---

## 🔧 Configuração e Instalação (Desenvolvimento)

### Pré-requisitos
* Python 3.10 ou superior instalado no Raspberry Pi / ambiente local.
* Arduino IDE (para carregar o firmware no microcontrolador).
* Git configurado.

### 1. Clonando o Repositório
```bash
git clone [https://github.com/seu-usuario/makerpass.git](https://github.com/seu-usuario/makerpass.git)
cd makerpass