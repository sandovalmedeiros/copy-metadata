"""Testes do motor de cópia (T004 — sdd/motor-de-copia-renomeacao.md).

Cobertura: lote feliz, destino criado, política de sobrescrita
(sobrescrever/pular), colisão de UUID, falha individual não aborta,
cancelamento preserva cópias feitas, destino inválido.
"""
from __future__ import annotations

import os
import tempfile
import threading
import unittest

from app.modelos import (
    ALVO_AUSENTE,
    ALVO_ENCONTRADO,
    CANCELADO,
    COLISAO,
    COPIADO,
    ERRO,
    ItemCopia,
    PastaScandeada,
    POLITICA_PULAR,
    POLITICA_SOBRESCREVER,
    PULADO,
    ResultadoVarredura,
    SOBRESCRITO,
)
from app.motor import MotorErro, copiar_lote
from app.scanner import varrer

UUIDS = [
    "0b8733a3-93ba-4d18-aa6a-a63782546898",
    "11111111-2222-3333-4444-555555555555",
    "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
]
SEM_ALVO = "ffffffff-0000-0000-0000-000000000000"


class FixtureLote:
    def __init__(self, base: str) -> None:
        self.origem = os.path.join(base, "IDEBAHIA-TESTE")
        os.makedirs(self.origem)
        for uuid in UUIDS:
            pasta = os.path.join(self.origem, uuid, "metadata")
            os.makedirs(pasta)
            with open(os.path.join(pasta, "metadata.xml"), "w", encoding="utf-8") as fh:
                fh.write(f"<metadata>teste {uuid}</metadata>")
        os.makedirs(os.path.join(self.origem, SEM_ALVO))

    @property
    def representante(self) -> str:
        return os.path.join(self.origem, UUIDS[0], "metadata", "metadata.xml")


