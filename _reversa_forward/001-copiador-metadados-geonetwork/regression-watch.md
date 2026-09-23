# Regression Watch: Copiador de Metadados GeoNetwork (MVP)

> Identificador: `001-copiador-metadados-geonetwork`
> Data: 2026-09-23
> Feature greenfield: sem regras 🟢 extraídas de código anterior, o watch principal inicia vazio. Os RFs implementados ficam registrados como **Observações** (sem peso de regressão) até que uma futura extração `/reversa` sobre o código novo os confirme como 🟢.

## Watch principal

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|-------------------------|------------------------------|---------------------|-------------------|
| _n/a_ | — | — | — | — |

## Histórico de re-extrações

> Vazio — nenhuma re-extração `/reversa` executada desde a entrega desta feature.

## Arquivadas

> Vazio.

## Observações (RFs implementados — IDs estáveis)

Estes itens NÃO têm peso de regressão enquanto não confirmados 🟢 por extração futura. Uma re-extração deve promovê-los ao watch principal conforme confirmados no código.

| ID | Origem (spec, RF) | Comportamento entregue |
|----|------------------|------------------------|
| O001 | sdd/scanner-de-pastas.md RF-01/RF-02 | Enumera todas as subpastas diretas da origem, capturando cada nome como `nome_novo` |
| O002 | sdd/scanner-de-pastas.md RF-03 | Deriva o caminho relativo do arquivo-alvo a partir da seleção do usuário (D-04) |
| O003 | sdd/scanner-de-pastas.md RF-05/RF-06 | Pasta sem alvo registrada com motivo; nenhuma pasta omitida da saída |
| O004 | sdd/scanner-de-pastas.md RF-07/RF-08 | Arquivos soltos ignorados; nome de pasta invalidado como nome Windows |
| O005 | sdd/motor-de-copia-renomeacao.md RF-01 | Cópia de cada pasta válida como `<nome_pasta>.xml` com conteúdo idêntico |
| O006 | sdd/motor-de-copia-renomeacao.md RF-02 | Pasta de destino criada quando inexistente |
| O007 | sdd/motor-de-copia-renomeacao.md RF-03 | Política de sobrescrita aplicada sem sobrescrita silenciosa (padrão: perguntar — D-05) |
| O008 | sdd/motor-de-copia-renomeacao.md RF-04/RF-06 | Colisão de UUID detectada; falha individual registrada sem abortar o lote (RN-03) |
| O009 | sdd/motor-de-copia-renomeacao.md RF-06 | Cancelamento preserva cópias concluídas (RN-06) |
| O010 | sdd/relatorio-de-execucao.md RF-01/RF-02 | Contagens por status fecham com o total; problemas listados com motivo |
| O011 | sdd/relatorio-de-execucao.md RF-03/RF-04 | Relatório exibido em todo término, inclusive parcial de cancelamento |
| O012 | sdd/relatorio-de-execucao.md RF-07 | Exportação opcional para `relatorio-execucao-*.txt` no destino |
| O013 | sdd/interface-desktop.md RF-01–RF-04 | Seleção por diálogos nativos; Executar habilitado só com campos completos |
| O014 | sdd/interface-desktop.md RF-06/RF-07/RF-10 | Progresso N de M; cancelamento em <-2 s; controles bloqueados na execução |
| O015 | sdd/interface-desktop.md RF-09 | Validações com mensagens específicas (origem inacessível, alvo fora da origem) |
| O016 | sdd/interface-desktop.md RF-11 | Empacotamento viável via `copiador.spec` (one-dir, sem runtime instalado) |
