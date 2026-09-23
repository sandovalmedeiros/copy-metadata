# PRD: Demanda Geonetwork — utilitário de cópia e renomeação de metadados em lote

> Selo 🟡 PLANEJADO. Documento gerado a partir de ideation + personas.

**Versão:** 1.0
**Data:** 2026-09-23T11:45:00-03:00
**Autor:** reversa-drafter
**Status:** rascunho
**Documento-fonte da demanda:** `Demanda Geonetwork.pdf` (23/09/2026)

---

## 1. Problema

🟡 Exportações do GeoNetwork chegam como uma pasta por lote (ex.: `IDEBAHIA-CADASTRO-2026-09-22T150904`) contendo uma subpasta por registro de metadado, nomeada com o UUID do registro (ex.: `0b8733a3-93ba-4d18-aa6a-a63782546898`), dentro da qual o arquivo XML está aninhado (ex.: `<uuid>\metadata\metadata.xml`). Para usar ou importar esses metadados em outra instância, é necessário extrair cada XML e renomeá-lo para `<uuid>.xml` — hoje feito à mão, pasta por pasta, no Windows Explorer: trabalho repetitivo, lento e propenso a erro (UUID digitado errado, pastas esquecidas, sobrescritas acidentais).

### Quem sente
🟡 O técnico de geoprocessamento responsável pelo cadastro de metadados da IDE (Digeo / IDE Bahia), no momento em que prepara um lote exportado para importação — tipicamente durante o expediente, num desktop Windows com acesso ao share de rede onde a exportação foi gravada.

---

## 2. Personas-alvo

🟡 Referência completa em [`personas.md`](./personas.md). Resumo:

- **Técnico de Geoprocessamento**: 🟡 perfil técnico intermediário (GIS/GeoNetwork/Windows, não programador); dor principal: copiar e renomear manualmente cada `metadata.xml` para `<uuid>.xml`, pasta por pasta, em lotes de exportação.

---

## 3. Métricas de sucesso

🟡 A entrevista não fixou métricas; as linhas abaixo são **propostas derivadas da demanda** — alvos a validar com o usuário.

| Métrica | Unidade | Alvo | Prazo |
|---|---|---|---|
| 🟡 Taxa de conversão do lote (pastas UUID com arquivo-alvo que geram `<uuid>.xml` no destino) | % do lote | 100%, com exceções listadas em relatório | 🟡 [a definir] |
| 🟡 Retrabalho manual pós-execução (renomeações manuais necessárias) | renomeações | 0 | 🟡 [a definir] |
| 🟡 Tempo de processamento de um lote típico de exportação | minutos | 🟡 [a definir com usuário] | 🟡 [a definir] |

---

## 4. Escopo (in)

🟡 Itens derivados da demanda (passos 1–5 do PDF), da decisão de operação **em lote** e da jornada da persona:

