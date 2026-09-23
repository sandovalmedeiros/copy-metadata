"""Contratos de dados compartilhados entre os módulos (sdd/*#9).

Toda a informação vive em memória: nenhum estado é persistido entre execuções
(data-delta.md §1). Estruturas consumidas por scanner -> motor -> relatorio
e pela interface.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

# Status de uma pasta varrida (sdd/scanner-de-pastas.md#9)
ALVO_ENCONTRADO = "alvo-encontrado"
ALVO_AUSENTE = "alvo-ausente"
NOME_INVALIDO = "nome-invalido"
ERRO_LEITURA = "erro-leitura"

# Status de um item de cópia (sdd/motor-de-copia-renomeacao.md#9).
# Os status de varredura também podem atravessar para o relatório
# (sdd/relatorio-de-execucao.md#9 conta "alvo ausente" no resumo).
COPIADO = "copiado"
SOBRESCRITO = "sobrescrito"
PULADO = "pulado"
COLISAO = "colisao"
ERRO = "erro"
CANCELADO = "cancelado"

STATUS_PROCESSAVEIS = (COPIADO, SOBRESCRITO)
POLITICA_SOBRESCREVER = "sobrescrever"
POLITICA_PULAR = "pular"


@dataclass
class PastaScandeada:
    """Uma subpasta direta da origem (sdd/scanner-de-pastas.md#9)."""

    nome_pasta: str            # UUID capturado — a variável `nome_novo` da demanda
    caminho_absoluto: str
    caminho_relativo_alvo: str
    status: str
    motivo: str = ""


@dataclass
class ResultadoVarredura:
    """Saída do scanner, entrada do motor (sdd/scanner-de-pastas.md#9)."""

    origem: str
    arquivo_alvo_selecionado: str
    caminho_relativo_alvo: str
    pastas: list[PastaScandeada] = field(default_factory=list)


@dataclass
class ItemCopia:
    """Resultado da cópia de uma pasta (sdd/motor-de-copia-renomeacao.md#9)."""

    nome_pasta: str
    origem: str
    destino_final: str
    status: str
    motivo: str = ""


@dataclass
class ResultadoCopia:
    """Saída do motor, entrada do relatório (sdd/motor-de-copia-renomeacao.md#9)."""

    destino: str
    politica_sobrescrita: str
    itens: list[ItemCopia] = field(default_factory=list)
    cancelado: bool = False
    falha_infra: str = ""      # mensagem quando o lote parou por infraestrutura


@dataclass
class ResumoExecucao:
    """Contagens e tempos de uma execução (sdd/relatorio-de-execucao.md#9)."""

    total_itens: int
    por_status: dict[str, int]
    iniciado_em: datetime
    concluido_em: datetime

    @property
    def duracao_segundos(self) -> float:
        return (self.concluido_em - self.iniciado_em).total_seconds()


@dataclass
class RelatorioExecucao:
    """Consolidação exibida/exportada (sdd/relatorio-de-execucao.md#9)."""

    resumo: ResumoExecucao
    problemas: list[ItemCopia] = field(default_factory=list)
    detalhe: list[ItemCopia] = field(default_factory=list)
