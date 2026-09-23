"""Scanner de pastas (sdd/scanner-de-pastas.md).

Varre o primeiro nível da origem (uma subpasta por registro de metadado),
captura o nome de cada subpasta como `nome_novo` (UUID) e localiza o
arquivo-alvo em cada uma pelo caminho relativo derivado da seleção do
usuário (decisão D-04 do roadmap). Sem UI; testável com paths diretos.
"""
from __future__ import annotations

import os
import re

from app.modelos import (
    ALVO_AUSENTE,
    ALVO_ENCONTRADO,
    ERRO_LEITURA,
    NOME_INVALIDO,
    PastaScandeada,
    ResultadoVarredura,
)

_CARACTERES_PROIBIDOS = re.compile(r'[<>:"/\\|?*]')
_NOMES_RESERVADOS = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)


class ScannerErro(Exception):
    """Falha de infraestrutura na origem (spec scanner EC-01)."""


def nome_arquivo_valido(nome: str) -> bool:
    """Valida um nome de pasta como nome de arquivo Windows (RF-08 do scanner)."""
    if not nome:
        return False
    if nome.upper() in _NOMES_RESERVADOS:
        return False
    if _CARACTERES_PROIBIDOS.search(nome):
        return False
    if nome.endswith(".") or nome.endswith(" "):
        return False
    return True


def derivar_caminho_relativo(origem: str, arquivo_selecionado: str) -> str:
    """Deriva o caminho do arquivo-alvo com relação à subpasta que o contém.

    Seleção `<origem>/<uuid>/metadata/metadata.xml` -> `metadata/metadata.xml`.
    O primeiro componente do caminho relativo (a pasta do arquivo selecionado)
    é descartado porque cada subpasta do lote ocupa essa posição.
    """
    relativo = os.path.relpath(os.path.abspath(arquivo_selecionado), os.path.abspath(origem))
    partes = relativo.split(os.sep)
    if len(partes) <= 1:
        # arquivo direto na raiz da origem: aplica apenas o nome em cada subpasta
        return partes[0]
    return os.path.join(*partes[1:])


def varrer(origem: str, arquivo_selecionado: str) -> ResultadoVarredura:
    """Enumera as subpastas diretas da origem e localiza o alvo em cada uma.

    Levanta ScannerErro quando a origem não existe ou não é acessível —
    sem enumeração parcial (spec scanner EC-01).
    """
    origem = os.path.abspath(origem)
    arquivo_selecionado = os.path.abspath(arquivo_selecionado)
    if not os.path.isdir(origem):
        raise ScannerErro(
            f"Pasta de origem inexistente ou inacessível: {origem}"
            " (confira o caminho e o acesso ao share de rede)."
        )

    resultado = ResultadoVarredura(
        origem=origem,
        arquivo_alvo_selecionado=arquivo_selecionado,
        caminho_relativo_alvo=derivar_caminho_relativo(origem, arquivo_selecionado),
    )

    try:
        entradas = sorted(os.listdir(origem))
    except OSError as exc:
        raise ScannerErro(f"Falha ao ler a origem {origem}: {exc}") from exc

    for nome in entradas:
        caminho = os.path.join(origem, nome)
        if not os.path.isdir(caminho):
            continue  # RF-07: arquivos soltos na raiz são ignorados
        pasta = PastaScandeada(
            nome_pasta=nome,
            caminho_absoluto=caminho,
            caminho_relativo_alvo=resultado.caminho_relativo_alvo,
            status=ALVO_AUSENTE,
        )
        try:
            if not nome_arquivo_valido(nome):
                pasta.status = NOME_INVALIDO
                pasta.motivo = "nome de pasta inválido como nome de arquivo Windows"
            else:
                alvo = os.path.join(caminho, resultado.caminho_relativo_alvo)
                if os.path.isfile(alvo):
                    pasta.status = ALVO_ENCONTRADO
                else:
                    pasta.status = ALVO_AUSENTE
                    pasta.motivo = (
                        f"alvo ausente: {resultado.caminho_relativo_alvo} não encontrado na pasta"
                    )
        except OSError as exc:
            pasta.status = ERRO_LEITURA
            pasta.motivo = f"falha de leitura na pasta: {exc}"
        resultado.pastas.append(pasta)

    return resultado
