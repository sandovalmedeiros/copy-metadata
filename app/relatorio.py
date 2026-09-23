"""Relatório de execução (sdd/relatorio-de-execucao.md).

Consolida o ResultadoCopia em contagens por status, lista de problemas
com motivo (na frente, decisão do spec) e texto exportável para o destino.
"""
from __future__ import annotations

import os
from datetime import datetime

from app.modelos import (
    STATUS_PROCESSAVEIS,
    RelatorioExecucao,
    ResumoExecucao,
    ResultadoCopia,
)

_ROTULOS = {
    "copiado": "copiados",
    "sobrescrito": "sobrescritos",
    "pulado": "pulados",
    "colisao": "colisões",
    "erro": "erros",
    "cancelado": "cancelados",
    "alvo-ausente": "alvo ausente",
    "nome-invalido": "nome inválido",
    "erro-leitura": "erro de leitura",
}


def consolidar(
    resultado: ResultadoCopia,
    iniciado_em: datetime,
    concluido_em: datetime,
) -> RelatorioExecucao:
    """Monta o relatório: resumo por status + problemas primeiro (RF-01/RF-02/RF-05)."""
    por_status: dict[str, int] = {}
    for item in resultado.itens:
        por_status[item.status] = por_status.get(item.status, 0) + 1
    resumo = ResumoExecucao(
        total_itens=len(resultado.itens),
        por_status=por_status,
        iniciado_em=iniciado_em,
        concluido_em=concluido_em,
    )
    problemas = [i for i in resultado.itens if i.status not in STATUS_PROCESSAVEIS]
    return RelatorioExecucao(
        resumo=resumo,
        problemas=problemas,
        detalhe=list(resultado.itens),
    )


def formatar_texto(relatorio: RelatorioExecucao) -> str:
    """Renderiza o relatório como texto simples (tela e exportação usam o mesmo corpo)."""
    resumo = relatorio.resumo
    linhas = [
        "RELATÓRIO DE EXECUÇÃO — Copiador de Metadados GeoNetwork",
        "",
        f"Iniciado em: {resumo.iniciado_em.strftime('%d/%m/%Y %H:%M:%S')}",
        f"Duração: {resumo.duracao_segundos:.1f} s",
        f"Total de pastas: {resumo.total_itens}",
        "",
    ]
    for status in sorted(resumo.por_status):
        rotulo = _ROTULOS.get(status, status)
        linhas.append(f"  {rotulo}: {resumo.por_status[status]}")

    linhas.append("")
    if relatorio.problemas:
        linhas.append(f"PROBLEMAS ({len(relatorio.problemas)}) — revise as pastas abaixo:")
        for problema in relatorio.problemas:
            motivo = problema.motivo or "sem motivo registrado"
            linhas.append(f"  {problema.nome_pasta} | {problema.status} | {motivo}")
    else:
        linhas.append("PROBLEMAS (0) — lote íntegro, nada a revisar.")
    return "\n".join(linhas) + "\n"


def exportar(relatorio: RelatorioExecucao, destino: str) -> str:
    """Grava o relatório em texto no destino e retorna o caminho criado (RF-07, Could).

    Nome do arquivo conforme data-delta.md §3:
    `relatorio-execucao-YYYYMMDD-HHMMSS.txt`.
    """
    destino = os.path.abspath(destino)
    marca = relatorio.resumo.concluido_em.strftime("%Y%m%d-%H%M%S")
    caminho = os.path.join(destino, f"relatorio-execucao-{marca}.txt")
    with open(caminho, "w", encoding="utf-8-sig", newline="\n") as fh:  # BOM: abre certo no Bloco de Notas
        fh.write(formatar_texto(relatorio))
    return caminho
