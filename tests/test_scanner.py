"""Testes do scanner (T003 — sdd/scanner-de-pastas.md).

Cobertura: enumeração de subpastas diretas, captura de `nome_novo`,
derivação do caminho relativo, alvo ausente, arquivos soltos ignorados,
validação de nome Windows, origem inexistente.
"""
from __future__ import annotations

import os
import tempfile
import unittest

from app.modelos import ALVO_AUSENTE, ALVO_ENCONTRADO
from app.scanner import (
    ScannerErro,
    derivar_caminho_relativo,
    nome_arquivo_valido,
    varrer,
)

UUIDS = [
    "0b8733a3-93ba-4d18-aa6a-a63782546898",
    "11111111-2222-3333-4444-555555555555",
    "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
]
SEM_ALVO = "ffffffff-0000-0000-0000-000000000000"


class FixtureLote:
    """Exportação falsa: 3 pastas com alvo + 1 sem alvo + 1 arquivo solto."""

    def __init__(self, base: str) -> None:
        self.origem = os.path.join(base, "IDEBAHIA-TESTE")
        os.makedirs(self.origem)
        for uuid in UUIDS:
            pasta = os.path.join(self.origem, uuid, "metadata")
            os.makedirs(pasta)
            with open(os.path.join(pasta, "metadata.xml"), "w", encoding="utf-8") as fh:
                fh.write(f"<metadata>teste {uuid}</metadata>")
        os.makedirs(os.path.join(self.origem, SEM_ALVO))  # pasta sem o alvo
        with open(os.path.join(self.origem, "solto.xml"), "w", encoding="utf-8") as fh:
            fh.write("arquivo solto na raiz deve ser ignorado")

    @property
    def arquivo_representante(self) -> str:
        return os.path.join(self.origem, UUIDS[0], "metadata", "metadata.xml")


class TestVarredura(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.lote = FixtureLote(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_enumeracao_captura_nome_de_cada_subpasta(self) -> None:
        resultado = varrer(self.lote.origem, self.lote.arquivo_representante)
        nomes = [p.nome_pasta for p in resultado.pastas]
        self.assertEqual(sorted(nomes), sorted(UUIDS + [SEM_ALVO]))

    def test_arquivos_soltos_sao_ignorados(self) -> None:
        resultado = varrer(self.lote.origem, self.lote.arquivo_representante)
        self.assertNotIn("solto.xml", [p.nome_pasta for p in resultado.pastas])

    def test_deriva_caminho_relativo_do_arquivo_selecionado(self) -> None:
        relativo = derivar_caminho_relativo(self.lote.origem, self.lote.arquivo_representante)
        self.assertEqual(relativo, os.path.join("metadata", "metadata.xml"))

    def test_alvo_encontrado_nas_pastas_com_arquivo(self) -> None:
        resultado = varrer(self.lote.origem, self.lote.arquivo_representante)
        por_nome = {p.nome_pasta: p for p in resultado.pastas}
        for uuid in UUIDS:
            self.assertEqual(por_nome[uuid].status, ALVO_ENCONTRADO)
            self.assertEqual(por_nome[uuid].motivo, "")

    def test_pasta_sem_alvo_registrada_com_motivo(self) -> None:
        resultado = varrer(self.lote.origem, self.lote.arquivo_representante)
        pasta = next(p for p in resultado.pastas if p.nome_pasta == SEM_ALVO)
        self.assertEqual(pasta.status, ALVO_AUSENTE)
        self.assertNotEqual(pasta.motivo, "")

    def test_origem_inexistente_levanta_erro_claro(self) -> None:
        with tempfile.TemporaryDirectory() as vazio:
            inexistente = os.path.join(vazio, "nao-existe")
            with self.assertRaises(ScannerErro):
                varrer(inexistente, self.lote.arquivo_representante)


class TestNomeArquivoValido(unittest.TestCase):
    def test_uuid_e_valido(self) -> None:
        self.assertTrue(nome_arquivo_valido(UUIDS[0]))

    def test_caracteres_proibidos_sao_invalidos(self) -> None:
        for nome in ("com<menor", "com:dois", "com|pipe", "com?interro"):
            self.assertFalse(nome_arquivo_valido(nome), nome)

    def test_nomes_reservados_sao_invalidos(self) -> None:
        for nome in ("CON", "PRN", "AUX", "NUL", "COM1", "LPT9"):
            self.assertFalse(nome_arquivo_valido(nome), nome)

    def test_nome_terminado_em_ponto_ou_espaco_e_invalido(self) -> None:
        self.assertFalse(nome_arquivo_valido("uuid."))
        self.assertFalse(nome_arquivo_valido("uuid "))


if __name__ == "__main__":
    unittest.main()
