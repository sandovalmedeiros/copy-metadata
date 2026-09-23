# Spec: Motor de Cópia e Renomeação (lote `<uuid>.xml`)

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-09-23
**Reviewers:** N/A — pipeline Reversa

---

## 1. Resumo

🟡 Componente que executa a cópia em lote: para cada pasta com arquivo-alvo localizado pelo scanner, copia o arquivo para a pasta de destino renomeado como `<nome_novo>.xml` (UUID da pasta de origem). Trata política de sobrescrita, colisões, falhas por pasta e cancelamento, preservando o conteúdo byte a byte.

---

## 2. Contexto e Motivação

**Problema:**
🟡 Com a lista de pastas identificada, a extração manual ainda exigiria copiar cada `metadata.xml` e renomear para `<uuid>.xml`, um por um, no Windows Explorer — etapa mais propensa a erro da demanda (UUID colado errado, sobrescrita acidental).

**Evidências:**
🟡 Demanda Geonetwork.pdf (23/09/2026), passos 4–5: usuário indica pasta de destino; o app copia o arquivo indicado salvando com o nome da variável `nome_novo` (ex.: `C:\metadados_geonetwork\0b8733a3-93ba-4d18-aa6a-a63782546898.xml`). Decisão de entrevista: operação em lote (todas as pastas).

**Por que agora:**
🟡 É o coração da demanda — sem o motor, o app não entrega valor; todos os demais componentes existem para alimentá-lo.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Copiar o arquivo-alvo de 100% das pastas válidas, salvando cada uma como `<nome_novo>.xml` no destino
- [ ] G-02: 🟡 Preservar o conteúdo byte a byte em toda cópia
- [ ] G-03: 🟡 Manter a execução íntegra após falha em pastas individuais, com 0 falhas silenciosas (toda ocorrência registrada com motivo)

**Métricas de sucesso:**
| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Pastas válidas copiadas por execução | 0% (manual) | 100% | entrega do MVP |
| 🟡 Diferença de conteúdo entre origem e destino | n/d | 0 bytes | entrega do MVP |
| 🟡 Duração da cópia de lote de 500 arquivos pequenos em rede | n/d | < 5 min (proposta a validar) | entrega do MVP |

---

## 4. Non-Goals (Fora do Escopo)

- NG-01: 🟡 Não varre a origem — consome o `ResultadoVarredura` do scanner
- NG-02: 🟡 Não edita, valida ou transforma o conteúdo XML
- NG-03: 🟡 Não envia os arquivos para nenhum serviço ou instância GeoNetwork (importação fica fora)
- NG-04: 🟡 Não desfaz cópias já concluídas quando o usuário cancela

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 Técnico de Geoprocessamento — dispara o lote pela interface e consome o resultado.
**Usuário secundário:** 🟡 Nenhum — componente interno.

**Jornada atual (sem a feature):**
🟡 1. Copia `metadata.xml` manualmente; 2. cola o UUID como novo nome; 3. repete por pasta, conferindo duplicatas à mão.

