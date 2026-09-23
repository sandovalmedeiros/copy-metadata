# Requirements: Copiador de Metadados GeoNetwork (MVP)

> Identificador: `001-copiador-metadados-geonetwork`
> Data: 2026-09-23
> Pasta da extração reversa: `_reversa_sdd/` (projeto greenfield — fontes: PRD, ideation, personas e specs SDD)
> Confidência: 🟢 CONFIRMADO (documento de demanda ou decisão do usuário), 🟡 INFERIDO/PREMISSA, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Entrega o MVP completo descrito no PRD: aplicativo desktop Windows que, a partir de uma pasta de exportação do GeoNetwork, copia em lote o arquivo `.xml` alvo de cada subpasta de registro (UUID) para uma pasta de destino, renomeando cada cópia como `<uuid>.xml`, com progresso, cancelamento e relatório de resultado. Atende o Técnico de Geoprocessamento e elimina a cópia/renomeação manual pasta a pasta — hoje o processo é inteiramente manual no Windows Explorer.

## 2. Contexto a partir do legado

> Projeto greenfield: não há sistema legado extraído. As fontes abaixo são os artefatos do pipeline `/reversa-new`.

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/prd.md#4-escopo-in` | Escopo funcional completo do MVP (seleção origem/alvo/destino, cópia em lote, progresso, relatório, GUI desktop) | 🟢 |
| `_reversa_sdd/prd.md#9-criterios-de-aceite-alto-nivel` | Cinco critérios Dado/Quando/Então de alto nível | 🟢 |
| `_reversa_sdd/sdd/scanner-de-pastas.md#6-requisitos-funcionais` | Varredura das subpastas, captura do `nome_novo`, derivação do caminho relativo do alvo | 🟡 |
| `_reversa_sdd/sdd/motor-de-copia-renomeacao.md#6-requisitos-funcionais` | Cópia em lote, sobrescrita, colisão, continuidade após falha, cancelamento | 🟡 |
| `_reversa_sdd/sdd/relatorio-de-execucao.md#6-requisitos-funcionais` | Consolidação por status, lista de problemas, exportação opcional | 🟡 |
| `_reversa_sdd/sdd/interface-desktop.md#6-requisitos-funcionais` | Diálogos nativos, validação, progresso, cancelar, executável único | 🟡 |
| `_reversa_sdd/personas.md#persona-1-tecnico-de-geoprocessamento` | Persona primária e jornada de 7 passos | 🟡 |
| `_reversa_sdd/ideation.md#premissas-a-validar` | Estrutura fixa, unicidade do UUID, acesso/permissões | 🟡 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Técnico de Geoprocessamento (personas.md) | Preparar lotes de metadados exportados para importação sem trabalho manual | Recebe uma exportação no share, executa o app uma vez e leva N arquivos `<uuid>.xml` prontos ao destino em minutos |

Frequência: sob demanda, a cada nova exportação de lote (tipicamente diária/semanal).

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** O nome de cada arquivo gerado é exclusivamente o nome da subpasta de origem (`nome_novo`), com extensão `.xml` — nunca o nome original do arquivo-alvo. 🟢
   - Origem no legado: n/a (greenfield; demanda PDF passos 2 e 5)
   - Tipo: nova
2. **RN-02:** Toda subpasta direta da origem é processada em uma única execução (operação em lote), sem seleção individual de pastas. 🟢
   - Origem no legado: n/a (decisão de entrevista: lote)
   - Tipo: nova
3. **RN-03:** Falha em uma pasta individual (alvo ausente, erro de leitura/escrita) nunca aborta o lote — a ocorrência é registrada com motivo e as demais continuam. 🟡
   - Origem no legado: n/a (spec motor RF-05)
   - Tipo: nova
4. **RN-04:** Sobrescrita de arquivo existente no destino nunca é silenciosa: segue a política configurada, com padrão "perguntar uma vez por execução" (sobrescrever tudo / pular existentes / cancelar). 🟡
   - Origem no legado: n/a (spec motor RF-03 + PRD §4; premissa a validar)
   - Tipo: nova
