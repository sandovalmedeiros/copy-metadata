# Spec: Scanner de Pastas (varredura do lote de exportação)

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-09-23
**Reviewers:** N/A — pipeline Reversa

---

## 1. Resumo

🟡 Componente que varre a pasta de origem indicada pelo usuário (lote de exportação do GeoNetwork), identifica cada subpasta de registro, captura o nome de cada uma como `nome_novo` (UUID), deriva o caminho relativo do arquivo-alvo a partir do arquivo selecionado pelo usuário e produz a lista de pastas com o arquivo-alvo localizado ou marcado como ausente. É a entrada do motor de cópia.

---

## 2. Contexto e Motivação

**Problema:**
🟡 Exportações do GeoNetwork chegam como uma pasta por lote (ex.: `IDEBAHIA-CADASTRO-2026-09-22T150904`) contendo uma subpasta por registro de metadado, nomeada com o UUID (ex.: `0b8733a3-93ba-4d18-aa6a-a63782546898`), com o XML aninhado em `<uuid>\metadata\metadata.xml`. Hoje o técnico navega manualmente nessa árvore para descobrir o que existe em cada pasta.

**Evidências:**
🟡 Documento de demanda `Demanda Geonetwork.pdf` (23/09/2026), passos 1–3: ler pastas de um path indicado, guardar o nome da pasta em variável e indicar o arquivo `.xml` alvo navegando pela interface. Decisão de entrevista: operação em lote (todas as pastas).

**Por que agora:**
🟡 Demanda formal registrada em 23/09/2026 pelo solicitante; o processo manual é o gargalo atual do fluxo de preparação de metadados para importação.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Enumerar 100% das subpastas diretas da pasta de origem, capturando o nome de cada uma
- [ ] 🟡 G-02: Derivar o caminho relativo do arquivo-alvo a partir do arquivo selecionado pelo usuário
- [ ] 🟡 G-03: Localizar o arquivo-alvo em cada subpasta, marcando como ausente as que não o contêm, com 0 pastas ignoradas sem registro

**Métricas de sucesso:**
| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Subpastas enumeradas por varredura | 0% (manual) | 100% das subpastas diretas | entrega do MVP |
| 🟡 Pastas ignoradas sem registro na saída | n/d | 0 pastas | entrega do MVP |
| 🟡 Duração da varredura de lote de 500 pastas em rede | n/d | < 60 s (proposta a validar) | entrega do MVP |

---

## 4. Non-Goals (Fora do Escopo)

- NG-01: 🟡 Não copia nem renomeia arquivos — papel do motor de cópia
- NG-02: 🟡 Não lê nem valida o conteúdo XML dos metadados
- NG-03: 🟡 Não varre recursivamente além do primeiro nível de subpastas da origem
- NG-04: 🟡 Não monitora a origem continuamente — executa sob demanda

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 Técnico de Geoprocessamento (ver personas.md) — indica origem e arquivo-alvo pela interface do app.
**Usuário secundário:** 🟡 Nenhum — componente interno, consumido pela interface-desktop.

**Jornada atual (sem a feature):**
🟡 1. Abre a pasta de exportação no Windows Explorer; 2. entra pasta por pasta para conferir a estrutura; 3. anota/copia UUIDs manualmente.