**Jornada futura (com a feature):**
🟡 1. Confere origem/alvo/destino na interface; 2. executa o lote; 3. encontra N arquivos `<uuid>.xml` prontos no destino.

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | 🟡 O sistema deve copiar o arquivo-alvo de cada pasta válida para o destino, salvando com o nome `<nome_pasta>.xml` | Must | 🟡 Lote com N pastas válidas produz N arquivos `<uuid>.xml` no destino com conteúdo idêntico |
| RF-02 | 🟡 O sistema deve criar a pasta de destino quando ela não existir | Must | 🟡 Destino inexistente é criado antes da primeira cópia |
| RF-03 | 🟡 O sistema deve aplicar a política de sobrescrita configurada quando `<nome_pasta>.xml` já existir no destino | Must | 🟡 Arquivo pré-existente gera status sobrescrito ou pulado conforme política; nunca sobrescrita silenciosa ⚠️ ABERTO: política padrão, ver OQ-01 |
| RF-04 | 🟡 O sistema deve detectar nomes duplicados no lote antes de copiar e sinalizar a segunda ocorrência como colisão | Should | 🟡 Duas pastas com o mesmo nome geram um copiado e uma colisão registrada, sem sobrescrita entre si |
| RF-05 | 🟡 O sistema deve continuar a execução após falha em uma pasta, registrando o erro e processando as demais | Must | 🟡 Falha em 1 pasta de um lote de N não impede as N-1 demais; falha fica no resultado com motivo |
| RF-06 | 🟡 O sistema deve permitir cancelamento durante o lote, preservando as cópias já concluídas | Must | 🟡 Cancelamento interrompe em < 2 s; cópias feitas permanecem no destino; itens não processados ficam cancelados |
| RF-07 | 🟡 O sistema deve reportar progresso a cada pasta concluída | Should | 🟡 Consumidor do progresso recebe contagem atualizada (N de M) por pasta |
| RF-08 | 🟡 O sistema deve copiar preservando o conteúdo byte a byte | Must | 🟡 Comparação de tamanho/conteúdo origem vs destino retorna igual |

### 6.2 Fluxo Principal (Happy Path)

1. O sistema recebe `ResultadoVarredura`, destino e política de sobrescrita
2. O sistema valida/cria a pasta de destino
3. O sistema copia o alvo da primeira pasta como `<nome_pasta>.xml`, reporta progresso e segue à próxima
4. O sistema repete até a última pasta válida
5. Resultado: `ResultadoCopia` com um `ItemCopia` por pasta (copiado/sobrescrito/pulado/colisao/erro/cancelado + motivo)

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — destino já contém arquivos de execução anterior:**
1. `<nome_pasta>.xml` já existe no destino
2. O sistema aplica a política de sobrescrita (sobrescrever ou pular)
3. A ocorrência é registrada com o status correspondente

**Fluxo Alternativo B — cancelamento no meio do lote:**
1. O usuário aciona cancelar
2. O sistema encerra a pasta corrente com status cancelado
3. As pastas restantes ficam canceladas; as cópias prontas permanecem

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| RNF-01 | Integridade da cópia | 🟡 0 bytes de diferença | 🟡 verificação de tamanho no mínimo; hash opcional |
| RNF-02 | Performance do lote | 🟡 < 5 min para 500 arquivos pequenos em rede | 🟡 proposta a validar |
| RNF-03 | Responsividade ao cancelamento | 🟡 < 2 s entre o acionamento e a parada | 🟡 checagem por pasta |
| RNF-04 | Execução local | 🟡 sem serviços instalados, sem internet | 🟡 desktop do usuário |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 componente interno sem UI própria; progresso e resultado exibidos pela interface-desktop.

**Comportamento esperado:**
🟡 Executa pasta a pasta, sequencial; publica progresso por pasta; nunca aborta o lote por falha individual.

**Estados da UI:**
- Estado vazio: 🟡 lote sem pastas válidas → resultado com 0 itens copiados e aviso
- Estado de carregamento: 🟡 lote em andamento → progresso N de M
- Estado de erro: 🟡 falha de infraestrutura (destino/escrita) → parada com mensagem e resultado parcial
- Estado de sucesso: 🟡 resultado consolidado por pasta

---

## 9. Modelo de Dados

**Entidades novas ou modificadas (em memória):**

```
ItemCopia {
  nome_pasta: texto          // UUID (nome_novo)
  origem: texto              // caminho absoluto do arquivo-alvo
  destino_final: texto       // <destino>\<nome_pasta>.xml
  status: texto              // copiado | sobrescrito | pulado | colisao | erro | cancelado
  motivo: texto              // preenchido quando status <> copiado
}

ResultadoCopia {
  destino: texto
  politica_sobrescrita: texto  // sobrescrever | pular
  itens: lista de ItemCopia
}
```