class TestMotor(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.lote = FixtureLote(self._tmp.name)
        self.destino = os.path.join(self._tmp.name, "saida")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def varrer(self) -> ResultadoVarredura:
        return varrer(self.lote.origem, self.lote.representante)

    def test_lote_feliz_copia_renomeia_por_uuid(self) -> None:
        resultado = copiar_lote(self.varrer(), self.destino)
        self.assertFalse(resultado.cancelado)
        self.assertEqual(resultado.falha_infra, "")
        for uuid in UUIDS:
            arquivo = os.path.join(self.destino, f"{uuid}.xml")
            self.assertTrue(os.path.isfile(arquivo), arquivo)
            with open(arquivo, encoding="utf-8") as fh:
                self.assertEqual(fh.read(), f"<metadata>teste {uuid}</metadata>")
        statuses = [i.status for i in resultado.itens]
        self.assertEqual(statuses.count(COPIADO), len(UUIDS))

    def test_destino_inexistente_e_criado(self) -> None:
        self.assertFalse(os.path.exists(self.destino))
        copiar_lote(self.varrer(), self.destino)
        self.assertTrue(os.path.isdir(self.destino))

    def test_pasta_sem_alvo_nao_impede_as_demais(self) -> None:
        resultado = copiar_lote(self.varrer(), self.destino)
        por_pasta = {i.nome_pasta: i for i in resultado.itens}
        self.assertEqual(por_pasta[SEM_ALVO].status, ALVO_AUSENTE)
        self.assertNotEqual(por_pasta[SEM_ALVO].motivo, "")
        for uuid in UUIDS:
            self.assertEqual(por_pasta[uuid].status, COPIADO)

    def test_politica_pular_preserva_existente(self) -> None:
        copiar_lote(self.varrer(), self.destino)
        existente = os.path.join(self.destino, f"{UUIDS[0]}.xml")
        with open(existente, "w", encoding="utf-8") as fh:
            fh.write("conteudo antigo que deve permanecer")
        resultado = copiar_lote(self.varrer(), self.destino, politica=POLITICA_PULAR)
        por_pasta = {i.nome_pasta: i for i in resultado.itens}
        self.assertEqual(por_pasta[UUIDS[0]].status, PULADO)
        with open(existente, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "conteudo antigo que deve permanecer")

    def test_politica_sobrescrever_substitui_existente(self) -> None:
        copiar_lote(self.varrer(), self.destino)
        resultado = copiar_lote(self.varrer(), self.destino, politica=POLITICA_SOBRESCREVER)
        por_pasta = {i.nome_pasta: i for i in resultado.itens}
        self.assertEqual(por_pasta[UUIDS[0]].status, SOBRESCRITO)
        with open(os.path.join(self.destino, f"{UUIDS[0]}.xml"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), f"<metadata>teste {UUIDS[0]}</metadata>")

    def test_uuid_duplicado_vira_colisao_sem_sobrescrita(self) -> None:
        varredura = self.varrer()
        duplicada = next(p for p in varredura.pastas if p.nome_pasta == UUIDS[0])
        varredura.pastas.append(
            PastaScandeada(
                nome_pasta=UUIDS[0],
                caminho_absoluto=duplicada.caminho_absoluto,
                caminho_relativo_alvo=duplicada.caminho_relativo_alvo,
                status=ALVO_ENCONTRADO,
            )
        )
        resultado = copiar_lote(varredura, self.destino)
        statuses = [i.status for i in resultado.itens if i.nome_pasta == UUIDS[0]]
        self.assertIn(COPIADO, statuses)
        self.assertEqual(statuses.count(COLISAO), 1)
        colisao = next(i for i in resultado.itens if i.status == COLISAO)
        self.assertNotEqual(colisao.motivo, "")

    def test_falha_individual_registra_erro_e_continua(self) -> None:
        varredura = self.varrer()
        # EC-06: alvo removido entre a varredura e a cópia
        os.remove(os.path.join(self.lote.origem, UUIDS[1], "metadata", "metadata.xml"))
        resultado = copiar_lote(varredura, self.destino)
        por_pasta = {i.nome_pasta: i for i in resultado.itens}
        self.assertEqual(por_pasta[UUIDS[1]].status, ERRO)
        self.assertNotEqual(por_pasta[UUIDS[1]].motivo, "")
        self.assertEqual(por_pasta[UUIDS[0]].status, COPIADO)
        self.assertEqual(por_pasta[UUIDS[2]].status, COPIADO)

    def test_cancelamento_preserva_copias_feitas(self) -> None:
        varredura = self.varrer()
        cancelar = threading.Event()

        def ao_concluir(_item: ItemCopia, indice: int, _total: int) -> None:
            if indice == 1:  # após a primeira cópia concluída
                cancelar.set()

        resultado = copiar_lote(varredura, self.destino, cancelar=cancelar, ao_concluir_item=ao_concluir)
        self.assertTrue(resultado.cancelado)
        statuses = [i.status for i in resultado.itens]
        self.assertEqual(statuses.count(COPIADO), 1)
        self.assertGreater(statuses.count(CANCELADO), 0)
        # a cópia concluída permanece no destino
        self.assertTrue(os.path.isfile(os.path.join(self.destino, f"{UUIDS[0]}.xml")))

    def test_destino_invalido_levanta_erro_de_infra(self) -> None:
        destino_ruim = os.path.join(self.destino, "sub<invalido>")
        with self.assertRaises(MotorErro):
            copiar_lote(self.varrer(), destino_ruim)

    def test_item_preexistente_sem_conflito_usa_politica_padrao_sobrescrever(self) -> None:
        copiar_lote(self.varrer(), self.destino)
        resultado = copiar_lote(self.varrer(), self.destino)  # default = sobrescrever
        statuses = [i.status for i in resultado.itens]
        self.assertEqual(statuses.count(SOBRESCRITO), len(UUIDS))


if __name__ == "__main__":
    unittest.main()