**Jornada futura (com a feature):**
🟡 1. Seleciona a origem e o arquivo representante na interface; 2. recebe a lista completa de pastas com alvo localizado/ausente; 3. segue direto para a cópia em lote.

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | 🟡 O usuário deve indicar a pasta de origem do lote a varrer | Must | 🟡 Dada uma origem válida com subpastas, a varredura retorna todas as subpastas diretas |
| RF-02 | 🟡 O sistema deve listar todas as subpastas diretas da origem, capturando o nome de cada uma como `nome_novo` | Must | 🟡 Origem com N subpastas retorna N registros, cada um com `nome_novo` igual ao nome da pasta |
| RF-03 | 🟡 O sistema deve derivar o caminho relativo do arquivo-alvo a partir do arquivo selecionado pelo usuário, com relação à subpasta que o contém | Must | 🟡 Seleção de `<origem>\<uuid>\metadata\metadata.xml` deriva caminho relativo `metadata\metadata.xml` ⚠️ ABERTO: ver OQ-01 |
| RF-04 | 🟡 O sistema deve localizar o arquivo-alvo em cada subpasta pelo caminho relativo derivado | Must | 🟡 Subpasta contendo o alvo no caminho derivado retorna status alvo-encontrado |
| RF-05 | 🟡 O sistema deve marcar como alvo-ausente cada subpasta sem o arquivo-alvo, com motivo registrado | Must | 🟡 Subpasta sem o alvo não gera cópia e aparece na saída com status alvo-ausente |
| RF-06 | 🟡 O sistema deve registrar na saída toda subpasta enumerada, inclusive as problemáticas | Must | 🟡 Contagem de registros na saída igual à contagem de subpastas diretas da origem |
| RF-07 | 🟡 O sistema deve ignorar arquivos soltos na raiz da origem, tratando apenas subpastas | Should | 🟡 Arquivo solto na origem não gera registro na saída |
| RF-08 | 🟡 O sistema deve validar o nome de cada subpasta como nome de arquivo Windows válido, sinalizando inválidos | Should | 🟡 Subpasta com caractere inválido para arquivo retorna status nome-invalido com motivo |

### 6.2 Fluxo Principal (Happy Path)

