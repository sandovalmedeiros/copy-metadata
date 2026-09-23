# Adendo 001 — Copiador de Metadados GeoNetwork (MVP)

> **Feature:** `001-copiador-metadados-geonetwork`
> **Data:** 2026-09-23T13:50:00-03:00
> **Cenário:** greenfield (extração ancorada em `prd.md` + specs `sdd/`; não há artefatos de legado)

## Vigência

Vigente desde 2026-09-23.

## Resumo da entrega

Entrega o MVP completo do PRD: aplicativo desktop Windows (Python + Tkinter) que lê as pastas UUID de uma exportação do GeoNetwork, copia o arquivo `.xml` alvo de cada uma em lote e salva renomeado como `<uuid>.xml` no destino indicado pelo usuário, com progresso, cancelamento, política de sobrescrita e relatório de resultado (objetivo consolidado do `requirements.md` da feature, 13 RFs + 7 RNs). Foram concluídas **14 de 14 ações** do `actions.md` (fases Preparação → Polimento), com suíte de 26 testes `unittest` verde, build PyInstaller one-dir validado por smoke e pacote de entrega versionado (`CopiadorMetadados-v1.0.0-2026-09-23.zip`, publicado no repositório Git).

## Impacto por artefato da extração

| Artefato | Seção | Tipo de impacto | Delta |
|---|---|---|---|
| `_reversa_sdd/prd.md` | §4 Escopo (in) | componente-novo | Todo o escopo do MVP foi implementado e testado — leia a lista de escopo como **entregue** (13 RFs mapeados no `requirements.md` da feature) |
| `_reversa_sdd/prd.md` | §9 Critérios de aceite | componente-novo | Os 5 critérios Dado/Quando/Então têm cobertura direta na suíte `tests/` e no smoke automatizado; critério do `.exe` sem runtime validado no build one-dir |
| `_reversa_sdd/sdd/scanner-de-pastas.md` | §6 Requisitos Funcionais | componente-novo | RF-01–RF-08 implementados em `app/scanner.py` (varredura nível 1, `nome_novo`, caminho relativo derivado — decisão D-04; ver observações O001–O004 do regression-watch) |
| `_reversa_sdd/sdd/motor-de-copia-renomeacao.md` | §6 Requisitos Funcionais | componente-novo | RF-01–RF-08 implementados em `app/motor.py` (lote `<uuid>.xml`, sobrescrita com padrão "perguntar 1×/execução" — D-05, colisão, continuidade, cancelamento; ver O005–O009) |
| `_reversa_sdd/sdd/relatorio-de-execucao.md` | §6 Requisitos Funcionais | componente-novo | RF-01–RF-07 implementados em `app/relatorio.py` (contagens que fecham com o total, problemas com motivo primeiro, exportação `.txt` opcional; ver O010–O012) |
| `_reversa_sdd/sdd/interface-desktop.md` | §6 Requisitos Funcionais e §8 Design | componente-novo | RF-01–RF-11 implementados em `app/interface.py` + `app/main.py` (worker thread + fila `after()` — D-03, estados da UI §8; ver O013–O015); empacotamento em `copiador.spec` (O016) |

Nenhum artefato pré-existente da extração foi alterado: todos os impactos são criações (cenário greenfield — os tipos `regra-alterada`/`regra-removida` não se aplicam).

## Regras sob vigilância

Nenhum watch item ativo (`W001…`): feature greenfield, o watch principal do `_reversa_forward/001-copiador-metadados-geonetwork/regression-watch.md` inicia vazio por definição. As observações **O001–O016** do mesmo arquivo registram os RFs implementados e ganham peso de regressão quando uma futura re-extração `/reversa` os confirmar como 🟢 no código.

## Fontes

- `_reversa_forward/001-copiador-metadados-geonetwork/legacy-impact.md`
- `_reversa_forward/001-copiador-metadados-geonetwork/regression-watch.md`
- `_reversa_forward/001-copiador-metadados-geonetwork/requirements.md`
- `_reversa_forward/001-copiador-metadados-geonetwork/progress.jsonl`
- `_reversa_forward/001-copiador-metadados-geonetwork/actions.md`
