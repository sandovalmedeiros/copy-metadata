"""Entry point do Copiador de Metadados GeoNetwork.

Execução em desenvolvimento: `python -m app.main` (a partir da raiz do projeto).
Empacotamento: ver `copiador.spec` (PyInstaller, modo one-dir — decisão D-07 do roadmap).
"""
from app.interface import JanelaPrincipal


def main() -> None:
    app = JanelaPrincipal()
    app.mainloop()


if __name__ == "__main__":
    main()
