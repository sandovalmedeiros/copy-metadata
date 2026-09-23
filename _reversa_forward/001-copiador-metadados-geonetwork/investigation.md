# Investigation: Copiador de Metadados GeoNetwork (MVP)

> Identificador: `001-copiador-metadados-geonetwork`
> Data: 2026-09-23
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Pesquisa de fundo

### Estrutura de exportação do GeoNetwork (MEF) 🟡

O GeoNetwork (catálogo de metadados geoespaciais open source) exporta registros no formato MEF (Metadata Exchange Format): um diretório por registro, nomeado com o UUID do metadado, contendo subpastas padronizadas — tipicamente `metadata/` com o arquivo XML principal (`metadata.xml` para ISO 19115/19139), além de `info/`, `public/` e `private/`. A demanda em tela segue exatamente esse padrão (`IDEBAHIA-CADASTRO-2026-09-22T150904\0b8733a3-...\metadata\metadata.xml`), o que sustenta a decisão D-04 (caminho relativo derivado da seleção).

Referência para consulta: documentação oficial do GeoNetwork — https://docs.geonetwork-opensource.org/

### Restrições de nomes de arquivo no Windows 🟡

O scanner precisa validar nomes de pastas antes de usá-los como nome de arquivo: caracteres proibidos (`< > : " / \ | ? *`), nomes reservados (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`), terminações com ponto/espaço. Sustenta RF de validação de nome e o edge case EC-05 do motor.

Referência: https://learn.microsoft.com/windows/win32/fileio/naming-a-file

### Threading com Tkinter 🟡

Tkinter não é thread-safe: a thread de lote não pode tocar widgets diretamente. Padrão estabelecido: worker thread + `queue.Queue` drenada pela mainloop via `after()` — publicando progresso, resultado e sinal de cancelamento (evento `threading.Event`). Sustenta D-03 e os requisitos de responsividade.

Referência: https://docs.python.org/3/library/tkinter.html (e módulos `threading`, `queue` da stdlib)

### Empacotamento 🟡

PyInstaller one-dir gera uma pasta com executável + DLLs; one-file extrai em temp a cada execução (inicialização mais longa e maior incidência de falsos positivos em antivírus corporativos). Sustenta D-07.

Referência: https://pyinstaller.org/en/stable/operating-mode.html

## 2. Alternativas avaliadas

| Alternativa | Por que foi descartada |
|-------------|------------------------|
| Script CLI (PowerShell/Python) sem GUI | A demanda pede explicitamente seleção "navegando através da interface"; a persona não é programadora (decisão do usuário: Python + GUI) |
| `robocopy` + renomeação em lote no PowerShell | Renomeação por UUID exigiria script ad hoc de qualquer forma; sem progresso/cancelamento/relatório amigáveis; manutenção pela equipe não-programadora inviável |
| PySide6 / wxWidgets | Toolkit mais rico, porém dependência externa pesada para um formulário com barra de progresso; Tkinter cobre o caso (decisão da spec interface) |
| Importação direta via API do GeoNetwork (mef.import) | Fora do escopo da demanda (não-objetivo NG-03 do motor): o pedido é preparar arquivos, não carregá-los |

## 3. Padrões aplicáveis

- **Cores/repositório único**: app pequeno; pacote único `app/` com módulos `scanner.py`, `motor.py`, `relatorio.py`, `interface.py` (+ `main.py`) mapeia 1:1 às specs SDD 🟡
- **Worker + fila de eventos** para UI responsiva (seção 1) 🟡
- **Cópia com verificação de tamanho** (`shutil.copyfile` + `os.path.getsize`) em vez de cópia raw, atendendo RN-05 com custo mínimo 🟡

## 4. Lacunas de investigação

- 🔴 Nenhuma validação empírica ainda da estrutura real das pastas em `S:\Digeo\...` (premissa MEF). Recomendado: usuário executa o app de teste do onboarding contra uma exportação real antes do uso corrente.
- 🟡 Comportamento exato do Tkinter `filedialog` em paths UNC (`\\servidor\share`) varia entre versões de Windows; testar no ambiente alvo (edge case registrado).
