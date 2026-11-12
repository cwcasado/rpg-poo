"""Componentes compartilhados para gerar diagramas no draw.io e um SVG de prévia.

Cada diagrama é descrito como uma lista de nós (caixas, elipses, atores, notas,
faixas) e arestas. :meth:`Diagrama.gerar` escreve o ``.drawio`` (XML ``mxfile``,
editável no draw.io) e o ``.svg`` (visualização) a partir do mesmo modelo — os
dois arquivos não podem divergir.

O módulo também valida o resultado antes de gravar:

* ids duplicados;
* referências quebradas (``source``/``target`` inexistente);
* nós sobrepostos;
* aresta atravessando um nó que não é a origem nem o destino.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from xml.dom import minidom
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "docs"

AZUL = "#dae8fc"
VERDE = "#d5e8d4"
AMARELO = "#fff2cc"
CINZA = "#f5f5f5"
BRANCO = "#ffffff"
BORDA = "#333333"

ESTILOS_ARESTA = {
    "heranca": "endArrow=block;endFill=0;",
    "realizacao": "endArrow=block;endFill=0;dashed=1;",
    "composicao": "startArrow=diamondThin;startFill=1;endArrow=none;",
    "agregacao": "startArrow=diamondThin;startFill=0;endArrow=none;",
    "dependencia": "endArrow=open;dashed=1;",
    "associacao": "endArrow=none;",
    "usa": "endArrow=open;",
    "fluxo": "endArrow=open;",
}


@dataclass(frozen=True)
class No:
    """Um elemento com posição e tamanho fixos no diagrama.

    Attributes:
        nid: identificador único (usado como id no draw.io).
        linhas: texto do nó, uma entrada por linha.
        x: posição horizontal.
        y: posição vertical.
        largura: largura em pixels.
        altura: altura em pixels.
        forma: caixa, elipse, ator, nota, faixa ou texto.
        fundo: cor de preenchimento.
        contorno: cor da borda.
        fonte: tamanho da fonte.
        negrito: aplica negrito ao texto.
        alinhamento: center ou left.
        valign: middle ou top.
        tracejado: borda tracejada.
        destaque_primeira: primeira linha em negrito.
        extra: estilo draw.io adicional.
    """

    nid: str
    linhas: tuple[str, ...]
    x: int
    y: int
    largura: int
    altura: int
    forma: str = "caixa"
    fundo: str = BRANCO
    contorno: str = BORDA
    fonte: int = 10
    negrito: bool = False
    alinhamento: str = "center"
    valign: str = "middle"
    tracejado: bool = False
    destaque_primeira: bool = False
    extra: str = ""

    def ponto(self, fx: float, fy: float) -> tuple[float, float]:
        """Converte uma âncora relativa (0..1) em coordenada absoluta."""
        return (self.x + self.largura * fx, self.y + self.altura * fy)


@dataclass(frozen=True)
class Aresta:
    """Uma ligação entre dois nós.

    Attributes:
        aid: identificador único.
        origem: id do nó de origem.
        destino: id do nó de destino.
        tipo: chave de :data:`ESTILOS_ARESTA`.
        saida: âncora relativa de saída na origem.
        entrada: âncora relativa de entrada no destino.
        pontos: pontos intermediários absolutos (roteamento ortogonal).
        rotulo: texto no meio da aresta.
        cor: cor do traço.
        largura: espessura do traço.
        extra: estilo draw.io adicional.
    """

    aid: str
    origem: str
    destino: str
    tipo: str = "fluxo"
    saida: tuple[float, float] = (0.5, 0.0)
    entrada: tuple[float, float] = (0.5, 1.0)
    pontos: tuple[tuple[int, int], ...] = ()
    rotulo: str = ""
    cor: str = BORDA
    largura: float = 1.2
    extra: str = ""


@dataclass
class Diagrama:
    """Modelo de um diagrama e escritor dos formatos draw.io e SVG.

    Attributes:
        arquivo: nome-base dos arquivos em ``docs/`` (sem extensão).
        id_diagrama: id da página no draw.io.
        nome: nome da página exibido no draw.io.
        largura: largura da página.
        altura: altura da página.
        titulo: título exibido no topo (SVG) e como célula de texto.
        nos: elementos do diagrama.
        arestas: ligações entre os elementos.
    """

    arquivo: str
    id_diagrama: str
    nome: str
    largura: int
    altura: int
    titulo: str
    nos: list[No] = field(default_factory=list)
    arestas: list[Aresta] = field(default_factory=list)

    # ------------------------------------------------------------------ modelo

    def caixa(
        self,
        nid: str,
        linhas: str | tuple[str, ...],
        x: int,
        y: int,
        largura: int,
        altura: int,
        **kwargs: object,
    ) -> No:
        """Adiciona uma caixa retangular."""
        return self._adicionar(No(nid, _linhas(linhas), x, y, largura, altura, **kwargs))

    def elipse(
        self,
        nid: str,
        linhas: str | tuple[str, ...],
        x: int,
        y: int,
        largura: int,
        altura: int,
        **kwargs: object,
    ) -> No:
        """Adiciona uma elipse (caso de uso)."""
        return self._adicionar(
            No(nid, _linhas(linhas), x, y, largura, altura, forma="elipse", **kwargs)
        )

    def ator(self, nid: str, nome: str, x: int, y: int) -> No:
        """Adiciona um ator UML (boneco palito) com o nome abaixo."""
        return self._adicionar(
            No(nid, (nome,), x, y, 40, 80, forma="ator", fundo=BRANCO)
        )

    def nota(
        self,
        nid: str,
        linhas: str | tuple[str, ...],
        x: int,
        y: int,
        largura: int,
        altura: int,
    ) -> No:
        """Adiciona uma nota amarela com a primeira linha em negrito."""
        return self._adicionar(
            No(
                nid,
                _linhas(linhas),
                x,
                y,
                largura,
                altura,
                forma="nota",
                fundo=AMARELO,
                contorno="#d6b656",
                alinhamento="left",
                valign="top",
                destaque_primeira=True,
                fonte=9,
            )
        )

    def faixa(
        self,
        nid: str,
        titulo: str,
        x: int,
        y: int,
        largura: int,
        altura: int,
        fundo: str = "#f7f7f7",
        contorno: str = "#999999",
        tracejado: bool = True,
    ) -> No:
        """Adiciona uma faixa/limite (camada ou fronteira do sistema)."""
        return self._adicionar(
            No(
                nid,
                (titulo,),
                x,
                y,
                largura,
                altura,
                forma="faixa",
                fundo=fundo,
                contorno=contorno,
                fonte=12,
                negrito=True,
                alinhamento="left",
                valign="top",
                tracejado=tracejado,
            )
        )

    def texto(
        self,
        nid: str,
        linhas: str | tuple[str, ...],
        x: int,
        y: int,
        largura: int,
        altura: int,
        **kwargs: object,
    ) -> No:
        """Adiciona texto solto (título de coluna, rótulo de linha)."""
        kwargs.setdefault("alinhamento", "left")
        return self._adicionar(
            No(nid, _linhas(linhas), x, y, largura, altura, forma="texto", **kwargs)
        )

    def conectar(
        self,
        aid: str,
        origem: str,
        destino: str,
        tipo: str = "fluxo",
        saida: tuple[float, float] = (0.5, 0.0),
        entrada: tuple[float, float] = (0.5, 1.0),
        pontos: tuple[tuple[int, int], ...] = (),
        rotulo: str = "",
        cor: str = BORDA,
        largura: float = 1.2,
        extra: str = "",
    ) -> Aresta:
        """Adiciona uma aresta entre dois nós."""
        return self._adicionar_aresta(
            Aresta(
                aid,
                origem,
                destino,
                tipo,
                saida,
                entrada,
                pontos,
                rotulo,
                cor,
                largura,
                extra,
            )
        )

    def _adicionar(self, no: No) -> No:
        self.nos.append(no)
        return no

    def _adicionar_aresta(self, aresta: Aresta) -> Aresta:
        self.arestas.append(aresta)
        return aresta

    def mapa(self) -> dict[str, No]:
        """Índice id -> nó."""
        return {no.nid: no for no in self.nos}

    # ------------------------------------------------------------------ validação

    def validar(self) -> None:
        """Falha rápido se o modelo tiver referência quebrada ou sobreposição."""
        ids = [no.nid for no in self.nos] + [a.aid for a in self.arestas]
        duplicados = {i for i in ids if ids.count(i) > 1}
        if duplicados:
            raise SystemExit(f"{self.arquivo}: ids duplicados: {sorted(duplicados)}")

        mapa = self.mapa()
        for aresta in self.arestas:
            for referencia in (aresta.origem, aresta.destino):
                if referencia not in mapa:
                    raise SystemExit(
                        f"{self.arquivo}: aresta {aresta.aid} aponta para {referencia}"
                    )

        moveis = [no for no in self.nos if no.forma not in ("faixa", "texto")]
        for indice, primeiro in enumerate(moveis):
            for segundo in moveis[indice + 1 :]:
                if _sobrepoe(primeiro, segundo):
                    raise SystemExit(
                        f"{self.arquivo}: {primeiro.nid} sobrepõe {segundo.nid}"
                    )

        for aresta in self.arestas:
            rota = self._rota(aresta)
            for x, y in _amostrar(rota):
                for no in moveis:
                    if no.nid in (aresta.origem, aresta.destino):
                        continue
                    if _dentro(no, x, y):
                        raise SystemExit(
                            f"{self.arquivo}: aresta {aresta.aid} atravessa {no.nid}"
                        )

    # ------------------------------------------------------------------ draw.io

    def gerar(self) -> tuple[Path, Path]:
        """Valida o modelo e grava ``.drawio`` e ``.svg`` em ``docs/``."""
        self.validar()
        DOCS.mkdir(exist_ok=True)
        drawio = DOCS / f"{self.arquivo}.drawio"
        svg = DOCS / f"{self.arquivo}.svg"
        drawio.write_text(self._xml(), encoding="utf-8")
        svg.write_text(self._svg(), encoding="utf-8")
        return drawio, svg

    def _xml(self) -> str:
        mxfile = ET.Element(
            "mxfile",
            host="app.diagrams.net",
            agent="Socrates",
            version="24.7.17",
            type="device",
        )
        diagrama = ET.SubElement(
            mxfile, "diagram", id=self.id_diagrama, name=self.nome
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
            pageWidth=str(self.largura),
            pageHeight=str(self.altura),
            math="0",
            shadow="0",
        )
        raiz = ET.SubElement(modelo, "root")
        ET.SubElement(raiz, "mxCell", id="0")
        ET.SubElement(raiz, "mxCell", id="1", parent="0")

        titulo = No(
            "titulo-diagrama",
            (self.titulo,),
            60,
            2,
            900,
            30,
            forma="texto",
            fonte=18,
            negrito=True,
        )
        self._celula_no(raiz, titulo)

        for no in self._ordenados():
            self._celula_no(raiz, no)
        for aresta in self.arestas:
            self._celula_aresta(raiz, aresta)

        bruto = ET.tostring(mxfile, encoding="unicode")
        return minidom.parseString(bruto).toprettyxml(
            indent="  ", encoding="UTF-8"
        ).decode("UTF-8")

    def _ordenados(self) -> list[No]:
        fundo = [no for no in self.nos if no.forma == "faixa"]
        demais = [no for no in self.nos if no.forma != "faixa"]
        return fundo + demais

    def _celula_no(self, raiz: ET.Element, no: No) -> None:
        valor = "<br>".join(escape(linha) for linha in no.linhas)
        if no.destaque_primeira and no.linhas:
            primeira = escape(no.linhas[0])
            resto = "<br>".join(escape(linha) for linha in no.linhas[1:])
            valor = f"<b>{primeira}</b>" + (f"<br>{resto}" if resto else "")
        celula = ET.SubElement(
            raiz,
            "mxCell",
            id=no.nid,
            value=valor,
            style=self._estilo_no(no),
            vertex="1",
            parent="1",
        )
        ET.SubElement(
            celula,
            "mxGeometry",
            x=str(no.x),
            y=str(no.y),
            width=str(no.largura),
            height=str(no.altura),
            **{"as": "geometry"},
        )

    def _estilo_no(self, no: No) -> str:
        base = {
            "caixa": "rounded=0;whiteSpace=wrap;html=1;",
            "elipse": "ellipse;whiteSpace=wrap;html=1;",
            "ator": (
                "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;"
                "html=1;outlineConnect=0;"
            ),
            "nota": (
                "shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;"
                "darkOpacity=0.05;spacing=8;"
            ),
            "faixa": "rounded=0;whiteSpace=wrap;html=1;",
            "texto": "text;html=1;strokeColor=none;fillColor=none;",
        }[no.forma]
        partes = [base.rstrip(";")]
        if no.forma in ("caixa", "elipse", "faixa"):
            partes.append(f"fillColor={no.fundo}")
            partes.append(f"strokeColor={no.contorno}")
        if no.forma == "ator":
            partes.append("fillColor=none")
            partes.append(f"strokeColor={no.contorno}")
        if no.forma != "ator":
            partes.append(f"align={no.alinhamento}")
            partes.append(f"verticalAlign={no.valign}")
        partes.append(f"fontSize={no.fonte}")
        if no.negrito:
            partes.append("fontStyle=1")
        if no.tracejado:
            partes.append("dashed=1")
        if no.forma == "faixa":
            partes.append("spacing=8")
        if no.extra:
            partes.append(no.extra)
        return ";".join(partes) + ";"

    def _celula_aresta(self, raiz: ET.Element, aresta: Aresta) -> None:
        sx, sy = aresta.saida
        ex, ey = aresta.entrada
        roteamento = "orthogonalEdgeStyle" if aresta.pontos else "none"
        estilo = (
            ESTILOS_ARESTA[aresta.tipo]
            + f"edgeStyle={roteamento};rounded=0;html=1;fontSize=9;"
            f"strokeColor={aresta.cor};strokeWidth={aresta.largura};"
            f"exitX={sx};exitY={sy};exitDx=0;exitDy=0;"
            f"entryX={ex};entryY={ey};entryDx=0;entryDy=0;"
        )
        if aresta.extra:
            estilo += aresta.extra
        celula = ET.SubElement(
            raiz,
            "mxCell",
            id=aresta.aid,
            value=escape(aresta.rotulo),
            style=estilo,
            edge="1",
            parent="1",
            source=aresta.origem,
            target=aresta.destino,
        )
        geometria = ET.SubElement(
            celula, "mxGeometry", relative="1", **{"as": "geometry"}
        )
        if aresta.pontos:
            pontos = ET.SubElement(geometria, "Array", **{"as": "points"})
            for px, py in aresta.pontos:
                ET.SubElement(pontos, "mxPoint", x=str(px), y=str(py))
        if aresta.rotulo:
            self._rotulo_aresta(raiz, aresta.aid, aresta.rotulo)

    def _rotulo_aresta(self, raiz: ET.Element, aresta: str, texto: str) -> None:
        estilo = (
            "edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;"
            "points=[];fontSize=9;"
        )
        celula = ET.SubElement(
            raiz,
            "mxCell",
            id=f"{aresta}-rotulo",
            value=escape(texto),
            style=estilo,
            vertex="1",
            connectable="0",
            parent=aresta,
        )
        geometria = ET.SubElement(
            celula, "mxGeometry", x="0", relative="1", **{"as": "geometry"}
        )
        ET.SubElement(
            geometria, "mxPoint", x="0", y="-12", **{"as": "offset"}
        )

    # ---------------------------------------------------------------------- SVG

    def _rota(self, aresta: Aresta) -> list[tuple[float, float]]:
        mapa = self.mapa()
        origem = mapa[aresta.origem]
        destino = mapa[aresta.destino]
        return [
            origem.ponto(*aresta.saida),
            *[(float(x), float(y)) for x, y in aresta.pontos],
            destino.ponto(*aresta.entrada),
        ]

    def _svg(self) -> str:
        partes = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.largura}" '
            f'height="{self.altura}" viewBox="0 0 {self.largura} {self.altura}" '
            'font-family="Segoe UI, Arial, sans-serif">',
            "<defs>",
            '<marker id="tri" markerWidth="12" markerHeight="12" refX="11" refY="6" '
            'orient="auto" markerUnits="userSpaceOnUse">'
            '<path d="M0,0 L12,6 L0,12 z" fill="#ffffff" stroke="#333" '
            'stroke-width="1"/></marker>',
            '<marker id="seta" markerWidth="12" markerHeight="12" refX="11" refY="6" '
            'orient="auto" markerUnits="userSpaceOnUse">'
            '<path d="M0,1 L11,6 L0,11" fill="none" stroke="#333" '
            'stroke-width="1.2"/></marker>',
            '<marker id="losango-cheio" markerWidth="14" markerHeight="12" refX="1" '
            'refY="6" orient="auto" markerUnits="userSpaceOnUse">'
            '<path d="M1,6 L7,1 L13,6 L7,11 z" fill="#333" stroke="#333"/></marker>',
            '<marker id="losango-vazio" markerWidth="14" markerHeight="12" refX="1" '
            'refY="6" orient="auto" markerUnits="userSpaceOnUse">'
            '<path d="M1,6 L7,1 L13,6 L7,11 z" fill="#ffffff" stroke="#333"/></marker>',
            "</defs>",
            '<rect width="100%" height="100%" fill="#ffffff"/>',
            f'<text x="60" y="22" font-size="18" font-weight="bold" fill="#111">'
            f"{escape(self.titulo)}</text>",
        ]
        for no in self._ordenados():
            partes.append(self._svg_no(no))
        for aresta in self.arestas:
            partes.append(self._svg_aresta(aresta))
        partes.append("</svg>")
        return "\n".join(partes)

    def _svg_no(self, no: No) -> str:
        if no.forma == "elipse":
            return self._svg_elipse(no)
        if no.forma == "ator":
            return self._svg_ator(no)
        if no.forma == "nota":
            return self._svg_nota(no)
        if no.forma == "texto":
            return self._svg_texto_livre(no)
        return self._svg_retangulo(no)

    def _svg_retangulo(self, no: No) -> str:
        tracejado = ' stroke-dasharray="6 4"' if no.tracejado else ""
        partes = [
            f'<rect x="{no.x}" y="{no.y}" width="{no.largura}" height="{no.altura}" '
            f'rx="2" fill="{no.fundo}" stroke="{no.contorno}"{tracejado}/>',
        ]
        partes.append(self._svg_linhas(no))
        return f"<g>{''.join(partes)}</g>"

    def _svg_elipse(self, no: No) -> str:
        cx = no.x + no.largura / 2
        cy = no.y + no.altura / 2
        partes = [
            f'<ellipse cx="{cx}" cy="{cy}" rx="{no.largura / 2}" '
            f'ry="{no.altura / 2}" fill="{no.fundo}" stroke="{no.contorno}"/>',
        ]
        partes.append(self._svg_linhas(no))
        return f"<g>{''.join(partes)}</g>"

    def _svg_ator(self, no: No) -> str:
        cx = no.x + no.largura / 2
        topo = no.y
        partes = [
            f'<circle cx="{cx}" cy="{topo + 11}" r="9" fill="none" '
            f'stroke="{no.contorno}" stroke-width="1.4"/>',
            f'<line x1="{cx}" y1="{topo + 20}" x2="{cx}" y2="{topo + 52}" '
            f'stroke="{no.contorno}" stroke-width="1.4"/>',
            f'<line x1="{cx - 17}" y1="{topo + 30}" x2="{cx + 17}" '
            f'y2="{topo + 30}" stroke="{no.contorno}" stroke-width="1.4"/>',
            f'<line x1="{cx}" y1="{topo + 52}" x2="{cx - 15}" y2="{topo + 76}" '
            f'stroke="{no.contorno}" stroke-width="1.4"/>',
            f'<line x1="{cx}" y1="{topo + 52}" x2="{cx + 15}" y2="{topo + 76}" '
            f'stroke="{no.contorno}" stroke-width="1.4"/>',
            f'<text x="{cx}" y="{topo + 94}" text-anchor="middle" font-size="11" '
            f'font-weight="bold" fill="#111">{escape(no.linhas[0])}</text>',
        ]
        return f"<g>{''.join(partes)}</g>"

    def _svg_nota(self, no: No) -> str:
        dobra = 14
        partes = [
            f'<path d="M{no.x},{no.y} h{no.largura - dobra} l{dobra},{dobra} '
            f'v{no.altura - dobra} h-{no.largura} z" fill="{no.fundo}" '
            f'stroke="{no.contorno}" stroke-width="1"/>',
        ]
        partes.append(self._svg_linhas(no))
        return f"<g>{''.join(partes)}</g>"

    def _svg_texto_livre(self, no: No) -> str:
        return f"<g>{self._svg_linhas(no)}</g>"

    def _svg_linhas(self, no: No) -> str:
        if not no.linhas:
            return ""
        altura_linha = no.fonte * 1.3
        total = altura_linha * len(no.linhas)
        if no.valign == "top":
            base = no.y + 13
        else:
            base = no.y + (no.altura - total) / 2 + altura_linha * 0.78
        if no.alinhamento == "left":
            x = no.x + 10
            ancora = "start"
        else:
            x = no.x + no.largura / 2
            ancora = "middle"
        peso = ' font-weight="bold"' if no.negrito else ""
        partes = []
        for indice, linha in enumerate(no.linhas):
            negrito = no.negrito or (no.destaque_primeira and indice == 0)
            peso_linha = ' font-weight="bold"' if negrito else peso
            partes.append(
                f'<text x="{x:.1f}" y="{base + indice * altura_linha:.1f}" '
                f'text-anchor="{ancora}" font-size="{no.fonte}"{peso_linha} '
                f'fill="#111">{escape(linha)}</text>'
            )
        return "".join(partes)

    def _svg_aresta(self, aresta: Aresta) -> str:
        rota = self._rota(aresta)
        pontos = " ".join(f"{x:.1f},{y:.1f}" for x, y in rota)
        marcador = {
            "heranca": 'marker-end="url(#tri)"',
            "realizacao": 'marker-end="url(#tri)"',
            "dependencia": 'marker-end="url(#seta)"',
            "usa": 'marker-end="url(#seta)"',
            "fluxo": 'marker-end="url(#seta)"',
            "composicao": 'marker-start="url(#losango-cheio)"',
            "agregacao": 'marker-start="url(#losango-vazio)"',
        }.get(aresta.tipo, "")
        tracejado = (
            ' stroke-dasharray="6 4"'
            if aresta.tipo in ("realizacao", "dependencia")
            else ""
        )
        partes = [
            f'<polyline points="{pontos}" fill="none" stroke="{aresta.cor}" '
            f'stroke-width="{aresta.largura}"{tracejado} {marcador}/>'
        ]

        if aresta.rotulo:
            total = _comprimento(rota)
            mx, my = _ponto_na_rota(rota, total / 2)
            largura = 6.2 * len(aresta.rotulo) + 8
            partes.append(
                f'<rect x="{mx - largura / 2:.1f}" y="{my - 8:.1f}" '
                f'width="{largura:.1f}" height="14" fill="#ffffff" opacity="0.92"/>'
                f'<text x="{mx:.1f}" y="{my + 3:.1f}" text-anchor="middle" '
                f'font-size="9" fill="#555">{escape(aresta.rotulo)}</text>'
            )
        return f"<g>{''.join(partes)}</g>"


def _linhas(valor: str | tuple[str, ...]) -> tuple[str, ...]:
    return (valor,) if isinstance(valor, str) else tuple(valor)


def _sobrepoe(a: No, b: No, margem: int = 4) -> bool:
    return not (
        a.x + a.largura + margem <= b.x
        or b.x + b.largura + margem <= a.x
        or a.y + a.altura + margem <= b.y
        or b.y + b.altura + margem <= a.y
    )


def _dentro(no: No, x: float, y: float, folga: int = 3) -> bool:
    return (
        no.x + folga < x < no.x + no.largura - folga
        and no.y + folga < y < no.y + no.altura - folga
    )


def _amostrar(rota: list[tuple[float, float]]) -> list[tuple[float, float]]:
    amostras: list[tuple[float, float]] = []
    for (x1, y1), (x2, y2) in zip(rota, rota[1:]):
        passos = max(int(abs(x2 - x1) + abs(y2 - y1)) // 4, 1)
        for passo in range(passos + 1):
            fator = passo / passos
            amostras.append((x1 + (x2 - x1) * fator, y1 + (y2 - y1) * fator))
    return amostras


def _comprimento(rota: list[tuple[float, float]]) -> float:
    total = 0.0
    for (x1, y1), (x2, y2) in zip(rota, rota[1:]):
        total += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return total


def _ponto_na_rota(
    rota: list[tuple[float, float]], distancia: float
) -> tuple[float, float]:
    restante = distancia
    for (x1, y1), (x2, y2) in zip(rota, rota[1:]):
        trecho = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if restante <= trecho or trecho == 0:
            fator = 0.0 if trecho == 0 else restante / trecho
            return (x1 + (x2 - x1) * fator, y1 + (y2 - y1) * fator)
        restante -= trecho
    return rota[-1]
