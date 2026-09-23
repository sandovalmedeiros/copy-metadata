# Spec: Interface Desktop (janela principal e orquestração do fluxo)

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-09-23
**Reviewers:** N/A — pipeline Reversa

---

## 1. Resumo

🟡 Componente de interface gráfica (Tkinter) que orquestra todo o fluxo do app: seleção de origem, arquivo-alvo e destino por diálogos nativos, execução do lote com barra de progresso e cancelamento, e exibição do relatório final. Responsável ainda pelo empacotamento da aplicação em executável único `.exe` para Windows.

---

## 2. Contexto e Motivação

**Problema:**
🟡 Os componentes internos (scanner, motor, relatório) só entregam valor se o técnico puder operá-los sem linha de comando — a persona não é programadora e a demanda pede explicitamente seleção "navegando através da interface".

**Evidências:**
🟡 Demanda Geonetwork.pdf, passo 3: "O usuário vai indicar qual o nome do arquivo .xml que será alvo da cópia navegando através da interface". Decisão de entrevista: stack Python + GUI desktop (Tkinter sugerido), Windows, empacotável em `.exe`. PRD seção 4: janela com seletores, progresso e relatório.

**Por que agora:**
🟡 É a face do produto — sem a interface, a demanda não é atendida para o público-alvo definido.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Permitir que o usuário complete 100% do fluxo (origem → alvo → destino → executar → relatório) só com mouse e diálogos nativos
- [ ] G-02: 🟡 Manter a janela responsiva durante o lote, com progresso visível e cancelamento atendendo em < 2 s
- [ ] G-03: 🟡 Distribuir o app como um único `.exe` executável em Windows 10/11 sem Python instalado

**Métricas de sucesso:**
| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Passos do fluxo concluídos sem linha de comando | 0% (manual) | 100% | entrega do MVP |
| 🟡 Tempo de inicialização do app | n/d | < 3 s | entrega do MVP |
| 🟡 Atraso entre cancelar e efetiva parada | n/d | < 2 s | entrega do MVP |

---

## 4. Non-Goals (Fora do Escopo)

- NG-01: 🟡 Não implementa lógica de varredura, cópia ou consolidação — consome os componentes internos
- NG-02: 🟡 Não oferece modo linha de comando (CLI) nesta versão
- NG-03: 🟡 Não persiste preferências entre execuções (lembrar última origem/destino fica para versão futura)
- NG-04: 🟡 Não suporta temas visuais customizáveis ou multi-idioma além do definido em OQ-01

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 Técnico de Geoprocessamento — nível técnico intermediário, acostumado com aplicativos Windows de produtividade; opera o app do início ao fim sem apoio.
**Usuário secundário:** 🟡 Nenhum.

**Jornada atual (sem a feature):**
🟡 1. Abre o Windows Explorer; 2. navega manualmente a árvore de exportação; 3. copia e renomeia arquivos um a um.

**Jornada futura (com a feature):**
🟡 1. Abre o app; 2. seleciona origem, arquivo-alvo e destino; 3. executa, acompanha o progresso e lê o relatório.

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | 🟡 O usuário deve selecionar a pasta de origem por meio de diálogo nativo de pastas | Must | 🟡 Campo origem preenchido com path escolhido no diálogo |
| RF-02 | 🟡 O usuário deve selecionar o arquivo-alvo `.xml` por meio de diálogo nativo de arquivos filtrando por `.xml` | Must | 🟡 Diálogo abre com filtro `*.xml`; campo alvo preenchido com o path selecionado |
| RF-03 | 🟡 O usuário deve selecionar a pasta de destino por meio de diálogo nativo de pastas | Must | 🟡 Campo destino preenchido com path escolhido no diálogo |
| RF-04 | 🟡 O sistema deve habilitar o botão executar somente com os três campos preenchidos e válidos | Must | 🟡 Botão permanece desabilitado enquanto qualquer campo está vazio ou inválido |
| RF-05 | 🟡 O usuário deve iniciar a execução do lote por botão dedicado | Must | 🟡 Clique em executar disparar scanner + motor na sequência |
| RF-06 | 🟡 O sistema deve exibir barra de progresso com contagem (N de M pastas) durante o lote | Must | 🟡 Progresso atualiza a cada pasta concluída até M |
| RF-07 | 🟡 O usuário deve cancelar a execução em andamento por botão dedicado | Must | 🟡 Clique em cancelar interrompe em < 2 s; relatório parcial exibido |
| RF-08 | 🟡 O sistema deve exibir o relatório de execução na própria janela ao término | Must | 🟡 Término em qualquer condição atualiza a área de relatório |
| RF-09 | 🟡 O sistema deve validar os paths ao executar, com mensagem específica para origem inexistente/inacessível | Must | 🟡 Origem inválida produz mensagem nomeando o problema; nada é copiado |
| RF-10 | 🟡 O sistema deve desabilitar os controles de configuração durante a execução | Must | 🟡 Durante o lote, seletores e executar ficam desabilitados; apenas cancelar ativo |
| RF-11 | 🟡 O usuário deve executar a aplicação a partir de um único `.exe` sem Python instalado | Must | 🟡 `.exe` gerado por empacotamento abre e opera todas as funções em máquina limpa |

