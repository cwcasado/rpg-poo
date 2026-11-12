"""Diagrama de visão de projeto: camadas, responsabilidades e acoplamento.

Fonte: ``docs/visao-de-projeto.md`` §2 (arquitetura) e §7 (ADRs).
"""

from __future__ import annotations

from pathlib import Path

from drawio_comum import AZUL, Diagrama, VERDE

ENTIDADES: tuple[tuple[str, str, int], ...] = (
    ("personagem.py", "ABC + 3 subclasses", 210),
    ("itens.py", "Item ABC + 3 subclasses", 430),
    ("grupo.py", "agregação 0..5", 650),
    ("cenario.py", "ABC + 3 cenários", 870),
    ("aldeao.py", "não-combatente", 1090),
)


def construir() -> Diagrama:
    """Monta o modelo do diagrama de visão de projeto."""
    diagrama = Diagrama(
        arquivo="diagrama-visao-de-projeto",
        id_diagrama="visao-de-projeto",
        nome="Visão de Projeto",
        largura=1400,
        altura=760,
        titulo="Visão de Projeto — Arquitetura em Camadas",
    )

    # Camada de apresentação -------------------------------------------------
    diagrama.faixa(
        "camada-apresentacao",
        "CAMADA DE APRESENTAÇÃO (console)",
        40,
        50,
        1320,
        130,
        fundo="#eaf2fb",
        contorno="#7ea6d8",
        tracejado=False,
    )
    diagrama.caixa(
        "cli",
        ("cli.py", "menu · input()/print()"),
        100,
        90,
        260,
        70,
        fundo=AZUL,
        destaque_primeira=True,
    )
    diagrama.caixa(
        "demo",
        ("demo.py", "roteiro fixo"),
        400,
        90,
        260,
        70,
        fundo=AZUL,
        destaque_primeira=True,
    )

    # Camada de domínio ------------------------------------------------------
    diagrama.faixa(
        "camada-dominio",
        "CAMADA DE DOMÍNIO (regras)",
        40,
        220,
        1320,
        460,
        fundo="#eef7ea",
        contorno="#8fbf7a",
        tracejado=False,
    )

    diagrama.texto("rot-orquestracao", "orquestração", 60, 255, 130, 24, negrito=True, fonte=9)
    diagrama.caixa(
        "combate",
        ("combate.py", "turnos · bônus · XP"),
        210,
        255,
        240,
        70,
        fundo=VERDE,
        destaque_primeira=True,
    )

    diagrama.texto("rot-entidades", "entidades", 60, 345, 130, 24, negrito=True, fonte=9)
    for nome, detalhe, x in ENTIDADES:
        diagrama.caixa(
            f"entidade-{nome.removesuffix('.py')}",
            (nome, detalhe),
            x,
            345,
            200,
            70,
            fundo=VERDE,
            destaque_primeira=True,
        )

    diagrama.texto("rot-composicao", "composição", 60, 435, 130, 24, negrito=True, fonte=9)
    diagrama.caixa(
        "ficha",
        ("ficha.py", "FichaDeStatus"),
        210,
        435,
        200,
        70,
        fundo=VERDE,
        destaque_primeira=True,
    )
    diagrama.caixa(
        "inventario",
        ("inventario.py", "Inventario"),
        430,
        435,
        200,
        70,
        fundo=VERDE,
        destaque_primeira=True,
    )

    diagrama.texto(
        "rot-contratos", "contratos e erros", 60, 525, 130, 40, negrito=True, fonte=9
    )
    diagrama.caixa(
        "interfaces",
        ("interfaces.py", "Combatente (interface)"),
        210,
        525,
        200,
        70,
        fundo=VERDE,
        destaque_primeira=True,
    )
    diagrama.caixa(
        "excecoes",
        ("excecoes.py", "10 erros de domínio"),
        430,
        525,
        200,
        70,
        fundo=VERDE,
        destaque_primeira=True,
    )

    # Notas de projeto -------------------------------------------------------
    diagrama.nota(
        "nota-acoplamento",
        (
            "Regra de dependência",
            "A apresentação conhece o domínio;",
            "o domínio nunca importa a apresentação.",
        ),
        700,
        265,
        600,
        70,
    )
    diagrama.nota(
        "nota-restricoes",
        (
            "Restrições do enunciado",
            "Python 3.10+ puro, sem dependências externas.",
            "Sem API/HTTP, sem banco, sem HTML/GUI.",
        ),
        700,
        435,
        600,
        70,
    )
    diagrama.nota(
        "nota-adr",
        (
            "ADR-02 — um arquivo por conceito",
            "O diagrama espelha a árvore de arquivos;",
            "cada conceito é localizável e testável.",
        ),
        700,
        535,
        600,
        70,
    )

    # Dependências -----------------------------------------------------------
    diagrama.conectar(
        "usa-cli-combate",
        "cli",
        "combate",
        "usa",
        saida=(0.5, 1.0),
        entrada=(0.5, 0.0),
        pontos=((230, 205), (330, 205)),
        rotulo="usa",
    )
    diagrama.conectar(
        "usa-demo-dominio",
        "demo",
        "camada-dominio",
        "usa",
        saida=(0.5, 1.0),
        entrada=(0.35, 0.0),
        pontos=((530, 190), (502, 190)),
        rotulo="usa",
    )
    diagrama.conectar(
        "usa-combate-entidades",
        "combate",
        "entidade-personagem",
        "usa",
        saida=(0.5, 1.0),
        entrada=(0.6, 0.0),
        rotulo="usa",
    )
    diagrama.conectar(
        "consome-combate-contratos",
        "combate",
        "interfaces",
        "dependencia",
        saida=(0.0, 0.5),
        entrada=(0.0, 0.5),
        pontos=((195, 290), (195, 560)),
        rotulo="consome",
    )
    diagrama.conectar(
        "compoe-personagem-ficha",
        "entidade-personagem",
        "ficha",
        "composicao",
        saida=(0.25, 1.0),
        entrada=(0.25, 0.0),
        rotulo="compõe",
    )
    diagrama.conectar(
        "compoe-personagem-inventario",
        "entidade-personagem",
        "inventario",
        "composicao",
        saida=(0.75, 1.0),
        entrada=(0.5, 0.0),
        pontos=((360, 425), (530, 425)),
        rotulo="compõe",
    )

    return diagrama


def gerar() -> tuple[Path, Path]:
    """Gera os arquivos ``.drawio`` e ``.svg`` a partir do modelo."""
    return construir().gerar()
