"""Gera todos os diagramas do projeto (draw.io + SVG de pré-visualização).

Uso::

    python ferramentas/gerar_diagramas.py

Saídas em ``docs/``:

* ``diagrama-classes``          — classes, herança, composição, agregação
* ``diagrama-casos-de-uso``     — atores, fronteira do sistema, UC01–UC08
* ``diagrama-visao-de-projeto`` — camadas, responsabilidades e acoplamento
* ``diagrama-rastreabilidade``  — exigência → arquivo → teste

Todos os arquivos são validados antes de serem gravados (ids, referências,
sobreposição de caixas e aresta atravessando nó).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gerar_drawio  # noqa: E402  (script irmao, importado apos ajustar o sys.path)
from diagramas import casos_uso, rastreabilidade, visao  # noqa: E402


def main() -> None:
    """Executa todos os geradores e informa os arquivos produzidos."""
    gerar_drawio.main()
    for modulo in (casos_uso, visao, rastreabilidade):
        for caminho in modulo.gerar():
            print(f"OK  {caminho.relative_to(gerar_drawio.RAIZ)}")


if __name__ == "__main__":
    main()