### 6.2 Fluxo Principal (Happy Path)

1. O usuário abre o app e vê a janela com três seletores vazios e botão executar desabilitado
2. O usuário seleciona origem, arquivo-alvo `.xml` e destino nos diálogos nativos
3. O botão executar é habilitado; o usuário aciona executar
4. O sistema varre a origem, copia em lote e atualiza a barra de progresso (N de M)
5. Resultado: relatório exibido na janela com contagens e lista de problemas

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — cancelamento:**
1. Durante o lote, o usuário aciona cancelar
2. O sistema para em < 2 s, mantendo o que foi copiado
3. O relatório parcial é exibido; os controles são reabilitados

**Fluxo Alternativo B — validação falha antes de executar:**
1. Origem aponta para share indisponível
2. O sistema exibe mensagem específica na validação
3. Nada é copiado; o app permanece utilizável para corrigir o path

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| RNF-01 | Inicialização | 🟡 < 3 s até a janela utilizável | 🟡 empacotamento one-dir favorece startup |
| RNF-02 | Responsividade durante o lote | 🟡 janela nunca congelada; UI em thread dedicada | 🟡 cópia roda fora da thread de eventos |
| RNF-03 | Compatibilidade | 🟡 Windows 10 e 11, 64 bits | 🟡 ambiente corporativo alvo |
| RNF-04 | Dependências | 🟡 apenas Tkinter + stdlib em runtime | 🟡 zero dependência externa de pacotes |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 janela única do app; diálogos nativos do Windows (pastas e arquivos).

**Comportamento esperado:**
🟡 Janela com três linhas de seleção (origem, arquivo-alvo, destino), cada uma com campo texto somente-leitura + botão "Procurar"; abaixo, botões Executar e Cancelar; barra de progresso com contagem; área de relatório rolável. Durante o lote, seletores e executar desabilitados; cancelar ativo; ao término, controles reabilitados e relatório atualizado.

**Estados da UI:**
- Estado vazio: 🟡 três campos vazios; executar desabilitado; área de relatório com orientação de uso
- Estado de carregamento: 🟡 barra de progresso N de M; cursor de ocupado; cancelar habilitado
- Estado de erro: 🟡 mensagem específica na área de status (origem inválida, destino sem permissão); app permanece aberto e corrigível
- Estado de sucesso: 🟡 relatório com resumo e problemas em destaque; novo lote pode ser iniciado

---

## 9. Modelo de Dados

**Entidades novas ou modificadas (em memória):**

```
EstadoTela {
  origem: texto | vazio
  arquivo_alvo: texto | vazio
  destino: texto | vazio
  executando: booleano
  progresso_atual: número
  progresso_total: número
}
```

