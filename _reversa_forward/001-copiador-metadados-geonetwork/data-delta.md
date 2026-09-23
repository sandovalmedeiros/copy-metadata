# Data Delta: Copiador de Metadados GeoNetwork (MVP)

> Identificador: `001-copiador-metadados-geonetwork`
> Data: 2026-09-23
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Modelo persistido

**Nenhum.** O aplicativo não cria banco de dados, arquivo de configuração ou estado persistente entre execuções. Toda a informação vive em memória durante a execução (greenfield, specs SDD seção 9 de cada componente).

Consequências:
- Migrações necessárias: **nenhuma**
- Backups/rollback: remover o executável; arquivos `<uuid>.xml` produzidos pertencem ao usuário
- Nenhum dado pessoal é armazenado ou transmitido

## 2. Estruturas em memória (contratos entre módulos)

Espelham os modelos declarados nas specs SDD:

```
PastaScandeada {          // sdd/scanner-de-pastas.md#9
  nome_pasta: str                 // UUID capturado (nome_novo)
  caminho_absoluto: str
  caminho_relativo_alvo: str
  status: str                     // alvo-encontrado | alvo-ausente | nome-invalido | erro-leitura
  motivo: str
}

ResultadoVarredura {      // sdd/scanner-de-pastas.md#9
  origem: str
  arquivo_alvo_selecionado: str
  caminho_relativo_alvo: str
  pastas: list[PastaScandeada]
}

ItemCopia {               // sdd/motor-de-copia-renomeacao.md#9
  nome_pasta: str
  origem: str
  destino_final: str
  status: str                     // copiado | sobrescrito | pulado | colisao | erro | cancelado
  motivo: str
}

ResultadoCopia {          // sdd/motor-de-copia-renomeacao.md#9
  destino: str
  politica_sobrescrita: str       // sobrescrever | pular
  itens: list[ItemCopia]
}

ResumoExecucao {          // sdd/relatorio-de-execucao.md#9
  total_itens: int
  por_status: dict[str, int]
  iniciado_em: datetime
  concluido_em: datetime
  duracao_segundos: float
}

RelatorioExecucao {       // sdd/relatorio-de-execucao.md#9
  resumo: ResumoExecucao
  problemas: list[ItemCopia]
  detalhe: list[ItemCopia]
}

EstadoTela {              // sdd/interface-desktop.md#9
  origem: str | vazio
  arquivo_alvo: str | vazio
  destino: str | vazio
  executando: bool
  progresso_atual: int
  progresso_total: int
}
```

## 3. Arquivo de saída opcional (exportação do relatório) 🟡

Quando o usuário exportar, o app grava **um arquivo texto** no destino da cópia:

- Nome sugerido: `relatorio-execucao-YYYYMMDD-HHMMSS.txt`
- Conteúdo: bloco de resumo (contagens por status, início, duração) + uma linha por problema (`<uuid> | status | motivo`) + contagem de sucesso
- Alternativa CSV registrada como OQ-02 da spec relatório (formato final a validar com o usuário; texto simples é o padrão seguro por não depender de delimitador regional)

## 4. Dados consumidos (somente leitura) 🟡

- Árvore de pastas da exportação no share de origem (paths de rede mapeados ou UNC)
- Arquivos `.xml` alvo dentro de cada subpasta — lidos byte a byte para cópia; **o conteúdo XML nunca é interpretado, validado ou alterado** (não-objetivo NG-02 do scanner/motor)
