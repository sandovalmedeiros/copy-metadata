"""Testes do relatório de execução (T005 — sdd/relatorio-de-execucao.md).

Cobertura: soma de contagens fecha com o total, problemas com motivo
na frente, parcial de cancelamento, exportação para arquivo texto.
"""
from __future__ import annotations

import os
import tempfile
import unittest
from datetime import datetime, timedelta

from app.modelos import (
    ALVO_AUSENTE,
    CANCELADO,
    COPIADO,
    ERRO,
    ItemCopia,
    ResumoExecucao,
    ResultadoCopia,
)
from app.relatorio import consolidar, exportar, formatar_texto


def item(nome: str, status: str, motivo: str = "") -> ItemCopia:
    return ItemCopia(
        nome_pasta=nome,
        origem=f"C:/origem/{nome}/metadata/metadata.xml",
        destino_final=f"C:/destino/{nome}.xml",
        status=status,
        motivo=motivo,
    )


ITENS = [
    item("uuid-1", COPIADO),
    item("uuid-2", COPIADO),
    item("uuid-3", CANCELADO, "cancelado antes do processamento"),
    item("uuid-4", ERRO, "falha de leitura no share"),
    item("uuid-5", ALVO_AUSENTE, "alvo ausente em metadata/metadata.xml"),
]


def resultado_cancelado() -> ResultadoCopia:
    return ResultadoCopia(
        destino="C:/metadados_geonetwork",
        politica_sobrescrita="sobrescrever",
        itens=list(ITENS),
        cancelado=True,
    )


class TestConsolidacao(unittest.TestCase):
    def setUp(self) -> None:
        inicio = datetime(2026, 9, 23, 12, 0, 0)
        self.relatorio = consolidar(
            resultado_cancelado(),
            iniciado_em=inicio,
            concluido_em=inicio + timedelta(seconds=12.5),
        )

    def test_soma_das_contagens_fecha_com_total(self) -> None:
        resumo: ResumoExecucao = self.relatorio.resumo
        self.assertEqual(sum(resumo.por_status.values()), resumo.total_itens)
        self.assertEqual(resumo.total_itens, len(ITENS))

    def test_duracao_calculada(self) -> None:
        self.assertAlmostEqual(self.relatorio.resumo.duracao_segundos, 12.5)

    def test_problemas_primeiro_e_com_motivo(self) -> None:
        problemas = self.relatorio.problemas
        self.assertEqual(len(problemas), 3)
        for p in problemas:
            self.assertNotEqual(p.motivo, "")
        self.assertEqual({p.status for p in problemas}, {CANCELADO, ERRO, ALVO_AUSENTE})

    def test_detalhe_mantem_ordem_de_processamento(self) -> None:
        self.assertEqual([i.nome_pasta for i in self.relatorio.detalhe], [i.nome_pasta for i in ITENS])


class TestFormatacaoExportacao(unittest.TestCase):
    def setUp(self) -> None:
        inicio = datetime(2026, 9, 23, 12, 0, 0)
        self.relatorio = consolidar(
            resultado_cancelado(),
            iniciado_em=inicio,
            concluido_em=inicio + timedelta(seconds=12.5),
        )

    def test_texto_contem_contagens_e_problemas(self) -> None:
        texto = formatar_texto(self.relatorio)
        self.assertIn("RELATÓRIO DE EXECUÇÃO", texto)
        self.assertIn("uuid-4", texto)      # problema listado
        self.assertIn("falha de leitura", texto)  # motivo visível
        self.assertIn("copiados", texto.lower())

    def test_exportar_grava_arquivo_texto_no_destino(self) -> None:
        with tempfile.TemporaryDirectory() as destino:
            caminho = exportar(self.relatorio, destino)
            self.assertTrue(os.path.isfile(caminho))
            self.assertTrue(caminho.startswith(destino))
            nome = os.path.basename(caminho)
            self.assertTrue(nome.startswith("relatorio-execucao-"))
            self.assertTrue(nome.endswith(".txt"))
            with open(caminho, encoding="utf-8-sig") as fh:
                conteudo = fh.read()
            self.assertIn("uuid-4", conteudo)


if __name__ == "__main__":
    unittest.main()