- 🟡 Selecionar, via interface, a **pasta de origem** do lote (ex.: `S:\Digeo\PUBLICO\Francisco\IDEBAHIA-CADASTRO-2026-09-22T150904`)
- 🟡 Varrer as **subpastas** da origem (uma pasta por registro), capturando o nome de cada uma como `nome_novo` (UUID)
- 🟡 Indicar, **navegando pela interface**, o arquivo `.xml` alvo (ex.: `metadata.xml` dentro de `<uuid>\metadata\`), do qual o app deriva o nome/caminho relativo aplicado a todas as pastas do lote
- 🟡 Selecionar, via interface, a **pasta de destino** (ex.: `C:\metadados_geonetwork`)
- 🟡 **Copiar em lote**: para cada pasta UUID, copiar o arquivo-alvo e salvar no destino renomeado como `<nome_novo>.xml`
- 🟡 Exibir **progresso** da operação durante a execução
- 🟡 Exibir **relatório de resultado**: arquivos copiados, pastas sem arquivo-alvo, erros (com motivo)
- 🟡 Tratar arquivo `<uuid>.xml` já existente no destino segundo **política de sobrescrita** (padrão proposto: perguntar/avisar — política final a validar)
- 🟡 Ser um **aplicativo desktop Windows com GUI** (Python + Tkinter sugerido), empacotável em `.exe`

---

## 5. Não-objetivos (out)

🟡 Inferidos do escopo da demanda — validar com o usuário:

- 🟡 O app **não importa** os metadados no GeoNetwork (só prepara os arquivos `<uuid>.xml`)
- 🟡 O app **não valida nem edita** o conteúdo XML dos metadados
- 🟡 O app **não monitora** pastas em tempo real (execução sob demanda, disparada pelo usuário)
- 🟡 O app **não gerencia** permissões de rede nem montagem do share de origem

---

## 6. Restrições

| Tipo | Descrição |
|---|---|
| 🟡 Técnica | 🟡 Python 3 + GUI desktop (Tkinter sugerido); executa em desktop Windows; deve ler paths de rede mapeados (ex.: `S:\`) e gravar em pasta local; empacotável em `.exe` (ex.: PyInstaller) |
| 🟡 Prazo | 🟡 [INDEFINIDO, validar com usuário] |
| 🟡 Compliance | 🟡 [INDEFINIDO, validar com usuário] — nota: a demanda envolve metadados públicos de IDE; nenhum dado pessoal foi identificado no material-fonte |
| 🟡 Orçamento | 🟡 [INDEFINIDO, validar com usuário] |

---

## 7. Dependências externas

- 🟡 Acesso de leitura ao **share de rede corporativo** onde ficam as exportações (ex.: `S:\Digeo\...`) — dependência de infraestrutura, não de API
- 🟡 Nenhuma API ou serviço externo identificado

---

## 8. Riscos

| Risco | Impacto | Probabilidade | Mitigação proposta |
|---|---|---|---|
| 🟡 Estrutura interna variar entre pastas do lote (subpasta/arquivo-alvo em caminho diferente) | 🟡 alto | 🟡 média | 🟡 Derivar caminho relativo completo do arquivo selecionado (não só o nome) e listar em relatório as pastas onde o arquivo não foi encontrado |
| 🟡 Colisão de nome (UUID duplicado no lote ou arquivo já existente no destino) | 🟡 médio | 🟡 baixa | 🟡 Detectar duplicatas antes de copiar e aplicar política de sobrescrita explícita (avisar por padrão) |
| 🟡 Share de origem lento ou indisponível durante o lote | 🟡 médio | 🟡 média | 🟡 Mensagens de erro claras, botão cancelar, relatório parcial do que já foi copiado |
| 🟡 Nome de pasta inválido como nome de arquivo Windows | 🟡 médio | 🟡 baixa | 🟡 Sanitização/validação do nome com aviso no relatório |
| 🟡 Empacotamento `.exe` (antivírus corporativo, tamanho do bundle) | 🟡 baixo | 🟡 média | 🟡 Usar PyInstaller com build enxuto e instrução de uso; alternativa: rodar via Python instalado |

---

## 9. Critérios de aceite (alto nível)

- 🟡 **Dado** um lote de origem com N pastas UUID, cada uma contendo o arquivo-alvo no caminho relativo indicado, **Quando** o usuário seleciona origem, arquivo-alvo e destino e executa a cópia, **Então** o destino passa a conter N arquivos `<uuid>.xml` com conteúdo idêntico ao arquivo-alvo de cada pasta.
- 🟡 **Dado** uma ou mais pastas UUID sem o arquivo-alvo, **Quando** o lote é executado, **Então** o app conclui as demais pastas, não trava e lista as pastas problemáticas no relatório com o motivo.
- 🟡 **Dado** um arquivo `<uuid>.xml` já existente no destino, **Quando** o lote alcança a pasta correspondente, **Então** o app aplica a política de sobrescrita definida e registra a ocorrência no relatório.
- 🟡 **Dado** a origem inacessível (share fora do ar / sem permissão), **Quando** o usuário tenta executar, **Então** o app exibe mensagem de erro clara e permanece utilizável.
- 🟡 **Dado** o app empacotado em `.exe`, **Quando** executado em um desktop Windows corporativo sem Python instalado, **Então** a interface abre e todas as funções operam normalmente.

---

## Pendências de cobertura

🟡 Itens marcados `[INDEFINIDO]` ou "a definir" que precisam de validação humana:

1. **Métricas de sucesso** — alvos e prazos das métricas propostas (seção 3)
2. **Prazo e orçamento** (seção 6)
3. **Compliance** — confirmar ausência de exigências regulatórias (seção 6)
4. **Política de sobrescrita** no destino — sobrescrever / pular / perguntar (seções 4 e 9)
5. **Não-objetivos** — confirmar a lista inferida (seção 5)
6. **Arquivo-alvo** — confirmar se a seleção do usuário define só o *nome* do arquivo (buscado dentro de cada pasta, em qualquer subnível) ou o *caminho relativo completo* (ex.: `metadata\metadata.xml`)

---
Gerado por reversa-drafter em 2026-09-23T11:45:00-03:00
Fontes: ideation.md, personas.md
