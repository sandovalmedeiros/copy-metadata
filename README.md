# Copiador de Metadados GeoNetwork

Aplicativo desktop Windows (Python + Tkinter) que transforma uma exportação do GeoNetwork em arquivos individuais prontos para uso: ele varre todas as pastas UUID do lote, copia o arquivo `.xml` alvo de cada uma (ex.: `metadata\metadata.xml`) e salva tudo renomeado como `<uuid>.xml` na pasta de destino — em uma única operação, com progresso, cancelamento e relatório de resultado.

> Origem: demanda "Demanda Geonetwork" (23/09/2026). Projeto greenfield especificado e implementado pelo pipeline Reversa (`/reversa-new` modo expresso).

## O problema que resolve

Exportações do GeoNetwork chegam como uma pasta por lote (ex.: `IDEBAHIA-CADASTRO-2026-09-22T150904`) contendo uma subpasta por registro de metadado, nomeada com o UUID, com o XML aninhado em `<uuid>\metadata\metadata.xml`. Para usar ou importar esses metadados em outra instância é preciso extrair cada XML e renomeá-lo manualmente para `<uuid>.xml` — pasta por pasta, no Windows Explorer. Este app elimina esse trabalho manual (repetitivo e propenso a erro de digitação de UUID).

## Exemplo

```
Origem:  S:\Digeo\PUBLICO\Francisco\IDEBAHIA-CADASTRO-2026-09-22T150904\
           0b8733a3-93ba-4d18-aa6a-a63782546898\metadata\metadata.xml
           11111111-2222-3333-4444-555555555555\metadata\metadata.xml
           ...

Destino: C:\metadados_geonetwork\
           0b8733a3-93ba-4d18-aa6a-a63782546898.xml
           11111111-2222-3333-4444-555555555555.xml
           ...
```

## Requisitos

- Windows 10 ou 11 (64 bits)
- Para executar via Python: **Python 3.10+** com Tkinter (incluído no instalador padrão do Windows) — desenvolvido e testado no 3.13
- Ou apenas o executável empacotado (não exige Python instalado)

## Como executar (desenvolvimento)

A partir da **raiz do projeto**:

```powershell
python -m app.main
```

> ⚠️ Execute sempre a partir da raiz. Se a sua variável `PYTHONPATH` apontar para outro projeto que também tenha um pacote `app`, garanta que a raiz deste projeto venha primeiro no caminho (rodar `python -m` a partir da raiz já resolve).

## Como gerar o .exe

```powershell
pip install pyinstaller
pyinstaller copiador.spec
```

Saída: `dist\CopiadorMetadados\CopiadorMetadados.exe` (pasta completa — modo *one-dir*, inicialização mais rápida e melhor aceitação por antivírus corporativos). Distribua a pasta inteira; não é preciso instalar nada na máquina de destino.

## Como usar

1. **Pasta de origem** — selecione a pasta do lote exportado (ex.: `S:\...\IDEBAHIA-CADASTRO-...`)
2. **Arquivo-alvo (.xml)** — navegue até o arquivo representante dentro de qualquer pasta UUID (ex.: `<uuid>\metadata\metadata.xml`). O app deriva o caminho relativo e aplica a **todas** as pastas do lote
3. **Pasta de destino** — onde os `<uuid>.xml` serão gravados (criada se não existir)
4. **Executar** — habilita só com os três campos preenchidos; a barra mostra o progresso (N de M pastas)
5. **Relatório** — aparece ao final, em qualquer condição (sucesso, cancelamento ou falha): contagens por status e lista de problemas com motivo
6. **Exportar relatório** (opcional) — grava `relatorio-execucao-AAAA-MM-DD-HHMMSS.txt` na pasta de destino

### Comportamentos importantes

- **Sobrescrita**: nunca silenciosa. Se já houver `.xml` no destino, o app pergunta uma vez por execução (sobrescrever tudo / pular existentes / cancelar)
- **Falha individual não aborta**: pasta sem arquivo-alvo, erro de leitura ou nome inválido ficam registradas no relatório e o lote continua
- **Cancelamento**: preserva as cópias já concluídas e gera relatório parcial
- **UUID duplicado no lote**: a segunda ocorrência é marcada como colisão, sem sobrescrever a primeira
- O app **não** valida nem altera o conteúdo XML, e **não** importa nada no GeoNetwork — só prepara os arquivos

### Exemplo de relatório

```
RELATÓRIO DE EXECUÇÃO — Copiador de Metadados GeoNetwork

Iniciado em: 23/09/2026 13:16:20
Duração: 0.0 s
Total de pastas: 4

  alvo ausente: 1
  copiados: 3

PROBLEMAS (1) — revise as pastas abaixo:
  ffffffff-0000-0000-0000-000000000000 | alvo-ausente | alvo ausente: metadata\metadata.xml não encontrado na pasta
```

## Estrutura do projeto

```
app/
  main.py        # entry point (python -m app.main)
  modelos.py     # contratos de dados entre os módulos
  scanner.py     # varredura da origem: pastas UUID + localização do alvo
  motor.py       # cópia em lote, sobrescrita, colisão, cancelamento
  relatorio.py   # consolidação, formatação e exportação
  interface.py   # janela Tkinter: seletores, progresso, relatório
tests/           # suíte unittest (26 testes)
copiador.spec    # spec do PyInstaller (one-dir)
```

Documentação de especificação (pipeline Reversa): `PRD` e specs SDD em `_reversa_sdd/`; requisitos, roadmap e artefatos da entrega em `_reversa_forward/001-copiador-metadados-geonetwork/` (incluindo `onboarding.md` com roteiro de teste passo a passo).

## Testes

```powershell
python -m unittest discover -s tests
```

26 testes cobrindo scanner (enumeração, caminho relativo, alvo ausente, nomes inválidos), motor (lote, sobrescrita, colisão, falha individual, cancelamento) e relatório (contagens, problemas, exportação).

## Notas

- Ferramenta interna (demanda Digeo / IDE Bahia); sem dados pessoais processados
- Decisões de design e premissas abertas: ver `_reversa_forward/001-copiador-metadados-geonetwork/roadmap.md` (seção Premissas)