1. O usuário indica a pasta de origem (ex.: `S:\Digeo\PUBLICO\Francisco\IDEBAHIA-CADASTRO-2026-09-22T150904`)
2. O sistema enumera as subpastas diretas e captura cada nome como `nome_novo`
3. O usuário seleciona o arquivo-alvo representante (ex.: `metadata.xml` dentro de `<uuid>\metadata\`)
4. O sistema deriva o caminho relativo do alvo (ex.: `metadata\metadata.xml`)
5. Resultado: lista de `PastaScandeada` com status alvo-encontrado ou alvo-ausente, pronta para o motor de cópia

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — alvo ausente em parte das pastas:**
1. A varredura localiza o alvo em parte das subpastas
2. As demais recebem status alvo-ausente com motivo
3. A lista completa é entregue — o motor decide o que copiar

**Fluxo Alternativo B — origem com arquivos soltos:**
1. A raiz da origem contém arquivos além de subpastas
2. O sistema ignora os arquivos soltos e processa apenas as subpastas

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| RNF-01 | Performance da enumeração | 🟡 < 60 s para 500 pastas em rede | 🟡 proposta a validar com ambiente real |
| RNF-02 | Execução local | sem serviços instalados | 🟡 roda no desktop do usuário |
| RNF-03 | Compatibilidade | Windows 10 e 11 | 🟡 ambiente corporativo alvo |
| RNF-04 | Rede | funciona com paths mapeados (ex.: `S:\`) e UNC | 🟡 sem dependência de internet |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 componente interno sem UI própria; consumido pela interface-desktop, que fornece os diálogos de seleção.

**Comportamento esperado:**
🟡 Recebe origem + arquivo-alvo selecionado; devolve estrutura `ResultadoVarredura` (seção 9). Nenhum estado visual próprio.

**Estados da UI:**
- Estado vazio: 🟡 origem sem subpastas → lista vazia com aviso "nenhuma subpasta encontrada"
- Estado de carregamento: 🟡 enumeração em andamento → progresso reportado por who consome (interface)
- Estado de erro: 🟡 origem inexistente/inacessível → erro propagado com mensagem clara
- Estado de sucesso: 🟡 lista completa com status por pasta

---

## 9. Modelo de Dados

**Entidades novas ou modificadas (em memória):**

```
PastaScandeada {
  nome_pasta: texto              // UUID capturado (nome_novo)
  caminho_absoluto: texto        // caminho da subpasta na origem
  caminho_relativo_alvo: texto   // ex.: metadata\metadata.xml
  status: texto                  // alvo-encontrado | alvo-ausente | nome-invalido | erro-leitura
  motivo: texto                  // preenchido quando status <> alvo-encontrado
}

ResultadoVarredura {
  origem: texto
  arquivo_alvo_selecionado: texto
  caminho_relativo_alvo: texto
  pastas: lista de PastaScandeada
}
```

**Migrações necessárias:** Não — componente sem persistência.

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|-------------|------|------------------------|
| 🟡 Share de rede Windows (origem, leitura) | Obrigatória | 🟡 erro claro de origem inacessível; nenhuma enumeração parcial |
| 🟡 Sistema de arquivos local (stdlib) | Obrigatória | 🟡 falha irrecuperável do app com mensagem |
| 🟡 interface-desktop (fornecedor dos diálogos) | Obrigatória | 🟡 componente não executa isolado; testável com paths diretos |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---------|---------|----------------------|
| EC-01: 🟡 origem inexistente ou sem permissão | 🟡 path inválido ou share fora do ar | 🟡 mensagem de erro clara; nenhuma enumeração parcial; falha reportada à interface |
| EC-02: 🟡 origem sem subpastas | 🟡 lote vazio ou path de pasta simples | 🟡 resultado vazio com aviso explícito "nenhuma subpasta encontrada" |
| EC-03: 🟡 nome de subpasta inválido como arquivo | 🟡 caracteres proibidos no Windows | 🟡 status nome-invalido com motivo; demais pastas seguem |
| EC-04: 🟡 subpasta sem permissão de leitura | 🟡 ACL restritiva no share | 🟡 status erro-leitura com motivo; enumeração continua |
| EC-05: 🟡 estrutura aninhada distinta | 🟡 alvo em subnível diferente do derivado | 🟡 status alvo-ausente; registro permite diagnóstico posterior |

---

## 12. Segurança e Privacidade

- **Autenticação:** 🟡 nenhuma — aplicativo local de desktop
- **Autorização:** 🟡 herdada do usuário Windows sobre o share e pastas locais
- **Dados sensíveis:** 🟡 nenhum identificado — metadados públicos de IDE; nenhum dado pessoal processado
- **Auditoria:** 🟡 o relatório de execução cumpre o papel de registro por operação; sem log persistente adicional

---

## 13. Plano de Rollout

- **Estratégia:** 🟡 entrega empacotada no executável único do app (componente interno, sem rollout separado)
- **Como reverter (rollback):** 🟡 remover o executável do app (não há estado no sistema)
- **Monitoramento pós-deploy:** 🟡 feedback direto do técnico durante o primeiro lote real

---

## 14. Open Questions

| # | Pergunta | Impacto | Dono | Prazo |
|---|---------|---------|------|-------|
| OQ-01 | 🟡 A seleção do usuário define o caminho relativo completo (ex.: `metadata\metadata.xml`) ou apenas o nome do arquivo, buscado em qualquer subnível de cada pasta? | Alto | Sandoval | antes do coding |
| OQ-02 | 🟡 Confirmar se as pastas podem conter outros `.xml` (ex.: `schemas.xml`) que devam ser ignorados explicitamente | Médio | Sandoval | antes do coding |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão | Alternativas consideradas | Racional |
|---------|--------------------------|----------|
| 🟡 Varredura restrita ao primeiro nível de subpastas | varredura recursiva | 🟡 coerente com a estrutura de exportação MEF (uma pasta por registro) e com a demanda |
| 🟡 Derivar caminho relativo do arquivo selecionado | busca por nome em qualquer subnível | 🟡 comportamento previsível e diagnosticável; alternativa registrada como OQ-01 |

---

## Apêndice

### Referências
- 🟡 prd.md (seções 4, 8, 9); ideation.md; personas.md; Demanda Geonetwork.pdf

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
