# Spec: Relatório de Execução (consolidação e exibição do resultado)

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-09-23
**Reviewers:** N/A — pipeline Reversa

---

## 1. Resumo

🟡 Componente que consolida o `ResultadoCopia` do motor em um relatório legível: contagens por status, lista por pasta com motivo das ocorrências problemáticas e resumo de duração. Exibido na janela do app ao final de toda execução — concluída, cancelada ou falha — e exportável para arquivo no destino.

---

## 2. Contexto e Motivação

**Problema:**
🟡 Um lote com centenas de pastas pode terminar com a maioria copiada e algumas poucas problemáticas (alvo ausente, erro de leitura, colisão). Sem consolidação, o técnico precisaria conferir manualmente o destino contra a origem para descobrir o que faltou — reintroduzindo o trabalho manual que o app elimina.

**Evidências:**
🟡 PRD (seção 4): "Exibir relatório de resultado: arquivos copiados, pastas sem arquivo-alvo, erros (com motivo)"; persona (jornada, passo 7): "Conferir o relatório de resultado (copiados, pastas sem arquivo-alvo, erros)".

**Por que agora:**
🟡 Métrica de sucesso proposta no PRD: 100% das pastas com alvo geram `<uuid>.xml`, com exceções listadas em relatório — sem o relatório, a métrica é in verificável.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Consolidar contagens por status para 100% dos itens do `ResultadoCopia`
- [ ] G-02: 🟡 Listar toda ocorrência problemática com motivo, permitindo localizar a pasta envolvida
- [ ] G-03: 🟡 Exibir o relatório em toda condição de término (concluído, cancelado, falha), com 0 ocorrências omitidas

**Métricas de sucesso:**
| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Itens do resultado refletidos no relatório | 0% (manual) | 100% | entrega do MVP |
| 🟡 Ocorrências problemáticas com motivo exibido | n/d | 100% | entrega do MVP |
| 🟡 Tempo de geração do relatório na tela | n/d | < 2 s para lote de 500 itens | entrega do MVP |

---

## 4. Non-Goals (Fora do Escopo)

- NG-01: 🟡 Não mantém histórico persistente entre execuções — o relatório vale para a execução corrente
- NG-02: 🟡 Não envia o relatório por e-mail, rede ou serviço externo
- NG-03: 🟡 Não gera formatos binários ou proprietários — texto na tela e exportação texto/CSV
- NG-04: 🟡 Não decide políticas do motor — apenas apresenta o que ocorreu

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 Técnico de Geoprocessamento — lê o relatório para conferir o lote e agir sobre as exceções.
**Usuário secundário:** 🟡 Nenhum — componente interno consumido pela interface-desktop.

**Jornada atual (sem a feature):**
🟡 1. Confere o destino manualmente contra a origem; 2. reabre pastas para entender falhas; 3. repete a cópia dos faltosos à mão.

**Jornada futura (com a feature):**
🟡 1. Lê o resumo (N copiados, M problemas); 2. abre a lista de problemas com motivos; 3. trata apenas as pastas listadas.

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | 🟡 O sistema deve consolidar contagens por status: copiados, sobrescritos, pulados, colisões, erros, cancelados e alvo ausente | Must | 🟡 Soma das contagens igual ao total de itens do `ResultadoCopia` |
| RF-02 | 🟡 O sistema deve listar cada item com status individual e motivo quando aplicável | Must | 🟡 Item com status erro aparece na lista com campo motivo preenchido |
| RF-03 | 🟡 O usuário deve visualizar o relatório na janela do app ao final de toda execução | Must | 🟡 Término concluído, cancelado ou com falha exibe o relatório correspondente |
| RF-04 | 🟡 O sistema deve exibir o relatório parcial quando a execução for cancelada | Must | 🟡 Cancelamento no item K de N exibe K processados + N-K cancelados |
| RF-05 | 🟡 O sistema deve destacar as ocorrências problemáticas antes das bem-sucedidas na exibição | Should | 🟡 Lista de problemas aparece acima do resumo de sucesso |
| RF-06 | 🟡 O sistema deve exibir duração total e horário de início/término da execução | Should | 🟡 Relatório mostra "iniciado em" e "duração" calculados |
| RF-07 | 🟡 O usuário deve poder exportar o relatório para arquivo texto ou CSV na pasta de destino | Could | 🟡 Exportação grava arquivo legível com as mesmas contagens e lista ⚠️ ABERTO: formato final, ver OQ-02 |

### 6.2 Fluxo Principal (Happy Path)

1. O motor conclui o lote e entrega o `ResultadoCopia`
2. O sistema consolida contagens por status
3. O sistema monta a lista por pasta (problemas primeiro, com motivos)
4. O usuário visualiza o relatório na janela
5. Resultado: conferência do lote concluída sem inspeção manual do destino

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — execução cancelada:**
1. O motor para no item K com status cancelado nos restantes
2. O sistema consolida o parcial
3. O relatório exibe copiados até K, cancelados K+1..N

