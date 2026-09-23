"""Motor de cópia e renomeação em lote (sdd/motor-de-copia-renomeacao.md).

Copia o arquivo-alvo de cada pasta válida para o destino salvando como
`<nome_pasta>.xml` (RF-01 do motor), aplicando política de sobrescrita
(D-05 do roadmap), detectando colisões, continuando após falhas
individuais (RN-03) e honrando cancelamento (RN-06).
"""
from __future__ import annotations

import os
import shutil
import threading
from typing import Callable

from app.modelos import (
    ALVO_ENCONTRADO,
    CANCELADO,
    COLISAO,
    COPIADO,
    ERRO,
    POLITICA_SOBRESCREVER,
    PULADO,
    SOBRESCRITO,
    ItemCopia,
    ResultadoCopia,
    ResultadoVarredura,
)

Progresso = Callable[[ItemCopia, int, int], None]


class MotorErro(Exception):
    """Falha de infraestrutura que interrompe o lote (spec motor EC-01)."""


def _verificar_tamanho(origem: str, destino: str) -> None:
    """Verificação mínima de integridade por tamanho (RN-05, decisão D-08)."""
    if os.path.getsize(origem) != os.path.getsize(destino):
        raise OSError(f"tamanho divergente após a cópia: {origem} -> {destino}")


def copiar_lote(
    varredura: ResultadoVarredura,
    destino: str,
    politica: str = POLITICA_SOBRESCREVER,
    cancelar: threading.Event | None = None,
    ao_concluir_item: Progresso | None = None,
) -> ResultadoCopia:
    """Executa a cópia em lote e devolve um ItemCopia por pasta varrida.

    Pastas não processáveis da varredura atravessam com o status de origem
    (alvo-ausente / nome-invalido / erro-leitura) para o relatório consolidar.
    """
    destino = os.path.abspath(destino)
    try:
        os.makedirs(destino, exist_ok=True)
    except OSError as exc:
        raise MotorErro(
            f"Não foi possível criar/acessar a pasta de destino {destino}: {exc}"
        ) from exc

    resultado = ResultadoCopia(destino=destino, politica_sobrescrita=politica)
    cancelado = cancelar is not None and cancelar.is_set()
    vistos: set[str] = set()
    total = len(varredura.pastas)

    for indice, pasta in enumerate(varredura.pastas, start=1):
        item = ItemCopia(
            nome_pasta=pasta.nome_pasta,
            origem=os.path.join(pasta.caminho_absoluto, pasta.caminho_relativo_alvo),
            destino_final=os.path.join(destino, f"{pasta.nome_pasta}.xml"),
            status=CANCELADO,
        )

        if cancelado:
            item.motivo = "cancelado antes do processamento"
        elif pasta.status != ALVO_ENCONTRADO:
            item.status = pasta.status  # atravessa alvo-ausente/nome-invalido/erro-leitura
            item.motivo = pasta.motivo
        elif pasta.nome_pasta in vistos:
            item.status = COLISAO  # RF-04: duplicata no lote, sem sobrescrita silenciosa
            item.motivo = "UUID duplicado no lote; apenas a primeira ocorrência foi copiada"
        else:
            vistos.add(pasta.nome_pasta)
            item.status, item.motivo = _copiar_item(item, politica)

        resultado.itens.append(item)
        if ao_concluir_item is not None:
            ao_concluir_item(item, indice, total)
        if cancelar is not None and cancelar.is_set():
            cancelado = True

    resultado.cancelado = cancelado
    return resultado


def _copiar_item(item: ItemCopia, politica: str) -> tuple[str, str]:
    """Copia um item individual; falha individual não aborta o lote (RN-03)."""
    existia = os.path.isfile(item.destino_final)
    if existia and politica != POLITICA_SOBRESCREVER:
        return PULADO, "arquivo já existia no destino (política: pular)"
    try:
        shutil.copyfile(item.origem, item.destino_final)
        _verificar_tamanho(item.origem, item.destino_final)
    except OSError as exc:
        return ERRO, f"falha ao copiar: {exc}"
    return (SOBRESCRITO if existia else COPIADO), ""