**Migrações necessárias:** Não — componente sem persistência.

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|-------------|------|------------------------|
| 🟡 scanner-de-pastas (entrada `ResultadoVarredura`) | Obrigatória | 🟡 motor não executa; falha de contrato reportada ao desenvolvedor via teste |
| 🟡 Share de rede (leitura dos alvos) | Obrigatória | 🟡 erro por pasta com motivo; lote continua nas demais |
| 🟡 Sistema de arquivos local (escrita no destino) | Obrigatória | 🟡 parada com mensagem de falha de escrita e resultado parcial |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---------|---------|----------------------|
| EC-01: 🟡 destino sem permissão ou sem espaço | 🟡 falha de escrita na primeira cópia | 🟡 parada do lote com mensagem específica; nenhum resultado perdido |
| EC-02: 🟡 arquivo de origem travado por outro processo | 🟡 arquivo aberto/exclusivo no share | 🟡 status erro com motivo; lote segue nas demais pastas |
| EC-03: 🟡 queda de rede no meio do lote | 🟡 share indisponível durante a cópia | 🟡 pasta corrente com status erro (falha de leitura); tentativa de seguir nas demais; restantes podem falhar em cadeia com o mesmo motivo |
| EC-04: 🟡 UUID duplicado no lote | 🟡 duas subpastas com o mesmo nome | 🟡 primeira ocorrência copiada; segunda com status colisao, sem sobrescrita silenciosa |
| EC-05: 🟡 nome reservado no Windows | 🟡 pasta chamada CON, PRN, AUX etc. | 🟡 status erro com motivo nome-reservado; lote segue |
| EC-06: 🟡 arquivo-alvo removido entre varredura e cópia | 🟡 alteração concorrente na origem | 🟡 status erro com motivo alvo-sumido; lote segue |

---

## 12. Segurança e Privacidade

- **Autenticação:** 🟡 nenhuma — aplicativo local de desktop
- **Autorização:** 🟡 herdada do usuário Windows (leitura na origem, escrita no destino)
- **Dados sensíveis:** 🟡 nenhum identificado — metadados públicos; nenhum dado pessoal processado
- **Auditoria:** 🟡 o `ResultadoCopia` registra toda ocorrência por pasta; sem log persistente adicional

---

## 13. Plano de Rollout

- **Estratégia:** 🟡 entrega empacotada no executável único do app (componente interno)
- **Como reverter (rollback):** 🟡 remover o executável; arquivos copiados são produtos do usuário e permanecem
- **Monitoramento pós-deploy:** 🟡 primeira execução real acompanhada pelo técnico; conferência de contagens do relatório

---

## 14. Open Questions

| # | Pergunta | Impacto | Dono | Prazo |
|---|---------|---------|------|-------|
| OQ-01 | 🟡 Política de sobrescrita padrão quando `<uuid>.xml` já existe no destino: perguntar uma vez por execução, sobrescrever sempre ou pular sempre? | Alto | Sandoval | antes do coding |
| OQ-02 | 🟡 Verificar integridade por hash (além do tamanho) ativa por padrão? | Baixo | Sandoval | antes do coding |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão | Alternativas consideradas | Racional |
|---------|--------------------------|----------|
| 🟡 Cópia sequencial com continuidade após falha por pasta | transação tudo-ou-nada | 🟡 coerente com lote: maximiza o trabalho aproveitado; falhas ficam registradas |
| 🟡 Preservar cópias ao cancelar | desfazer cópias no cancelamento | 🟡 cancelamento não destrói trabalho; usuário decide o que fazer com o parcial |
| 🟡 Detecção de colisão antes de copiar | sobrescrita direta | 🟡 evita perda silenciosa de arquivo em lotes com duplicatas |

---

## Apêndice

### Referências
- 🟡 prd.md (seções 4, 8, 9); scanner-de-pastas.md; Demanda Geonetwork.pdf (passos 4–5)

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
