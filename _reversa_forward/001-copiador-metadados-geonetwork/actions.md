# Actions: Copiador de Metadados GeoNetwork (MVP)

> Identificador: `001-copiador-metadados-geonetwork`
> Data: 2026-09-23
> Roadmap: `_reversa_forward/001-copiador-metadados-geonetwork/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 14 |
| Paralelizáveis (`[//]`) | 7 |
| Maior cadeia de dependência | 7 (T001→T002→T003→T006→T009→T010→T011) |
| Concluídas | **14 de 14** |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Criar pacote `app/` com `__init__.py` e `main.py` (entry point vazio executável via `python -m app.main`) | - | - | `app/main.py` | 🟢 | `[X]` |
| T002 | Criar `app/modelos.py` com as dataclasses dos contratos entre módulos: `PastaScandeada`, `ResultadoVarredura`, `ItemCopia`, `ResultadoCopia`, `ResumoExecucao`, `RelatorioExecucao` | T001 | - | `app/modelos.py` | 🟢 | `[X]` |

## Fase 2, Testes

> Suíte em `unittest` (stdlib) para manter o projeto livre de dependências de runtime e de teste.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T003 | Escrever `tests/test_scanner.py`: enumeração de subpastas diretas, captura de `nome_novo`, derivação de caminho relativo, alvo ausente, arquivos soltos ignorados, nome inválido/reservado | T002 | `[//]` | `tests/test_scanner.py` | 🟡 | `[X]` |
| T004 | Escrever `tests/test_motor.py`: lote feliz (N cópias `<uuid>.xml`), destino criado, sobrescrita sobrescrever/pular, colisão de UUID, falha individual não aborta, cancelamento preserva feitas | T002 | `[//]` | `tests/test_motor.py` | 🟡 | `[X]` |
| T005 | Escrever `tests/test_relatorio.py`: soma de contagens fecha com total, problemas com motivo primeiro, parcial de cancelamento, exportação para arquivo texto | T002 | `[//]` | `tests/test_relatorio.py` | 🟡 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T006 | Implementar `app/scanner.py`: varredura do primeiro nível da origem, captura do nome, validação de nome Windows, localização do alvo pelo caminho relativo derivado, status por pasta com motivo | T001, T002, T003 | `[//]` | `app/scanner.py` | 🟡 | `[X]` |
| T007 | Implementar `app/motor.py`: cópia em lote `<nome_pasta>.xml`, criação do destino, política de sobrescrita, detecção de colisão, continuidade após falha, cancelamento por `threading.Event`, verificação de tamanho | T001, T002, T004 | `[//]` | `app/motor.py` | 🟡 | `[X]` |
| T008 | Implementar `app/relatorio.py`: consolidação por status, lista de problemas com motivo, tempos/duração, formatação texto e exportação opcional no destino | T001, T002, T005 | `[//]` | `app/relatorio.py` | 🟡 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T009 | Implementar `app/interface.py`: janela Tkinter com três seletores (diálogos nativos, filtro `*.xml`), validação e habilitação de Executar, worker thread + fila `after()` para progresso, botão cancelar (< 2 s), diálogo de política de sobrescrita, exibição do relatório, bloqueio de controles na execução, confirmação ao fechar durante lote | T006, T007, T008 | - | `app/interface.py` | 🟡 | `[X]` |
| T010 | Ligar `app/main.py`: instanciar a janela e entrar no mainloop | T009 | - | `app/main.py` | 🟢 | `[X]` |
| T011 | Criar `copiador.spec` (PyInstaller, modo one-dir) apontando o entry point e incluindo o pacote `app/` | T010 | - | `copiador.spec` | 🟡 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T012 | Executar a bateria completa (`python -m unittest discover -s tests`) e corrigir falhas até verde | T009, T010 | - | `tests/` | 🟢 | `[X]` |
| T013 | Revisar estados e mensagens da interface conforme spec interface-desktop §8 (estado vazio, carregamento, erro, sucesso; mensagens específicas de origem inacessível) | T009 | `[//]` | `app/interface.py` | 🟡 | `[X]` |
| T014 | Smoke manual guiado pelo `onboarding.md` com lote de teste sintético (3 pastas + 1 sem alvo; conferir destino, relatório, sobrescrita e cancelamento) | T012, T013 | - | `app/` | 🟢 | `[X]` |

## Notas de execução

- **T004/T005 vs. implementação:** um defeito real de import (`ALVO_AUSENTE` não importado em `tests/test_motor.py`) foi detectado pelos diagnsticos estáticos durante a Fase 2 e corrigido antes da suíte rodar; `datetime` não usado foi removido.
- **T010:** `app/main.py` foi criado já ligado em T001 (import de `JanelaPrincipal` + mainloop); T010 confirmou o funcionamento via suíte e smoke.
- **T012:** suíte verde na primeira execução — 26 testes, 0 falhas (0,133 s); re-executada após os ajustes de T013, ainda verde (26/26, 0,096 s).
- **T013:** corrigiu defeito real de estado da UI (rótulo permanecia "Executando…" após concluir — condição invertida) e acrescentou o cabeçalho "Execução CANCELADA…" no relatório parcial; flag `_falhou` preserva o estado de erro.
- **T014:** executado de forma **automatizada** (pipeline completo scanner→motor→relatório + construção/destruição da GUI sem mainloop): 5 passos OK. O teste visual interativo (diálogos nativos, barra de progresso) permanece como passo humano guiado pelo `onboarding.md`.
- **Ambiente:** rodar suíte e scripts sempre **a partir da raiz do projeto** (`python -m unittest discover -s tests`). O `PYTHONPATH` global desta máquina aponta para outro projeto com pacote `app` (`D:\chat-mapoteca`) — em modo script, inserir a raiz no `sys.path` explicitamente (como o smoke fez).

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-09-23 | Versão inicial gerada por `/reversa-to-do` (pipeline /reversa-new expresso) | reversa-to-do |
| 2026-09-23 | 14/14 ações concluídas por `/reversa-coding`; notas de execução registradas | reversa-coding |
