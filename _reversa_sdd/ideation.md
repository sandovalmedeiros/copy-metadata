# Ideation, Demanda Geonetwork

> Selo 🟡 PLANEJADO em todos os itens, sujeito a validação.

## Brief original

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

Fontes complementares do brief: seção "Decisões da entrevista única" (escopo expresso, operação em lote, stack Python + GUI desktop) e seção "Contexto inferido".

## Problema

🟡 **Inferido do documento de demanda — validar com o usuário.** Extrair metadados de uma exportação do GeoNetwork exige, hoje, navegar manualmente pasta por pasta dentro da árvore exportada (`<uuid>\metadata\`), copiar o `metadata.xml` de cada uma e renomeá-lo manualmente para `<uuid>.xml`. Com dezenas ou centenas de pastas UUID por exportação, o processo é repetitivo, lento e propenso a erro (digitar/colar UUID errado, renomear sobre arquivo existente, esquecer pastas). Quem sente: a equipe técnica de geoprocessamento (Digeo / IDE Bahia), no momento de preparar os metadados exportados para importação em outra instância do GeoNetwork.

## Valor entregue

🟡 Em uma única operação com interface gráfica, transformar N pastas exportadas em N arquivos `<uuid>.xml` prontos para uso/importação — o usuário indica origem, arquivo-alvo e destino, e o app faz a varredura, a cópia e a renomeação em lote, eliminando a navegação e a renomeação manuais.

## Alternativas existentes

🟡 `[INDEFINIDO, validar com usuário]` — o usuário não mencionou alternativas. Nota: o processo manual no Windows Explorer é a alternativa implícita descrita na própria demanda (passos 3–5 feitos à mão); não foi feita pesquisa de ferramentas ou scripts existentes para esta tarefa.

## Público-alvo (bruto)

🟡 Técnico(s) de geoprocessamento responsáveis pelo cadastro e manutenção de metadados na infraestrutura de dados espaciais (ex.: Francisco, citado no path `S:\Digeo\PUBLICO\Francisco\`), usuários de desktop Windows com acesso ao share de rede corporativo.

## Métricas de sucesso

🟡 `[INDEFINIDO, validar com usuário]` — não respondido na entrevista. Candidatas a validar (sugestão, não decisão): (a) 100% das pastas UUID com arquivo-alvo presente resultam em `<uuid>.xml` no destino, com relatório de exceções; (b) tempo total de processamento de um lote típico de exportação; (c) zero renomeações manuais necessárias pós-execução.

## Premissas a validar

🟡 1. **Estrutura interna fixa** — toda pasta UUID da exportação contém o arquivo-alvo no mesmo caminho relativo (ex.: `metadata\metadata.xml`). Se a estrutura variar entre pastas, a cópia em lote falha parcialmente.
🟡 2. **Nome de pasta = identificador único e seguro** — o nome de cada pasta (UUID) é único dentro do lote e válido como nome de arquivo Windows. Duplicatas gerariam sobrescrita; caracteres inválidos gerariam erro.
🟡 3. **Acesso e permissões** — a máquina do usuário (desktop Windows) enxerga o share de origem (ex.: `S:\`) e tem permissão de leitura nele e de escrita na pasta de destino (ex.: `C:\metadados_geonetwork`).

## Notas

🟡 Decisões já tomadas na entrevista única (2026-09-23): operação **em lote** (todas as pastas UUID do path de origem); stack **Python + GUI desktop** (sugestão: Tkinter, empacotável em `.exe`); pipeline expresso até o código.
🟡 Pontos em aberto que o PRD deve resolver ou marcar `[INDEFINIDO]`: política de sobrescrita quando `<uuid>.xml` já existir no destino (sobrescrever / pular / perguntar); comportamento quando uma pasta UUID não contiver o arquivo-alvo (ignorar com relatório vs. abortar); se o arquivo-alvo indicado pelo usuário define apenas o *nome* buscado dentro de cada pasta (ex.: `metadata.xml` dentro de `metadata\`) ou um caminho relativo completo.
🟡 O documento de demanda descreve "o usuário vai indicar qual o nome do arquivo .xml ... navegando através da interface" — interpretado como seleção do arquivo-representante via diálogo de navegação, a partir do qual o app deriva o nome/caminho relativo a aplicar em todas as pastas do lote.

---
Gerado por reversa-ideator em 2026-09-23T11:38:30-03:00
Fonte: newproject-brief.md