**Fluxo Alternativo B — exportação do relatório:**
1. O usuário aciona exportar
2. O sistema grava o relatório em texto/CSV no destino
3. A mensagem confirma o caminho do arquivo gerado

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| RNF-01 | Performance de consolidação | 🟡 < 2 s para 500 itens | 🟡 operação em memória |
| RNF-02 | Legibilidade | 🟡 texto simples, sem dependência de fontes externas | 🟡 público técnico |
| RNF-03 | Compatibilidade | 🟡 Windows 10 e 11 | 🟡 ambiente corporativo |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 área de relatório da janela principal (interface-desktop); estrutura de dados consumida também pelos testes do motor.

**Comportamento esperado:**
🟡 Ao término, exibe resumo (contagens + duração) seguido da lista detalhada; ocorrências problemáticas primeiro; exportação opcional por botão.

**Estados da UI:**
- Estado vazio: 🟡 nenhuma execução ainda → área com orientação "execute um lote para ver o relatório"
- Estado de carregamento: 🟡 consolidação imediata ao término (sem espera perceptível)
- Estado de erro: 🟡 término por falha de infraestrutura → relatório parcial + mensagem da falha
- Estado de sucesso: 🟡 resumo + lista completa exibidos

---

## 9. Modelo de Dados

**Entidades novas ou modificadas (em memória):**

```
ResumoExecucao {
  total_itens: número
  por_status: mapa texto -> número    // copiado, sobrescrito, pulado, colisao, erro, cancelado, alvo-ausente
  iniciado_em: data/hora
  concluido_em: data/hora
  duracao_segundos: número
}

RelatorioExecucao {
  resumo: ResumoExecucao
  problemas: lista de ItemCopia        // status <> copiado/sobrescrito
  detalhe: lista de ItemCopia          // todos os itens, ordem de processamento
}
```

**Migrações necessárias:** Não — sem persistência (exportação é arquivo de saída do usuário, não banco).

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|-------------|------|------------------------|
| 🟡 motor-de-copia-renomeacao (entrada `ResultadoCopia`) | Obrigatória | 🟡 sem dados para consolidar; componente sem função |
| 🟡 interface-desktop (exibição) | Obrigatória | 🟡 consolidação ainda testável isolada; exibição indisponível |
| 🟡 Sistema de arquivos local (exportação) | Opcional | 🟡 exportação falha com mensagem; relatório permanece na tela |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---------|---------|----------------------|
| EC-01: 🟡 lote termina 100% problemático | 🟡 todas as pastas com erro/alvo ausente | 🟡 relatório exibe 0 copiados e a lista completa de motivos, sem omitir nada |
| EC-02: 🟡 lote vazio | 🟡 origem sem subpastas válidas | 🟡 aviso explícito "nenhuma pasta processada" em vez de relatório com zeros |
| EC-03: 🟡 cancelamento imediato | 🟡 cancelado antes da primeira pasta | 🟡 relatório parcial com todos os itens cancelados |
| EC-04: 🟡 exportação para destino sem permissão | 🟡 falha de escrita no arquivo exportado | 🟡 mensagem de erro clara; relatório permanece visível na tela |
| EC-05: 🟡 falha de infraestrutura no meio do lote | 🟡 indisponibilidade do destino/share | 🟡 relatório parcial dos itens processados + mensagem da falha de origem |

---

## 12. Segurança e Privacidade

- **Autenticação:** 🟡 nenhuma — aplicativo local de desktop
- **Autorização:** 🟡 escrita do arquivo exportado limitada às permissões do usuário Windows
- **Dados sensíveis:** 🟡 nenhum identificado — conteúdo limitado a nomes de pastas, status e mensagens de erro do sistema de arquivos
- **Auditoria:** 🟡 o relatório exportado, quando gerado, cumpre o papel de registro da execução

---

## 13. Plano de Rollout

- **Estratégia:** 🟡 entrega empacotada no executável único do app (componente interno)
- **Como reverter (rollback):** 🟡 remover o executável; arquivos exportados pertencem ao usuário
- **Monitoramento pós-deploy:** 🟡 conferência das contagens do relatório contra o destino no primeiro lote real

---

## 14. Open Questions

| # | Pergunta | Impacto | Dono | Prazo |
|---|---------|---------|------|-------|
| OQ-01 | 🟡 Formato de exibição na tela: lista rolável simples ou tabela com colunas? | Baixo | Sandoval | antes do coding |
| OQ-02 | 🟡 Exportação em texto simples ou CSV (delimitador vírgula ou ponto e vírgula pt-br)? | Médio | Sandoval | antes do coding |
| OQ-03 | 🟡 Manter os últimos N relatórios em arquivo automático no destino? | Baixo | Sandoval | pós-MVP |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão | Alternativas consideradas | Racional |
|---------|--------------------------|----------|
| 🟡 Relatório sempre visível, inclusive em falha/cancelamento | exibir só no sucesso | 🟡 o parcial é o que permite retomar sem repetir o lote inteiro |
| 🟡 Problemas primeiro na exibição | ordem cronológica simples | 🟡 o que exige ação do técnico aparece primeiro |
| 🟡 Exportação opcional (Could), não automática | gravar sempre em arquivo | 🟡 evita sujeira no destino quando o usuário só quer conferir |

---

## Apêndice

### Referências
- 🟡 prd.md (seções 3 e 4); personas.md (jornada, passo 7); motor-de-copia-renomeacao.md

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