5. **RN-05:** A cópia preserva o conteúdo byte a byte do arquivo-alvo. 🟡
   - Origem no legado: n/a (spec motor RF-08)
   - Tipo: nova
6. **RN-06:** Cancelamento preserva as cópias já concluídas e gera relatório parcial. 🟡
   - Origem no legado: n/a (spec motor RF-06 + relatório RF-04)
   - Tipo: nova
7. **RN-07:** O relatório de execução é exibido em toda condição de término — sucesso, cancelamento ou falha. 🟡
   - Origem no legado: n/a (spec relatório RF-03)
   - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | O sistema lista todas as subpastas diretas da origem, capturando o nome de cada uma | Must | Origem com N subpastas gera N registros na varredura | 🟢 |
| RF-02 | O usuário indica o arquivo-alvo `.xml` navegando pela interface; o sistema localiza o arquivo correspondente em cada subpasta pelo caminho relativo derivado da seleção | Must | Seleção de `<origem>\<uuid>\metadata\metadata.xml` localiza `metadata\metadata.xml` em todas as pastas; pastas sem o alvo ficam marcadas com motivo | 🟢 |
| RF-03 | O sistema copia o arquivo-alvo de cada pasta válida para o destino, salvando como `<nome_pasta>.xml` | Must | Lote com N pastas válidas produz N arquivos `<uuid>.xml` com conteúdo idêntico | 🟢 |
| RF-04 | O sistema cria a pasta de destino quando inexistente | Must | Destino inexistente é criado antes da primeira cópia | 🟡 |
| RF-05 | O sistema aplica a política de sobrescrita a arquivos pré-existentes, sem sobrescrita silenciosa | Must | Arquivo existente gera status sobrescrito ou pulado conforme política escolhida na execução | 🟡 |
| RF-06 | O sistema continua o lote após falha individual, registrando o erro com motivo | Must | Falha em 1 pasta de N não impede as demais; falha aparece no relatório | 🟡 |
| RF-07 | O usuário cancela a execução em andamento; cópias concluídas permanecem | Must | Cancelamento efetivo em < 2 s; relatório parcial exibido | 🟡 |
| RF-08 | O usuário seleciona origem, arquivo-alvo e destino por diálogos nativos do Windows | Must | Os três campos são preenchidos sem digitação obrigatória de paths | 🟢 |
| RF-09 | O botão de execução habilita somente com os três campos preenchidos e válidos | Must | Campo vazio ou origem inacessível mantém o botão desabilitado com indicação do problema | 🟡 |
| RF-10 | O sistema exibe progresso (N de M pastas) durante o lote e desabilita os controles de configuração | Must | Progresso atualiza a cada pasta; seletores ficam inativos durante a execução | 🟡 |
| RF-11 | O sistema exibe o relatório consolidado (contagens por status + problemas com motivo) ao término | Must | Soma das contagens igual ao total de itens; problemas listados com motivo | 🟡 |
| RF-12 | O usuário exporta o relatório para arquivo texto/CSV no destino | Could | Exportação grava arquivo legível com as mesmas contagens | 🟡 |
| RF-13 | O usuário executa a aplicação a partir de um único executável, sem runtime instalado | Must | Executável abre e opera todas as funções em máquina Windows limpa | 🟢 |

