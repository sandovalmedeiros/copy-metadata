# Brief inicial, /reversa-new

> Selo 🟡 PLANEJADO. Documento de entrada do time Code New Project Agents.

**Data:** 2026-09-23T11:38:30-03:00
**Usuário:** Sandoval
**Modo:** expresso (até o código)
**Documento-fonte:** `D:\demanda_francisco\Demanda Geonetwork.pdf` (1 página, 23/09/2026)

## Ideia original

Pedido do usuário: *"Transforme o documento Demanda Geonetwork.pdf em um PRD"* — e, confirmado na entrevista única, seguir o modo expresso completo (da ideia ao código).

### Transcrição integral da demanda (PDF)

> **Demanda Geonetwork – 23/09/2026**
>
> 1 - A aplicação vai ler pastas em um path indicado pelo usuário.
> Exemplo: `S:\Digeo\PUBLICO\Francisco\IDEBAHIA-CADASTRO-2026-09-22T150904`
>
> 2 – A APP vai ler o nome da pasta e guarda numa variável (exemplo: `nome_novo=0b8733a3-93ba-4d18-aa6a-a63782546898`)
>
> 3 - O usuário vai indicar qual o nome do arquivo .xml que será alvo da cópia navegando através da interface. Exemplo:
> Arquivo -> metadata.xml no path: `S:\Digeo\PUBLICO\Francisco\IDEBAHIA-CADASTRO-2026-09-22T150904\0b8733a3-93ba-4d18-aa6a-a63782546898\metadata`
>
> 4 - O usuário vai indicar uma pasta de destino: Exemplo `C:\metadados_geonetwork`
>
> 5 – A APP vai copiar o arquivo indicado e salvar renomeando com o nome do conteúdo da variável, `nome_novo`. Exemplo: `C:\metadados_geonetwork\0b8733a3-93ba-4d18-aa6a-a63782546898.xml`

## Decisões da entrevista única (2026-09-23)

| Pergunta | Resposta |
|---|---|
| Escopo do pipeline | **Expresso até o código** (ideator → researcher → drafter → spec-sdd → requirements → plan → to-do → coding) |
| Operação da cópia | **Lote**: varrer TODAS as pastas UUID do path de origem, copiar o `.xml` alvo de cada uma e salvar como `<uuid>.xml` no destino |
| Stack | **Python + GUI desktop** (interface gráfica simples, ex.: Tkinter; desktop Windows; empacotável em `.exe`) |
| Dúvidas durante a execução | `answer_mode: chat` (pausar e perguntar) — já persistido em `state.json` |

## Contexto inferido 🟡

- A estrutura de pastas segue o padrão de exportação do **GeoNetwork** (pacotes no formato MEF: `<export>/<uuid>/metadata/metadata.xml`), e o objetivo é "achatar" os metadados — tirar cada `metadata.xml` de dentro da árvore e renomeá-lo pelo UUID da pasta pai — tipicamente para importação em massa em outra instância do GeoNetwork.
- Origem típica: share de rede (`S:\Digeo\PUBLICO\Francisco\...`); destino típico: pasta local (`C:\metadados_geonetwork`).
- Público-alvo provável: equipe técnica de geoprocessamento (Digeo/IDE Bahia), em particular o usuário Francisco citado no path.

---
Gerado por /reversa-new em 2026-09-23T11:38:30-03:00