**Migrações necessárias:** Não — sem persistência.

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|-------------|------|------------------------|
| 🟡 scanner-de-pastas | Obrigatória | 🟡 execução aborta com erro de contrato; app continua aberto |
| 🟡 motor-de-copia-renomeacao | Obrigatória | 🟡 idem |
| 🟡 relatorio-de-execucao | Obrigatória | 🟡 término sem relatório; app sinaliza falha |
| 🟡 Tkinter + stdlib | Obrigatória | 🟡 app não inicia; distribuição Windows com Python inclui Tkinter |
| 🟡 PyInstaller (build, não runtime) | Obrigatória | 🟡 sem `.exe`; alternativa é rodar via Python instalado |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---------|---------|----------------------|
| EC-01: 🟡 campos incompletos | 🟡 usuário tenta preparar execução sem os três paths | 🟡 botão executar permanece desabilitado com dica do que falta |
| EC-02: 🟡 origem inacessível na validação | 🟡 share fora do ar ou sem permissão | 🟡 mensagem específica de falha/indisponibilidade; nada é copiado; app utilizável |
| EC-03: 🟡 falha inesperada durante o lote | 🟡 exceção não prevista no motor/scanner | 🟡 mensagem de erro com opção de ver o relatório parcial; app não fecha sozinho |
| EC-04: 🟡 fechamento da janela durante execução | 🟡 usuário clica no X com lote em andamento | 🟡 confirmação antes de encerrar; lote cancelado de forma ordenada |
| EC-05: 🟡 `.exe` bloqueado por antivírus corporativo | 🟡 política de execução no desktop | 🟡 instrução de liberação/documentação anexa; alternativa de execução via Python |

---

## 12. Segurança e Privacidade

- **Autenticação:** 🟡 nenhuma — aplicativo local de desktop
- **Autorização:** 🟡 operações limitadas às permissões do usuário Windows logado
- **Dados sensíveis:** 🟡 nenhum identificado — a UI manipula apenas paths de rede/locais e resultados
- **Auditoria:** 🟡 nenhuma além do relatório de execução exportável

---

## 13. Plano de Rollout

- **Estratégia:** 🟡 distribuição do `.exe` empacotado (PyInstaller, modo one-dir) por pasta compartilhada ou mídia interna
- **Como reverter (rollback):** 🟡 remover a pasta do app da máquina; nenhum estado residual no sistema
- **Monitoramento pós-deploy:** 🟡 primeiro lote real acompanhado pelo técnico; verificação de bloqueio por antivírus corporativo

---

## 14. Open Questions

| # | Pergunta | Impacto | Dono | Prazo |
|---|---------|---------|------|-------|
| OQ-01 | 🟡 Idioma da interface: pt-br presumido — confirmar? | Baixo | Sandoval | antes do coding |
| OQ-02 | 🟡 Lembrar última origem/destino entre execuções (arquivo de configuração local)? | Médio | Sandoval | pós-MVP |
| OQ-03 | 🟡 Modo one-dir ou one-file no PyInstaller? | Baixo | Sandoval | antes do build |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão | Alternativas consideradas | Racional |
|---------|--------------------------|----------|
| 🟡 Tkinter como toolkit | PySide6, wxWidgets | 🟡 vem com Python (zero dependência externa); suficiente para formulário com progresso |
| 🟡 Lote em thread separada da UI | execução síncrona na thread de eventos | 🟡 mantém a janela responsiva e o cancelamento imediato |
| 🟡 Diálogos nativos do Windows | widgets próprios de árvore de arquivos | 🟡 familiaridade da persona com diálogos do Windows; menos código a manter |
| 🟡 Empacotamento preferindo one-dir | one-file | 🟡 inicialização mais curta e melhor aceitação por antivírus corporativo (decisão revisável em OQ-03) |

---

## Apêndice

### Referências
- 🟡 prd.md (seções 4, 6, 8); personas.md; Demanda Geonetwork.pdf (passo 3)

### Histórico de Revisões
| Versão | Data | Autor | Mudanças |
|--------|------|-------|---------|
| 1.0 | 2026-09-23 | reversa-spec-sdd | Criação inicial |

---

## Avaliação de Qualidade

> Executado por `scripts/spec_scorer.py` em 2026-09-23 (pipeline /reversa-new, modo expresso).

**Score total: 100/100** — ⭐ Excelente — Pronta para implementação
**Iterações:** 1 (score ≥ 80 na primeira avaliação; nenhuma correção necessária)

| Dimensão | Peso | Resultado |
|---|---|---|
| Completude | 30% | 100% |
| Testabilidade | 25% | 100% |
| Clareza | 20% | 100% |
| Escopo | 15% | 100% |
| Edge Cases | 10% | 100% |

**Gaps críticos:** nenhum. **Sugestões:** nenhuma.
