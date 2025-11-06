# Análise de Riscos OWASP - Projeto Makerpass

---

## Risco 1 – A01 – Controle de Acesso Quebrado

### Descrição
> Esse risco se caracteriza pelo acesso de usuários não autorizados a recursos ou dados que deveriam estar restritos. Isso geralmente acontece por falhas na verificação de permissões no backend ou por endpoints sem autenticação adequada.

### Evidência no projeto
No meu projeto Makerpass, existem endpoints Django que não utilizam o `LoginRequiredMixin` ou decoradores de autenticação como `@login_required`, `@permission_required`.

Durante a execução do Vulture, foi identificado que `LoginRequiredMixin` e `csrf_exempt` estavam importados mas não utilizados em no arquivo de views do projeto, indicando que algumas views podem estar acessíveis sem autenticação.

### Justificativa
Se endpoints públicos permitirem ações administrativas, qualquer usuário pode executar operações indevidas, comprometendo a integridade dos dados do sistema.

### Como resolver
1. Adicionar `LoginRequiredMixin` a todas as classes de views que exigem autenticação.
2. Usar o decorator `@login_required` quando necessário.
3. Revisar os controles de permissão, garantindo que rotas críticas exigem login.

---

## Risco 2 – A09 - Falhas de Registro e Monitoramento de Segurança

### Descrição
> Ocorre quando o sistema não registra tentativas suspeitas ou não possui alertas para atividades anômalas. Isso impede a detecção e resposta rápida a incidentes.

### Evidência no projeto
Durante uma breve análise, não identifiquei nenhuma configuração de logging de segurança no meu projeto Django (`LOGGING` no `settings.py`) nem uso explícito de logs nas views para registrar erros ou tentativas de acesso inválidas.

### Justificativa
Sem logs adequados, ataques de força bruta, acessos indevidos ou falhas de autenticação podem passar despercebidos.

### Como resolver
1. Configurar o sistema de logs do Django em `settings.py`.
2. Registrar tentativas de login falhas e acessos negados.
3. Integrar a aplicação com ferramentas de monitoramento (ex: Sentry, Grafana ou ELK Stack).

---

## Risco 3 – A04 – Design Inseguro

### Descrição
> O risco de design inseguro refere-se a falhas conceituais ou arquitetônicas no projeto do sistema que comprometem sua segurança, independentemente da implementação do código.
>
> Diferente de bugs de programação, o Insecure Design está relacionado à ausência de princípios de segurança desde a concepção da aplicação, como:
>
> * Falta de modelagem de ameaças;
> * Ausência de políticas de segurança robustas;
> * Lógica de negócio vulnerável a abuso;
> * Falta de segregação de responsabilidades e camadas.

### Evidência no projeto
Durante a análise no meu projeto, foram observadas algumas evidências de design potencialmente inseguro:

1. **Ausência de camadas claras de autorização e validação:**
   O uso não aplicado de `LoginRequiredMixin` e `csrf_exempt` indica que a aplicação pode permitir requisições sem autenticação ou sem proteção contra CSRF, o que demonstra falha no design de segurança da aplicação.

### Como resolver
1. **Aplicar o princípio de “Security by Design”:**
   Projetar a aplicação com segurança em mente desde o início, definindo políticas de autenticação, autorização e validação antes da implementação.

2. **Criar uma camada de serviço (Service Layer):**
   Separar a lógica de negócios da camada de apresentação, deixando as views responsáveis apenas por receber e devolver respostas HTTP. Isso reduz a complexidade e o risco de vulnerabilidades em endpoints.

3. **Adicionar modelagem de ameaças (Threat Modeling):**
   Mapear os fluxos de dados e identificar onde informações sensíveis podem ser expostas ou manipuladas indevidamente.

4. **Utilizar middlewares para segurança padronizada:**
   Centralizar autenticação, logs e auditoria em middlewares para evitar repetição e inconsistência de segurança entre diferentes rotas.

5. **Proteger endpoints críticos com regras de segurança adicionais:** Implementar:
   * Tokens de verificação;
   * Rate limiting;
   * Proteções contra CSRF em todas as rotas com `POST/PUT/DELETE`.