Rastreabilidade por componente: RF-01/02 → sdd/scanner-de-pastas.md; RF-03–07 → sdd/motor-de-copia-renomeacao.md; RF-08–10, RF-13 → sdd/interface-desktop.md; RF-11/12 → sdd/relatorio-de-execucao.md.

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Varredura de lote de 500 pastas em rede conclui em < 60 s; cópia em < 5 min | Targets propostos nas specs (a validar em ambiente real) | 🟡 |
| Integridade | 0 bytes de diferença entre arquivo de origem e cópia no destino | Spec motor RNF-01; verificação mínima por tamanho | 🟡 |
| Compatibilidade | Windows 10 e 11, 64 bits, com paths de rede mapeados e UNC | Ambiente corporativo da persona (PRD §6) | 🟡 |
| Responsividade | Janela nunca congela durante o lote; cancelamento atende em < 2 s | Spec interface RNF-02; lote fora da thread de eventos | 🟡 |
| Distribuição | Executável único portável, inicialização < 3 s, sem instalação | Decisão de entrevista + spec interface G-03/RNF-01 | 🟢 |
| Segurança | Nenhum dado pessoal processado; operações limitadas às permissões do usuário Windows | PRD §6/§7 e specs seção 12 | 🟡 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Cópia em lote bem-sucedida
  Dado uma origem com 3 subpastas UUID, cada uma contendo "metadata\metadata.xml"
  Quando o usuário seleciona origem, arquivo-alvo e destino e executa
  Então o destino contém 3 arquivos "<uuid>.xml" com conteúdo idêntico ao alvo de cada pasta
  E o relatório exibe 3 copiados e 0 problemas

Cenário: Pasta sem arquivo-alvo
  Dado uma origem com 3 subpastas, uma delas sem o arquivo-alvo no caminho esperado
  Quando o usuário executa a cópia em lote
  Então 2 arquivos são copiados, o lote não é abortado
  E o relatório lista a pasta problemática com motivo "alvo ausente"

Cenário: Arquivo já existente no destino
  Dado um arquivo "<uuid>.xml" já presente no destino
  Quando o lote alcança a pasta correspondente
  Então o sistema apresenta a escolha de política (sobrescrever ou pular)
  E a ocorrência é registrada no relatório com o status aplicado

Cenário: Origem inacessível
  Dado uma origem em share de rede indisponível
  Quando o usuário tenta executar
  Então o sistema exibe mensagem específica do problema, nada é copiado
  E a aplicação permanece utilizável para corrigir o caminho

Cenário: Cancelamento no meio do lote
  Dado um lote em andamento com 2 de 5 pastas concluídas
  Quando o usuário aciona cancelar
  Então a execução para em menos de 2 segundos, as 2 cópias permanecem no destino
  E o relatório parcial exibe 2 copiados e 3 cancelados
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01, RF-02, RF-03 | Must | Núcleo da demanda (PDF passos 1–5) — sem eles não há produto |
| RF-04, RF-05 | Must | Destino utilizável e segurança contra perda silenciosa de arquivo |
| RF-06, RF-07 | Must | Lote resiliente e controlável — requisitos do PRD §9 |
| RF-08–RF-11 | Must | Persona não programadora; operação inteira por interface com feedback |
| RF-12 | Could | Exportação é conveniência pós-conferência (spec relatório NG/decisão) |
| RF-13 | Must | Decisão explícita de entrevista (executável sem runtime) |
| RNF desempenho | Should | Targets propostos, não confirmados em ambiente real |

## 9. Esclarecimentos

> Nenhuma sessão de dúvidas registrada ainda. Rode `/reversa-clarify` quando houver `[DÚVIDA]` pendente.

## 10. Lacunas

Nenhuma lacuna 🔴 bloqueante. Premissas 🟡 adotadas (revisar com o usuário):

- 🟡 Premissa 1 — Semântica do arquivo-alvo: o sistema deriva o **caminho relativo completo** da seleção do usuário (ex.: `metadata\metadata.xml`), aplicando-o a todas as pastas (decisão do Decision Log do scanner; alternativa "busca por nome em qualquer subnível" ficou como OQ-01 da spec).
- 🟡 Premissa 2 — Política de sobrescrita padrão: **perguntar uma vez por execução** (sobrescrever tudo / pular existentes / cancelar), conforme proposta do PRD §4 e spec motor OQ-01.
- 🟡 Premissa 3 — Idioma da interface: **pt-br** (presumido; spec interface OQ-01).
- 🟡 Premissa 4 — Métricas de desempenho (60 s / 5 min / 500 pastas) são targets propostos, a validar em ambiente real.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-09-23 | Versão inicial gerada por `/reversa-requirements` (pipeline /reversa-new expresso) | reversa-requirements |
