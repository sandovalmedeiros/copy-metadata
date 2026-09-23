# Legacy Impact: Copiador de Metadados GeoNetwork (MVP)

> **Feature greenfield, sem legado pré-existente. Âncora: prd.md + specs SDD.**
> Identificador: `001-copiador-metadados-geonetwork`
> Data: 2026-09-23
> Política de edição no momento da execução: `allowLegacyEdits: true`, `allowedPaths: ["app/**", "tests/**", "copiador.spec"]` — todas as escritas fora das pastas do Reversa ocorreram exclusivamente nesses globs; nenhum arquivo pré-existente foi modificado ou removido.

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|-----------------|------------|------|------------|---------------|
| `app/__init__.py` | pacote da aplicação | componente-novo | LOW | Criação do pacote (T001) |
| `app/main.py` | interface-desktop (entry point) | componente-novo | LOW | Entry point `python -m app.main` + mainloop (T001/T010) |
| `app/modelos.py` | contratos (sdd/*#9) | componente-novo | LOW | Dataclasses compartilhadas scanner→motor→relatório (T002) |
| `app/scanner.py` | scanner-de-pastas | componente-novo | LOW | Varredura nível 1, captura `nome_novo`, alvo por caminho relativo (T006) |
| `app/motor.py` | motor-de-copia-renomeacao | componente-novo | LOW | Cópia em lote `<uuid>.xml`, sobrescrita, colisão, cancelamento (T007) |
| `app/relatorio.py` | relatorio-de-execucao | componente-novo | LOW | Consolidação, problemas com motivo, exportação (T008) |
| `app/interface.py` | interface-desktop | componente-novo | LOW | Janela Tkinter, worker thread, política de sobrescrita, estados (T009/T013) |
| `tests/test_scanner.py` | verificação/scanner | componente-novo | LOW | 10 testes unittest (T003) |
| `tests/test_motor.py` | verificação/motor | componente-novo | LOW | 10 testes unittest (T004) |
| `tests/test_relatorio.py` | verificação/relatório | componente-novo | LOW | 6 testes unittest (T005) |
| `copiador.spec` | empacotamento (spec interface, G-03) | componente-novo | LOW | PyInstaller one-dir, decisão D-07 (T011) |

## Diff conceitual por componente

- **scanner-de-pastas** (`app/scanner.py`): varredura do primeiro nível da origem; derivação do caminho relativo do arquivo-alvo a partir da seleção (D-04); validação de nome Windows (RF-08); status por pasta com motivo; `ScannerErro` para origem inacessível sem enumeração parcial (EC-01).
- **motor-de-copia-renomeacao** (`app/motor.py`): cópia sequencial `shutil.copyfile` + verificação de tamanho (RN-05/D-08); criação do destino; política de sobrescrita sobrescrever/pular (D-05); detecção de UUID duplicado como colisão; continuidade após falha individual (RN-03); cancelamento por `threading.Event` preservando cópias (RN-06); pastas não processáveis da varredura atravessam para o relatório.
- **relatorio-de-execucao** (`app/relatorio.py`): consolidação por status (soma fecha com total), problemas primeiro com motivo (RF-05), duração calculada, formatação texto única para tela e exportação, arquivo `relatorio-execucao-*.txt` com BOM para leitura no Bloco de Notas.
- **interface-desktop** (`app/interface.py`): janela única com três seletores de diálogo nativo (filtro `*.xml`); Executar habilitado só com campos completos e dica do que falta; worker thread + `queue.Queue` drenada por `after()` (D-03); pergunta única de sobrescrita apenas quando há `.xml` no destino; cancelamento; estados vazio/carregamento/erro/sucesso conforme spec §8; confirmação ao fechar com lote ativo.

## Preservadas

> Vazia por definição — feature greenfield: não existem regras 🟢 de legado a preservar (`_reversa_sdd/domain.md` não existe).

## Modificadas

> Vazia por definição — nenhum arquivo pré-existente do projeto foi modificado ou removido (verificação: política de edição respeitada; somente arquivos novos nos globs liberados).
