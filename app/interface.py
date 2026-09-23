"""Interface desktop (sdd/interface-desktop.md).

Janela única Tkinter que orquestra o fluxo: seleção de origem, arquivo-alvo
e destino por diálogos nativos; execução do lote em thread separada da
thread de eventos (decisão D-03); progresso e cancelamento; exibição e
exportação do relatório. Estados da UI conforme spec §8.
"""
from __future__ import annotations

import os
import queue
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext, ttk

from app import motor, relatorio, scanner
from app.modelos import POLITICA_PULAR, POLITICA_SOBRESCREVER

TITULO = "Copiador de Metadados GeoNetwork"

ORIENTACAO = (
    "1. Selecione a pasta de origem (lote exportado, ex.: S:\\...\\IDEBAHIA-CADASTRO-...)\n"
    "2. Selecione o arquivo .xml alvo navegando até ele (ex.: <uuid>\\metadata\\metadata.xml)\n"
    "3. Selecione a pasta de destino (ex.: C:\\metadados_geonetwork)\n"
    "4. Clique em Executar — cada pasta vira um arquivo <uuid>.xml no destino.\n"
    "\n"
    "Execute um lote para ver o relatório aqui."
)


class JanelaPrincipal(tk.Tk):
    """Janela principal do aplicativo (todos os RFs da spec interface)."""

    def __init__(self) -> None:
        super().__init__()
        self.title(TITULO)
        self.resizable(True, True)

        self._origem = tk.StringVar()
        self._alvo = tk.StringVar()
        self._destino = tk.StringVar()

        self._fila: queue.Queue = queue.Queue()
        self._evento_cancelar: threading.Event | None = None
        self._executando = False
        self._falhou = False
        self._ultimo_relatorio: relatorio.RelatorioExecucao | None = None

        self._construir_layout()
        self.protocol("WM_DELETE_WINDOW", self._confirmar_fechar)
        self.after(100, self._drenar_fila)

    # ── layout ────────────────────────────────────────────────────────────

    def _construir_layout(self) -> None:
        quadro = ttk.Frame(self, padding=12)
        quadro.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._linha_campo(quadro, 0, "Pasta de origem:", self._origem, self._selecionar_origem)
        self._linha_campo(quadro, 1, "Arquivo-alvo (.xml):", self._alvo, self._selecionar_alvo)
        self._linha_campo(quadro, 2, "Pasta de destino:", self._destino, self._selecionar_destino)

        acoes = ttk.Frame(quadro)
        acoes.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(10, 4))
        self._btn_executar = ttk.Button(acoes, text="Executar", state="disabled", command=self._executar)
        self._btn_executar.grid(row=0, column=0, padx=(0, 6))
        self._btn_cancelar = ttk.Button(acoes, text="Cancelar", state="disabled", command=self._cancelar)
        self._btn_cancelar.grid(row=0, column=1, padx=(0, 6))
        self._btn_exportar = ttk.Button(acoes, text="Exportar relatório", state="disabled", command=self._exportar)
        self._btn_exportar.grid(row=0, column=2)

        self._barra = ttk.Progressbar(quadro, mode="determinate", maximum=1)
        self._barra.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(8, 2))
        self._rotulo_progresso = ttk.Label(quadro, text="Pronto.")
        self._rotulo_progresso.grid(row=5, column=0, columnspan=3, sticky="w")

        self._area_relatorio = scrolledtext.ScrolledText(quadro, height=14, state="disabled")
        self._area_relatorio.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
        quadro.rowconfigure(6, weight=1)
        quadro.columnconfigure(1, weight=1)

        self._escrever_relatorio(ORIENTACAO)

    def _linha_campo(self, pai: ttk.Frame, linha: int, rotulo: str, variavel: tk.StringVar, comando) -> None:
        ttk.Label(pai, text=rotulo).grid(row=linha, column=0, sticky="w", pady=2)
        ttk.Entry(pai, textvariable=variavel, state="readonly").grid(
            row=linha, column=1, sticky="ew", padx=6
        )
        ttk.Button(pai, text="Procurar…", command=comando).grid(row=linha, column=2)

    # ── seleção e validação ───────────────────────────────────────────────

    def _selecionar_origem(self) -> None:
        escolha = filedialog.askdirectory(title="Selecione a pasta de origem do lote", parent=self)
        if escolha:
            self._origem.set(os.path.normpath(escolha))
            self._validar_campos()

    def _selecionar_alvo(self) -> None:
        escolha = filedialog.askopenfilename(
            title="Selecione o arquivo .xml alvo (ex.: metadata.xml)",
            filetypes=[("Arquivos XML", "*.xml"), ("Todos os arquivos", "*.*")],
            parent=self,
        )
        if escolha:
            self._alvo.set(os.path.normpath(escolha))
            self._validar_campos()

    def _selecionar_destino(self) -> None:
        escolha = filedialog.askdirectory(title="Selecione a pasta de destino", parent=self)
        if escolha:
            self._destino.set(os.path.normpath(escolha))
            self._validar_campos()

    def _campos_pendentes(self) -> list[str]:
        faltando = []
        if not self._origem.get():
            faltando.append("origem")
        if not self._alvo.get():
            faltando.append("arquivo-alvo")
        if not self._destino.get():
            faltando.append("destino")
        return faltando

    def _validar_campos(self) -> None:
        """RF-09/EC-01: Executar habilita só com os três campos; dica do que falta."""
        faltando = self._campos_pendentes()
        if self._executando:
            estado = "disabled"
            self._rotulo_progresso.config(text="Executando… use Cancelar para interromper.")
        elif faltando:
            estado = "disabled"
            self._rotulo_progresso.config(text=f"Preencha ainda: {', '.join(faltando)}.")
        else:
            estado = "normal"
            self._rotulo_progresso.config(text="Pronto para executar.")
        self._btn_executar.config(state=estado)

    # ── execução ──────────────────────────────────────────────────────────

    def _executar(self) -> None:
        origem = self._origem.get()
        alvo = self._alvo.get()
        destino = self._destino.get()

        # RF-09 / EC-02: validação com mensagem específica, nada copiado
        if not os.path.isdir(origem):
            messagebox.showerror(
                "Origem inválida",
                f"A pasta de origem não existe ou está inacessível:\n{origem}\n\n"
                "Confira o caminho e o acesso ao share de rede.",
                parent=self,
            )
            return
        if not os.path.isfile(alvo):
            messagebox.showerror("Arquivo-alvo inválido", f"O arquivo-alvo não existe:\n{alvo}", parent=self)
            return
        try:
            dentro = os.path.commonpath([os.path.abspath(origem), os.path.abspath(alvo)]) == os.path.abspath(origem)
        except ValueError:
            dentro = False
        if not dentro:
            messagebox.showerror(
                "Arquivo-alvo fora da origem",
                "O arquivo-alvo selecionado deve estar DENTRO da pasta de origem\n"
                "(ele define o caminho relativo aplicado a cada pasta do lote).",
                parent=self,
            )
            return
        if os.path.exists(destino) and not os.path.isdir(destino):
            messagebox.showerror("Destino inválido", f"O destino não é uma pasta:\n{destino}", parent=self)
            return

        # RN-04 / decisão D-05: perguntar UMA vez por execução quando há conflito
        # potencial; sem arquivos .xml no destino não há o que sobrescrever.
        politica = POLITICA_SOBRESCREVER
        if os.path.isdir(destino) and any(nome.endswith(".xml") for nome in os.listdir(destino)):
            resposta = messagebox.askyesnocancel(
                "Política de sobrescrita",
                "Já existem arquivos .xml na pasta de destino.\n\n"
                "Sobrescrever os arquivos existentes?\n\n"
                "Sim = sobrescrever | Não = pular existentes | Cancelar = não executar",
                parent=self,
            )
            if resposta is None:
                return
            politica = POLITICA_SOBRESCREVER if resposta else POLITICA_PULAR

        self._iniciar_execucao(origem, alvo, destino, politica)

    def _iniciar_execucao(self, origem: str, alvo: str, destino: str, politica: str) -> None:
        self._executando = True
        self._falhou = False
        self._evento_cancelar = threading.Event()
        self._btn_executar.config(state="disabled")
        self._btn_cancelar.config(state="normal")
        self._btn_exportar.config(state="disabled")
        self._barra.config(maximum=1, value=0)
        self._rotulo_progresso.config(text="Executando… 0 de ?")
        self._escrever_relatorio("Executando o lote… o relatório aparece aqui ao terminar.\n")

        trabalhadora = threading.Thread(
            target=self._trabalhar, args=(origem, alvo, destino, politica), daemon=True
        )
        trabalhadora.start()

    def _trabalhar(self, origem: str, alvo: str, destino: str, politica: str) -> None:
        """Roda na thread de lote — nunca toca widgets; comunica pela fila (D-03)."""
        iniciado_em = datetime.now()
        try:
            varredura = scanner.varrer(origem, alvo)
        except scanner.ScannerErro as exc:
            self._fila.put(("erro", str(exc)))
            self._fila.put(("fim",))
            return

        self._fila.put(("total", len(varredura.pastas)))

        def ao_concluir(_item, indice: int, total: int) -> None:
            self._fila.put(("progresso", indice, total))

        try:
            resultado = motor.copiar_lote(
                varredura, destino, politica=politica, cancelar=self._evento_cancelar,
                ao_concluir_item=ao_concluir,
            )
        except motor.MotorErro as exc:
            self._fila.put(("erro", str(exc)))
            self._fila.put(("fim",))
            return

        relatorio_execucao = relatorio.consolidar(resultado, iniciado_em, datetime.now())
        texto = relatorio.formatar_texto(relatorio_execucao)
        if resultado.cancelado:
            texto = "Execução CANCELADA — as cópias já concluídas foram preservadas.\n\n" + texto
        if resultado.falha_infra:
            texto = f"AVISO: {resultado.falha_infra}\n\n" + texto
        self._fila.put(("resultado", relatorio_execucao, texto))
        self._fila.put(("fim",))

    # ── eventos da fila ───────────────────────────────────────────────────

    def _drenar_fila(self) -> None:
        try:
            while True:
                mensagem = self._fila.get_nowait()
                tipo = mensagem[0]
                if tipo == "total":
                    self._barra.config(maximum=mensagem[1], value=0)
                elif tipo == "progresso":
                    indice, total = mensagem[1], mensagem[2]
                    self._barra.config(value=indice, maximum=total)
                    self._rotulo_progresso.config(text=f"Executando… {indice} de {total}")
                elif tipo == "resultado":
                    self._ultimo_relatorio = mensagem[1]
                    self._escrever_relatorio(mensagem[2])
                elif tipo == "erro":
                    messagebox.showerror("Falha na execução", mensagem[1], parent=self)
                    self._rotulo_progresso.config(text="Falha — corrija e execute novamente.")
                    self._falhou = True
                elif tipo == "fim":
                    self._finalizar_execucao()
        except queue.Empty:
            pass
        self.after(100, self._drenar_fila)

    def _finalizar_execucao(self) -> None:
        self._executando = False
        self._evento_cancelar = None
        self._btn_executar.config(state="normal" if not self._campos_pendentes() else "disabled")
        self._btn_cancelar.config(state="disabled")
        if self._ultimo_relatorio is not None:
            self._btn_exportar.config(state="normal")
        if not self._falhou:  # estado de sucesso da spec §8; "Falha…" permanece como está
            self._rotulo_progresso.config(text="Concluído — confira o relatório abaixo.")

    def _cancelar(self) -> None:
        if self._evento_cancelar is not None:
            self._evento_cancelar.set()
            self._rotulo_progresso.config(text="Cancelando… as cópias concluídas são preservadas.")

    # ── relatório e saída ─────────────────────────────────────────────────

    def _escrever_relatorio(self, texto: str) -> None:
        self._area_relatorio.config(state="normal")
        self._area_relatorio.delete("1.0", "end")
        self._area_relatorio.insert("1.0", texto)
        self._area_relatorio.config(state="disabled")

    def _exportar(self) -> None:
        if self._ultimo_relatorio is None:
            return
        destino = self._destino.get() or os.getcwd()
        try:
            caminho = relatorio.exportar(self._ultimo_relatorio, destino)
        except OSError as exc:  # EC-04 do relatório: falha de exportação não perde o relatório
            messagebox.showerror("Falha ao exportar", f"Não foi possível gravar o relatório:\n{exc}", parent=self)
            return
        messagebox.showinfo("Relatório exportado", f"Relatório gravado em:\n{caminho}", parent=self)

    def _confirmar_fechar(self) -> None:
        if self._executando:  # EC-04 da interface: confirmar antes de encerrar com lote ativo
            sair = messagebox.askyesno(
                "Execução em andamento",
                "Há um lote em andamento. Cancelar e sair?\n"
                "As cópias já concluídas permanecem no destino.",
                parent=self,
            )
            if not sair:
                return
            if self._evento_cancelar is not None:
                self._evento_cancelar.set()
        self.destroy()
