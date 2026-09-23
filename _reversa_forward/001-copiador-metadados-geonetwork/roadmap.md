# Roadmap: Copiador de Metadados GeoNetwork (MVP)

> Identificador: `001-copiador-metadados-geonetwork`
> Data: 2026-09-23
> Requirements: `_reversa_forward/001-copiador-metadados-geonetwork/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Aplicativo desktop monolítico em Python com interface Tkinter, organizado em quatro módulos internos puros (`scanner`, `motor`, `relatorio`) consumidos por uma GUI fina (`interface`) — decomposição espelhada nas specs SDD. O lote roda em thread separada da thread de eventos, publicando progresso por pasta; toda falha individual é registrada sem abortar o lote. Runtime 100% stdlib; distribuição por executável empacotado (one-dir). Projeto greenfield: todos os componentes são novos, não há delta sobre legado.

## 2. Princípios aplicados

> `.reversa/principles.md` não existe neste projeto — nenhum princípio ativo a aplicar (config `principles.enabled` aguarda criação via `/reversa-principles`).

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| n/a (arquivo ausente) | Sem princípios cadastrados | n/a |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Python 3 + Tkinter como plataforma | Decisão explícita do usuário na entrevista; Tkinter acompanha o Python (zero dependência externa) | PySide6, wxWidgets, aplicativo web local | 🟢 |
| D-02 | Quatro módulos puros testáveis + GUI fina | Espelha a decomposição das specs SDD; scanner/motor/relatório rodam sem UI e são testáveis por paths diretos | Monólito único dentro da GUI | 🟡 |
| D-03 | Lote em thread separada da thread de eventos Tk | Janela responsiva e cancelamento < 2 s (spec interface RNF-02) | Execução síncrona na thread de eventos | 🟡 |
| D-04 | Derivar caminho relativo completo do arquivo-alvo a partir da seleção do usuário | Comportamento previsível e diagnosticável (Decision Log scanner) | Buscar o arquivo por nome em qualquer subnível | 🟡 |
| D-05 | Política de sobrescrita padrão: perguntar uma vez por execução | Evita perda silenciosa e evita perguntar por pasta (PRD §4 + spec motor RF-03) | Sobrescrever sempre; pular sempre | 🟡 |
| D-06 | Continuidade após falha por pasta, com registro de motivo | Maximiza o trabalho aproveitado no lote (spec motor RF-05) | Transação tudo-ou-nada | 🟡 |
| D-07 | Empacotamento PyInstaller modo one-dir | Inicialização mais curta e melhor aceitação por antivírus corporativo (spec interface, OQ-03) | one-file; Nuitka | 🟡 |
| D-08 | Verificação de integridade por tamanho de arquivo (mínimo), hash opcional | Custo baixo atende à RN-05 com verificação mínima (spec motor OQ-02) | Hash SHA-256 obrigatório por cópia | 🟡 |
| D-09 | Exportação de relatório como texto/CSV opcional (Could) | Evita gravar arquivo no destino quando o usuário só confere (Decision Log relatório) | Exportar sempre automaticamente | 🟡 |

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| O arquivo-alvo é localizado pelo caminho relativo derivado da seleção (ex.: `metadata\metadata.xml`), igual em todas as pastas | §10 Premissa 1 | Se a estrutura variar entre pastas, cópias ficam faltando (relatório aponta como alvo ausente; retrabalho) |
| Sobrescrita padrão = perguntar uma vez por execução | §10 Premissa 2 | Se o usuário esperava sobrescrever/pular sem perguntar, atrito menor; ajuste de UI |
| Interface em pt-br | §10 Premissa 3 | Se outro idioma for necessário, retrabalho de strings (baixo) |
| Targets de desempenho (varredura < 60 s / cópia < 5 min para 500 pastas) | §10 Premissa 4 | Redefinição de meta de performance; sem impacto funcional |

## 5. Delta arquitetural

> Greenfield: nenhum componente pré-existente muda; os quatro abaixo são criados do zero.

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|----------------|--------|
| scanner-de-pastas | `_reversa_sdd/sdd/scanner-de-pastas.md` | componente-novo | Varre subpastas da origem, captura `nome_novo`, localiza alvo por caminho relativo |
| motor-de-copia-renomeacao | `_reversa_sdd/sdd/motor-de-copia-renomeacao.md` | componente-novo | Cópia em lote `<uuid>.xml` com política de sobrescrita, colisão e cancelamento |
| relatorio-de-execucao | `_reversa_sdd/sdd/relatorio-de-execucao.md` | componente-novo | Consolidação por status, problemas com motivo, exportação opcional |
| interface-desktop | `_reversa_sdd/sdd/interface-desktop.md` | componente-novo | Janela Tkinter orquestrando o fluxo; thread de lote; empacotamento |

## 6. Delta no modelo de dados

- Resumo das mudanças: nenhum modelo persistido — estruturas em memória (`PastaScandeada`, `ResultadoVarredura`, `ItemCopia`, `ResultadoCopia`, `ResumoExecucao`, `RelatorioExecucao`) e um arquivo de saída opcional (relatório exportado). Sem banco, sem migrações.
- Detalhe completo em: `_reversa_forward/001-copiador-metadados-geonetwork/data-delta.md`

## 7. Delta de contratos externos

Nenhum contrato externo (HTTP / fila / gRPC / GraphQL). A interação com o mundo é apenas sistema de arquivos: leitura no share de origem, escrita na pasta de destino. Diretório `interfaces/` omitido por não haver contrato a documentar.

## 8. Plano de migração

n/a — projeto greenfield, sem dados nem serviços legados a migrar.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Estrutura interna variar entre pastas do lote | alto | média | Caminho relativo derivado + relatório de alvos ausentes para diagnóstico |
| Colisão de nome (UUID duplicado ou arquivo pré-existente) | médio | baixa | Detecção antes de copiar + política de sobrescrita explícita |
| Share lento/indisponível durante o lote | médio | média | Erro por pasta com motivo, continuidade, relatório parcial, cancelamento |
| Nome de pasta inválido/reservado no Windows | médio | baixa | Validação de nome com status específico no relatório |
| `.exe` bloqueado por antivírus corporativo | baixo | média | one-dir + instrução de liberação; alternativa via Python instalado |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-09-23 | Versão inicial gerada por `/reversa-plan` (pipeline /reversa-new expresso) | reversa-plan |
