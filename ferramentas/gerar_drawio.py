"""Gera o diagrama de classes em draw.io (.drawio) e um SVG de pré-visualização.

O draw.io trabalha com o formato ``mxfile`` (XML ``mxGraphModel``). Este script
monta esse XML a partir de uma descrição única das classes e relações, o que
garante que o ``.drawio`` e o ``.svg`` mostrem exatamente o mesmo diagrama.

Uso::

    python ferramentas/gerar_drawio.py

Saídas:

* ``docs/diagrama-classes.drawio`` — editável no draw.io / diagrams.net
* ``docs/diagrama-classes.svg``   — visualização estática (GitHub/navegador)

O arquivo ``.drawio`` abre em https://app.diagrams.net (File > Open) ou no
VS Code com a extensão "Draw.io Integration".
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from xml.dom import minidom
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "docs"

ALTURA_CABECALHO = 30
ALTURA_LINHA = 13
ESPACO = 8

CORES = {
    "interface": "#dae8fc",
    "abstract": "#d5e8d4",
    "concreto": "#eeeeee",
}

ESTILOS_RELACAO = {
    "heranca": "endArrow=block;endFill=0;html=1;",
    "realizacao": "endArrow=block;endFill=0;dashed=1;html=1;",
    "composicao": "startArrow=diamondThin;startFill=1;endArrow=none;html=1;",
    "agregacao": "startArrow=diamondThin;startFill=0;endArrow=none;html=1;",
    "dependencia": "endArrow=open;dashed=1;html=1;",
}


@dataclass(frozen=True)
class Classe:
    """Uma caixa UML de classe.

    Attributes:
        cid: identificador único no arquivo draw.io.
        nome: nome exibido.
        x: posição horizontal.
        y: posição vertical.
        largura: largura da caixa.
        estereotipo: ``<<interface>>``, ``<<abstract>>`` ou vazio.
        atributos: linhas do compartimento de atributos.
        metodos: linhas do compartimento de métodos.
    """

    cid: str
    nome: str
    x: int
    y: int
    largura: int
    estereotipo: str = ""
    atributos: tuple[str, ...] = ()
    metodos: tuple[str, ...] = ()

    @property
    def altura_atributos(self) -> int:
        return ESPACO + ALTURA_LINHA * len(self.atributos) if self.atributos else 0

    @property
    def altura_metodos(self) -> int:
        return ESPACO + ALTURA_LINHA * len(self.metodos) + 4

    @property
    def altura(self) -> int:
        return ALTURA_CABECALHO + self.altura_atributos + self.altura_metodos

    @property
    def cor_cabecalho(self) -> str:
        if self.estereotipo == "<<interface>>":
            return CORES["interface"]
        if self.estereotipo == "<<abstract>>":
            return CORES["abstract"]
        return CORES["concreto"]

    def ponto(self, fx: float, fy: float) -> tuple[float, float]:
        """Converte uma âncora relativa (0..1) em coordenada absoluta."""
        return (self.x + self.largura * fx, self.y + self.altura * fy)


@dataclass(frozen=True)
class Relacao:
    """Uma aresta do diagrama.

    Attributes:
        rid: identificador único.
        origem: id da classe de origem.
        destino: id da classe de destino.
        tipo: heranca, realizacao, composicao, agregacao ou dependencia.
        saida: âncora relativa de saída (x, y) na origem.
        entrada: âncora relativa de entrada (x, y) no destino.
        pontos: pontos intermediários absolutos (roteamento).
        rotulo: texto exibido no meio da aresta.
        mult_origem: multiplicidade junto à origem.
        mult_destino: multiplicidade junto ao destino.
    """

    rid: str
    origem: str
    destino: str
    tipo: str
    saida: tuple[float, float] = (0.5, 0.0)
    entrada: tuple[float, float] = (0.5, 1.0)
    pontos: tuple[tuple[int, int], ...] = ()
    rotulo: str = ""
    mult_origem: str = ""
    mult_destino: str = ""


CLASSES: tuple[Classe, ...] = (
    Classe(
        "combatente",
        "Combatente",
        60,
        40,
        250,
        "<<interface>>",
        (),
        ("+ atacar(alvo): int", "+ defender(): int"),
    ),
    Classe(
        "personagem",
        "Personagem",
        60,
        170,
        310,
        "<<abstract>>",
        (
            "- nome: str",
            "# vida: int",
            "# vida_maxima: int",
            "# forca: int",
            "# defesa: int",
            "# bonus_ataque: int",
            "# bonus_defesa: int",
            "+ ficha: FichaDeStatus",
            "+ inventario: Inventario",
        ),
        (
            "+ atacar(alvo): int",
            "+ defender(): int",
            "+ receber_dano(dano): int",
            "+ curar(valor): int",
            "+ usar_item(nome): str",
            "+ esta_vivo(): bool",
            "+ resumo(): str",
        ),
    ),
    Classe(
        "guerreiro",
        "Guerreiro",
        430,
        170,
        200,
        atributos=(),
        metodos=("+ atacar(alvo): int",),
    ),
    Classe(
        "mago",
        "Mago",
        430,
        255,
        200,
        atributos=("- mana: int",),
        metodos=("+ atacar(alvo): int", "+ recarregar_mana(qtd): int"),
    ),
    Classe(
        "arqueiro",
        "Arqueiro",
        430,
        360,
        200,
        atributos=("- precisao: int",),
        metodos=("+ atacar(alvo): int",),
    ),
    Classe(
        "ficha",
        "FichaDeStatus",
        60,
        480,
        220,
        atributos=("- nivel: int", "- xp: int"),
        metodos=("+ ganhar_xp(qtd): int", "+ subir_nivel(): int", "+ resumo(): str"),
    ),
    Classe(
        "inventario",
        "Inventario",
        60,
        620,
        220,
        atributos=("- itens: list[Item]",),
        metodos=(
            "+ adicionar(item)",
            "+ remover(nome): Item",
            "+ buscar(nome): Item",
            "+ listar(): list",
            "+ vazio(): bool",
        ),
    ),
    Classe(
        "grupo",
        "Grupo",
        60,
        800,
        250,
        atributos=("- nome: str", "- membros: list[Personagem]"),
        metodos=(
            "+ adicionar(personagem)",
            "+ remover(nome): Personagem",
            "+ media_nivel(): float",
        ),
    ),
    Classe(
        "cenario",
        "Cenario",
        720,
        40,
        260,
        "<<abstract>>",
        ("# nome: str", "# classe_favorecida: type", "# bonus: float"),
        ("+ bonus_para(personagem): float", "+ descricao(): str"),
    ),
    Classe(
        "floresta",
        "Floresta",
        720,
        180,
        260,
        metodos=("+ descricao(): str",),
    ),
    Classe(
        "caverna",
        "Caverna",
        720,
        255,
        260,
        metodos=("+ descricao(): str",),
    ),
    Classe(
        "castelo",
        "Castelo",
        720,
        330,
        260,
        metodos=("+ descricao(): str",),
    ),
    Classe(
        "item",
        "Item",
        1100,
        40,
        260,
        "<<abstract>>",
        ("- nome: str",),
        ("+ usar(personagem): str", "+ descricao(): str"),
    ),
    Classe(
        "pocao",
        "Pocao",
        1100,
        180,
        260,
        atributos=("- cura: int",),
        metodos=("+ usar(personagem): str",),
    ),
    Classe(
        "arma",
        "Arma",
        1100,
        270,
        260,
        atributos=("- bonus_ataque: int",),
        metodos=("+ usar(personagem): str",),
    ),
    Classe(
        "armadura",
        "Armadura",
        1100,
        360,
        260,
        atributos=("- bonus_defesa: int",),
        metodos=("+ usar(personagem): str",),
    ),
    Classe(
        "combate",
        "Combate",
        720,
        520,
        320,
        atributos=(
            "- combatente_a: Combatente",
            "- combatente_b: Combatente",
            "- cenario: Cenario",
            "- log: list[RegistroTurno]",
        ),
        metodos=(
            "+ executar(max_turnos): ResultadoCombate",
            "+ executar_turno(a, d): RegistroTurno",
            "+ usar_pocao(combatente, nome): str",
        ),
    ),
    Classe(
        "aldeao",
        "Aldeao",
        1100,
        520,
        240,
        atributos=("- nome: str",),
        metodos=("+ falar(): str",),
    ),
)

RELACOES: tuple[Relacao, ...] = (
    Relacao(
        "r-realiza",
        "personagem",
        "combatente",
        "realizacao",
        saida=(0.5, 0.0),
        entrada=(0.5, 1.0),
        rotulo="realiza",
    ),
    Relacao(
        "r-herda-guerreiro",
        "guerreiro",
        "personagem",
        "heranca",
        saida=(0.0, 0.5),
        entrada=(1.0, 0.12),
    ),
    Relacao(
        "r-herda-mago",
        "mago",
        "personagem",
        "heranca",
        saida=(0.0, 0.5),
        entrada=(1.0, 0.40),
    ),
    Relacao(
        "r-herda-arqueiro",
        "arqueiro",
        "personagem",
        "heranca",
        saida=(0.0, 0.5),
        entrada=(1.0, 0.85),
    ),
    Relacao(
        "r-floresta",
        "floresta",
        "cenario",
        "heranca",
        saida=(0.5, 0.0),
        entrada=(0.5, 1.0),
    ),
    Relacao(
        "r-caverna",
        "caverna",
        "cenario",
        "heranca",
        saida=(1.0, 0.5),
        entrada=(1.0, 0.55),
        pontos=((1015, 282), (1015, 103)),
    ),
    Relacao(
        "r-castelo",
        "castelo",
        "cenario",
        "heranca",
        saida=(0.0, 0.5),
        entrada=(0.0, 0.35),
        pontos=((688, 357), (688, 80)),
    ),
    Relacao(
        "r-pocao",
        "pocao",
        "item",
        "heranca",
        saida=(0.5, 0.0),
        entrada=(0.5, 1.0),
    ),
    Relacao(
        "r-arma",
        "arma",
        "item",
        "heranca",
        saida=(1.0, 0.5),
        entrada=(1.0, 0.40),
        pontos=((1392, 308), (1392, 76)),
    ),
    Relacao(
        "r-armadura",
        "armadura",
        "item",
        "heranca",
        saida=(0.0, 0.5),
        entrada=(0.0, 0.17),
        pontos=((1068, 398), (1068, 55)),
    ),
    Relacao(
        "r-compoe-ficha",
        "personagem",
        "ficha",
        "composicao",
        saida=(0.35, 1.0),
        entrada=(0.5, 0.0),
        rotulo="compõe",
        mult_origem="1",
        mult_destino="1",
    ),
    Relacao(
        "r-compoe-inventario",
        "personagem",
        "inventario",
        "composicao",
        saida=(0.9, 1.0),
        entrada=(1.0, 0.5),
        pontos=((339, 684), (280, 684)),
        rotulo="compõe",
        mult_origem="1",
        mult_destino="1",
    ),
    Relacao(
        "r-agrega-grupo",
        "grupo",
        "personagem",
        "agregacao",
        saida=(1.0, 0.5),
        entrada=(1.0, 0.60),
        pontos=((405, 857), (405, 325)),
        rotulo="agrega",
        mult_origem="1",
        mult_destino="0..5",
    ),
    Relacao(
        "r-agrega-inventario",
        "inventario",
        "item",
        "agregacao",
        saida=(0.0, 0.5),
        entrada=(0.3, 0.0),
        pontos=((28, 684), (28, 22), (1178, 22)),
        rotulo="agrega",
        mult_origem="1",
        mult_destino="0..*",
    ),
    Relacao(
        "r-consome-combatente",
        "combate",
        "combatente",
        "dependencia",
        saida=(0.0, 0.55),
        entrada=(1.0, 0.5),
        pontos=((655, 598), (655, 74)),
        rotulo="consome",
    ),
    Relacao(
        "r-consome-cenario",
        "combate",
        "cenario",
        "dependencia",
        saida=(1.0, 0.5),
        entrada=(1.0, 0.80),
        pontos=((1058, 590), (1058, 132)),
        rotulo="consome",
    ),
    Relacao(
        "r-consome-item",
        "combate",
        "item",
        "dependencia",
        saida=(1.0, 0.25),
        entrada=(0.0, 0.78),
        pontos=((1086, 555), (1086, 109)),
        rotulo="consome",
    ),
    Relacao(
        "r-consome-ficha",
        "combate",
        "ficha",
        "dependencia",
        saida=(0.0, 0.85),
        entrada=(1.0, 0.72),
        pontos=((420, 640), (420, 563)),
        rotulo="consome",
    ),
)

NOTAS: tuple[tuple[str, str, tuple[str, ...], int, int, int, int], ...] = (
    (
        "nota-aldeao",
        "Aldeao não realiza Combatente",
        ("Combate recusa com AlvoInvalidoError.",),
        1100,
        620,
        240,
        64,
    ),
    (
        "legenda",
        "LEGENDA UML",
        (
            "+ público   # protegido   - privado",
            "Triângulo vazio = herança / realização",
            "Losango cheio = composição (parte morre com o todo)",
            "Losango vazio = agregação (parte sobrevive ao todo)",
            "Seta tracejada = dependência (consome)",
        ),
        720,
        760,
        400,
        124,
    ),
)

TITULO = "Sistema de RPG — Diagrama de Classes (POO)"
LARGURA_PAGINA = 1500
ALTURA_PAGINA = 1000


def classe_por_id(cid: str) -> Classe:
    """Busca uma classe pelo id."""
    for classe in CLASSES:
        if classe.cid == cid:
            return classe
    raise KeyError(cid)


# --------------------------------------------------------------------- draw.io


def gerar_drawio() -> str:
    """Monta o XML ``mxfile`` completo e devolve como texto formatado."""
    mxfile = ET.Element(
        "mxfile",
        host="app.diagrams.net",
        agent="Socrates",
        version="24.7.17",
        type="device",
    )
    diagrama = ET.SubElement(
        mxfile, "diagram", id="rpg-poo-classes", name="Classes RPG POO"
    )
    modelo = ET.SubElement(
        diagrama,
        "mxGraphModel",
        dx="1600",
        dy="1000",
        grid="1",
        gridSize="10",
        guides="1",
        tooltips="1",
        connect="1",
        arrows="1",
        fold="1",
        page="1",
        pageScale="1",
        pageWidth=str(LARGURA_PAGINA),
        pageHeight=str(ALTURA_PAGINA),
        math="0",
        shadow="0",
    )
    raiz = ET.SubElement(modelo, "root")
    ET.SubElement(raiz, "mxCell", id="0")
    ET.SubElement(raiz, "mxCell", id="1", parent="0")

    for classe in CLASSES:
        _celula_classe(raiz, classe)
    for relacao in RELACOES:
        _celula_relacao(raiz, relacao)
    for nid, titulo, linhas, x, y, largura, altura in NOTAS:
        _celula_nota(raiz, nid, titulo, linhas, x, y, largura, altura)
    _celula_titulo(raiz)

    bruto = ET.tostring(mxfile, encoding="unicode")
    return minidom.parseString(bruto).toprettyxml(indent="  ", encoding="UTF-8").decode(
        "UTF-8"
    )


def _celula_classe(raiz: ET.Element, classe: Classe) -> None:
    """Adiciona uma classe como swimlane UML com dois compartimentos."""
    valor = (
        f"{escape(classe.estereotipo)}<br><b>{escape(classe.nome)}</b>"
        if classe.estereotipo
        else f"<b>{escape(classe.nome)}</b>"
    )
    estilo = (
        "swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;"
        "horizontal=1;startSize="
        f"{ALTURA_CABECALHO};horizontalStack=0;resizeParent=1;resizeParentMax=0;"
        "resizeLast=0;collapsible=0;marginBottom=0;html=1;whiteSpace=wrap;"
        f"fillColor={classe.cor_cabecalho};strokeColor=#333333;fontSize=11;"
    )
    celula = ET.SubElement(
        raiz,
        "mxCell",
        id=classe.cid,
        value=valor,
        style=estilo,
        vertex="1",
        parent="1",
    )
    ET.SubElement(
        celula,
        "mxGeometry",
        x=str(classe.x),
        y=str(classe.y),
        width=str(classe.largura),
        height=str(classe.altura),
        **{"as": "geometry"},
    )

    if classe.atributos:
        _filho_texto(
            raiz,
            f"{classe.cid}-atributos",
            "<br>".join(escape(a) for a in classe.atributos),
            classe.cid,
            0,
            ALTURA_CABECALHO,
            classe.altura_atributos,
        )
    _filho_texto(
        raiz,
        f"{classe.cid}-metodos",
        "<br>".join(escape(m) for m in classe.metodos),
        classe.cid,
        0,
        ALTURA_CABECALHO + classe.altura_atributos,
        classe.altura_metodos,
    )


def _filho_texto(
    raiz: ET.Element,
    cid: str,
    valor: str,
    pai: str,
    x: int,
    y: int,
    altura: int,
) -> None:
    """Adiciona um compartimento de texto dentro de uma swimlane."""
    estilo = (
        "text;strokeColor=none;fillColor=none;align=left;verticalAlign=top;"
        "spacingLeft=6;spacingRight=4;overflow=hidden;rotatable=0;"
        "points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;"
        "fontSize=10;fontFamily=Consolas;"
    )
    largura = classe_por_id(pai).largura
    celula = ET.SubElement(
        raiz,
        "mxCell",
        id=cid,
        value=valor,
        style=estilo,
        vertex="1",
        parent=pai,
    )
    ET.SubElement(
        celula,
        "mxGeometry",
        x=str(x),
        y=str(y),
        width=str(largura),
        height=str(altura),
        **{"as": "geometry"},
    )


def _celula_relacao(raiz: ET.Element, relacao: Relacao) -> None:
    """Adiciona uma aresta com portas, roteamento e rótulos."""
    sx, sy = relacao.saida
    ex, ey = relacao.entrada
    estilo = (
        ESTILOS_RELACAO[relacao.tipo]
        + "edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#333333;fontSize=9;"
        f"exitX={sx};exitY={sy};exitDx=0;exitDy=0;"
        f"entryX={ex};entryY={ey};entryDx=0;entryDy=0;"
    )
    celula = ET.SubElement(
        raiz,
        "mxCell",
        id=relacao.rid,
        value=escape(relacao.rotulo),
        style=estilo,
        edge="1",
        parent="1",
        source=relacao.origem,
        target=relacao.destino,
    )
    geometria = ET.SubElement(
        celula, "mxGeometry", relative="1", **{"as": "geometry"}
    )
    if relacao.pontos:
        pontos = ET.SubElement(geometria, "Array", **{"as": "points"})
        for px, py in relacao.pontos:
            ET.SubElement(pontos, "mxPoint", x=str(px), y=str(py))

    if relacao.rotulo:
        _rotulo_aresta(raiz, relacao.rid, "lbl", relacao.rotulo, 0.0, -12)
    if relacao.mult_origem:
        _rotulo_aresta(
            raiz, relacao.rid, "mult-origem", relacao.mult_origem, -0.92, 10
        )
    if relacao.mult_destino:
        _rotulo_aresta(raiz, relacao.rid, "mult-destino", relacao.mult_destino, 0.92, -10)


def _rotulo_aresta(
    raiz: ET.Element,
    aresta: str,
    sufixo: str,
    texto: str,
    posicao: float,
    deslocamento_y: int,
) -> None:
    """Adiciona um rótulo posicionado sobre a aresta."""
    estilo = (
        "edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;"
        "points=[];fontSize=9;fontFamily=Segoe UI;"
    )
    celula = ET.SubElement(
        raiz,
        "mxCell",
        id=f"{aresta}-{sufixo}",
        value=escape(texto),
        style=estilo,
        vertex="1",
        connectable="0",
        parent=aresta,
    )
    geometria = ET.SubElement(
        celula, "mxGeometry", x=str(posicao), relative="1", **{"as": "geometry"}
    )
    ET.SubElement(
        geometria,
        "mxPoint",
        x="0",
        y=str(deslocamento_y),
        **{"as": "offset"},
    )


def _celula_nota(
    raiz: ET.Element,
    nid: str,
    titulo: str,
    linhas: tuple[str, ...],
    x: int,
    y: int,
    largura: int,
    altura: int,
) -> None:
    """Adiciona uma nota (post-it) UML."""
    estilo = (
        "shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;darkOpacity=0.05;"
        "fillColor=#fff2cc;strokeColor=#d6b656;align=left;verticalAlign=top;"
        "spacing=6;fontSize=10;"
    )
    valor = f"<b>{escape(titulo)}</b><br>" + "<br>".join(escape(l) for l in linhas)
    celula = ET.SubElement(
        raiz, "mxCell", id=nid, value=valor, style=estilo, vertex="1", parent="1"
    )
    ET.SubElement(
        celula,
        "mxGeometry",
        x=str(x),
        y=str(y),
        width=str(largura),
        height=str(altura),
        **{"as": "geometry"},
    )


def _celula_titulo(raiz: ET.Element) -> None:
    """Adiciona o título do diagrama."""
    estilo = (
        "text;html=1;fontSize=18;fontStyle=1;align=left;verticalAlign=middle;"
        "strokeColor=none;fillColor=none;whiteSpace=wrap;"
    )
    celula = ET.SubElement(
        raiz,
        "mxCell",
        id="titulo",
        value=escape(TITULO),
        style=estilo,
        vertex="1",
        parent="1",
    )
    ET.SubElement(
        celula,
        "mxGeometry",
        x="60",
        y="0",
        width="700",
        height="30",
        **{"as": "geometry"},
    )


# ------------------------------------------------------------------------- SVG


def _rota(relacao: Relacao) -> list[tuple[float, float]]:
    """Devolve a polilinha completa da relação em coordenadas absolutas."""
    origem = classe_por_id(relacao.origem)
    destino = classe_por_id(relacao.destino)
    return [
        origem.ponto(*relacao.saida),
        *[(float(x), float(y)) for x, y in relacao.pontos],
        destino.ponto(*relacao.entrada),
    ]


def _comprimento(rota: list[tuple[float, float]]) -> float:
    total = 0.0
    for (x1, y1), (x2, y2) in zip(rota, rota[1:]):
        total += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return total


def _ponto_na_rota(
    rota: list[tuple[float, float]], distancia: float
) -> tuple[float, float]:
    """Caminha ``distancia`` ao longo da polilinha e devolve o ponto."""
    restante = distancia
    for (x1, y1), (x2, y2) in zip(rota, rota[1:]):
        trecho = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if restante <= trecho or trecho == 0:
            fator = 0.0 if trecho == 0 else restante / trecho
            return (x1 + (x2 - x1) * fator, y1 + (y2 - y1) * fator)
        restante -= trecho
    return rota[-1]


def _marcador(relacao: Relacao) -> str:
    if relacao.tipo in ("heranca", "realizacao"):
        return 'marker-end="url(#tri)"'
    if relacao.tipo == "dependencia":
        return 'marker-end="url(#seta)"'
    if relacao.tipo == "composicao":
        return 'marker-start="url(#losango-cheio)"'
    if relacao.tipo == "agregacao":
        return 'marker-start="url(#losango-vazio)"'
    return ""


def _svg_relacao(relacao: Relacao) -> str:
    """Desenha a aresta, o rótulo central e as multiplicidades."""
    rota = _rota(relacao)
    pontos = " ".join(f"{x:.1f},{y:.1f}" for x, y in rota)
    tracejado = (
        ' stroke-dasharray="6 4"'
        if relacao.tipo in ("realizacao", "dependencia")
        else ""
    )

    partes = [
        f'<polyline points="{pontos}" fill="none" stroke="#333" '
        f'stroke-width="1.3"{tracejado} {_marcador(relacao)}/>'
    ]

    total = _comprimento(rota)
    if relacao.rotulo:
        mx, my = _ponto_na_rota(rota, total / 2)
        largura = 6.2 * len(relacao.rotulo) + 8
        partes.append(
            f'<rect x="{mx - largura / 2:.1f}" y="{my - 8:.1f}" width="{largura:.1f}" '
            f'height="14" fill="#ffffff" opacity="0.92"/>'
            f'<text x="{mx:.1f}" y="{my + 3:.1f}" text-anchor="middle" '
            f'font-size="9" fill="#555">{escape(relacao.rotulo)}</text>'
        )
    if relacao.mult_origem:
        ox, oy = _ponto_na_rota(rota, 16)
        partes.append(
            f'<text x="{ox:.1f}" y="{oy - 6:.1f}" font-size="9" fill="#333">'
            f"{escape(relacao.mult_origem)}</text>"
        )
    if relacao.mult_destino:
        dx, dy = _ponto_na_rota(rota, max(total - 16, 0))
        partes.append(
            f'<text x="{dx + 4:.1f}" y="{dy + 12:.1f}" font-size="9" fill="#333">'
            f"{escape(relacao.mult_destino)}</text>"
        )
    return "".join(partes)


def _svg_classe(classe: Classe) -> str:
    """Desenha uma caixa UML com cabeçalho, atributos e métodos."""
    x, y, w, h = classe.x, classe.y, classe.largura, classe.altura
    partes = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#ffffff" '
        f'stroke="#333" stroke-width="1.2"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{ALTURA_CABECALHO}" '
        f'fill="{classe.cor_cabecalho}" stroke="#333" stroke-width="1.2"/>',
    ]

    if classe.estereotipo:
        partes.append(
            f'<text x="{x + w / 2:.1f}" y="{y + 12}" text-anchor="middle" '
            f'font-size="8.5" font-style="italic" fill="#333">'
            f"{escape(classe.estereotipo)}</text>"
        )
        partes.append(
            f'<text x="{x + w / 2:.1f}" y="{y + 25}" text-anchor="middle" '
            f'font-size="11.5" font-weight="bold" fill="#111">'
            f"{escape(classe.nome)}</text>"
        )
    else:
        partes.append(
            f'<text x="{x + w / 2:.1f}" y="{y + 20}" text-anchor="middle" '
            f'font-size="11.5" font-weight="bold" fill="#111">'
            f"{escape(classe.nome)}</text>"
        )

    cursor = y + ALTURA_CABECALHO
    if classe.atributos:
        partes.append(
            f'<line x1="{x}" y1="{cursor}" x2="{x + w}" y2="{cursor}" '
            f'stroke="#333" stroke-width="1"/>'
        )
        for indice, atributo in enumerate(classe.atributos):
            partes.append(
                f'<text x="{x + 7}" y="{cursor + 13 + indice * ALTURA_LINHA}" '
                f'font-size="9.5" font-family="Consolas, monospace" fill="#222">'
                f"{escape(atributo)}</text>"
            )
        cursor += classe.altura_atributos

    partes.append(
        f'<line x1="{x}" y1="{cursor}" x2="{x + w}" y2="{cursor}" '
        f'stroke="#333" stroke-width="1"/>'
    )
    for indice, metodo in enumerate(classe.metodos):
        partes.append(
            f'<text x="{x + 7}" y="{cursor + 13 + indice * ALTURA_LINHA}" '
            f'font-size="9.5" font-family="Consolas, monospace" fill="#222">'
            f"{escape(metodo)}</text>"
        )
    return "".join(partes)


def _svg_nota(
    titulo: str, linhas: tuple[str, ...], x: int, y: int, largura: int, altura: int
) -> str:
    """Desenha uma nota amarela com título em negrito e linhas de texto."""
    partes = [
        f'<path d="M{x},{y} h{largura - 14} l14,14 v{altura - 14} h-{largura} z" '
        'fill="#fff2cc" stroke="#d6b656" stroke-width="1"/>',
        f'<text x="{x + 8}" y="{y + 18}" font-size="10" font-weight="bold" '
        f'fill="#333">{escape(titulo)}</text>',
    ]
    for indice, linha in enumerate(linhas):
        partes.append(
            f'<text x="{x + 8}" y="{y + 33 + indice * 13}" font-size="9" fill="#333">'
            f"{escape(linha)}</text>"
        )
    return "".join(partes)


def gerar_svg() -> str:
    """Monta o SVG de pré-visualização a partir do mesmo modelo."""
    partes = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{LARGURA_PAGINA}" '
        f'height="{ALTURA_PAGINA}" viewBox="0 0 {LARGURA_PAGINA} {ALTURA_PAGINA}" '
        'font-family="Segoe UI, Arial, sans-serif">',
        "<defs>",
        '<marker id="tri" markerWidth="12" markerHeight="12" refX="11" refY="6" '
        'orient="auto" markerUnits="userSpaceOnUse">'
        '<path d="M0,0 L12,6 L0,12 z" fill="#ffffff" stroke="#333" stroke-width="1"/></marker>',
        '<marker id="seta" markerWidth="12" markerHeight="12" refX="11" refY="6" '
        'orient="auto" markerUnits="userSpaceOnUse">'
        '<path d="M0,1 L11,6 L0,11" fill="none" stroke="#333" stroke-width="1.2"/></marker>',
        '<marker id="losango-cheio" markerWidth="14" markerHeight="12" refX="1" refY="6" '
        'orient="auto" markerUnits="userSpaceOnUse">'
        '<path d="M1,6 L7,1 L13,6 L7,11 z" fill="#333" stroke="#333"/></marker>',
        '<marker id="losango-vazio" markerWidth="14" markerHeight="12" refX="1" refY="6" '
        'orient="auto" markerUnits="userSpaceOnUse">'
        '<path d="M1,6 L7,1 L13,6 L7,11 z" fill="#ffffff" stroke="#333"/></marker>',
        "</defs>",
        f'<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="60" y="20" font-size="18" font-weight="bold" fill="#111">'
        f"{escape(TITULO)}</text>",
    ]
    for classe in CLASSES:
        partes.append(f"<g>{_svg_classe(classe)}</g>")
    for relacao in RELACOES:
        partes.append(f"<g>{_svg_relacao(relacao)}</g>")
    for nid, titulo, linhas, x, y, largura, altura in NOTAS:
        partes.append(_svg_nota(titulo, linhas, x, y, largura, altura))
    partes.append("</svg>")
    return "\n".join(partes)


def main() -> None:
    """Gera os dois arquivos e valida o XML produzido."""
    DOCS.mkdir(exist_ok=True)

    drawio = DOCS / "diagrama-classes.drawio"
    drawio.write_text(gerar_drawio(), encoding="utf-8")

    svg = DOCS / "diagrama-classes.svg"
    svg.write_text(gerar_svg(), encoding="utf-8")

    arvore = ET.parse(drawio)
    celulas = list(arvore.getroot().iter("mxCell"))
    ids = [celula.get("id") for celula in celulas if celula.get("id")]
    duplicados = {i for i in ids if ids.count(i) > 1}
    if duplicados:
        raise SystemExit(f"ids duplicados no draw.io: {sorted(duplicados)}")

    conhecidos = set(ids)
    for celula in celulas:
        for atributo in ("parent", "source", "target"):
            valor = celula.get(atributo)
            if valor and valor not in conhecidos:
                raise SystemExit(
                    f"referencia quebrada: {celula.get('id')} -> {atributo}={valor}"
                )

    print(f"OK  {drawio.relative_to(RAIZ)}  ({len(celulas)} celulas mxCell)")
    print(f"OK  {svg.relative_to(RAIZ)}  ({len(CLASSES)} classes, {len(RELACOES)} relacoes)")


if __name__ == "__main__":
    main()
