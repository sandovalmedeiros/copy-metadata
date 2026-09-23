# Personas e Jornadas

> Selo 🟡 PLANEJADO em todos os itens.

## Persona 1: Técnico de Geoprocessamento
- **Perfil:** 🟡 Técnico de geoprocessamento responsável pelo cadastro e manutenção de metadados da infraestrutura de dados espaciais (Digeo / IDE Bahia), usuário de desktop Windows corporativo com acesso ao share de rede (arquétipo inspirado em "Francisco", citado no path de origem).
- **Contexto:** 🟡 Durante o expediente, recebe ou gera lotes de exportação do GeoNetwork no share de rede (ex.: `S:\Digeo\PUBLICO\Francisco\IDEBAHIA-CADASTRO-2026-09-22T150904`, com uma pasta UUID por registro de metadado) e precisa preparar esses arquivos para importação em outra instância — é nesse momento que o problema aparece.
- **Nível técnico:** 🟡 Intermediário — proficiente em GIS, GeoNetwork e Windows; não necessariamente programador (por isso a demanda pede aplicação com interface gráfica, e não script de linha de comando).
- **Dor principal:** 🟡 Ter de navegar manualmente pasta por pasta UUID, copiar o `metadata.xml` de cada uma e renomeá-lo para `<uuid>.xml` — trabalho repetitivo, lento e propenso a erro de renomeação com UUIDs.
- **Objetivo final:** 🟡 Manter o fluxo de metadados da IDE íntegro e ágil — entregar lotes completos e corretos para importação sem esforço manual e sem erros.

### Jornada principal
1. 🟡 Exportar ou receber o lote de metadados do GeoNetwork em pasta no share de rede (ex.: `IDEBAHIA-CADASTRO-<timestamp>`)
2. 🟡 Abrir o aplicativo no desktop Windows
3. 🟡 Indicar a pasta de origem do lote no share (ex.: `S:\Digeo\PUBLICO\Francisco\IDEBAHIA-CADASTRO-...`)
4. 🟡 Navegar pela interface e selecionar o arquivo `.xml` representante do lote (ex.: `metadata.xml` dentro de `<uuid>\metadata\`)
5. 🟡 Indicar a pasta de destino (ex.: `C:\metadados_geonetwork`)
6. 🟡 Executar a cópia em lote e acompanhar o progresso
7. 🟡 Conferir o relatório de resultado (copiados, pastas sem arquivo-alvo, erros) e usar os `<uuid>.xml` gerados na importação

---
Gerado por reversa-researcher em 2026-09-23T11:41:00-03:00
Fonte: ideation.md
