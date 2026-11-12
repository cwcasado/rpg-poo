"""Diagrama de casos de uso: ator Jogador, ator Sistema e os 8 casos (UC01–UC08).

Fonte: ``docs/caso-de-uso.md`` §2 (atores) e §3 (visão geral).
"""

from __future__ import annotations

from pathlib import Path

from drawio_comum import AZUL, Diagrama

CASOS: tuple[tuple[str, str], ...] = (
    ("UC01", "Criar personagem"),
    ("UC02", "Consultar ficha"),
    ("UC03", "Gerenciar inventário"),
    ("UC04", "Usar item"),
    ("UC05", "Montar grupo"),
    ("UC06", "Escolher cenário"),
    ("UC07", "Iniciar combate"),
    ("UC08", "Conversar com aldeão"),
)

# Casos em que o Sistema executa regras de domínio (ator secundário).
CASOS_DO_SISTEMA = (4, 6, 7)


def construir() -> Diagrama:
    """Monta o modelo do diagrama de casos de uso."""
    diagrama = Diagrama(
        arquivo="diagrama-casos-de-uso",
        id_diagrama="casos-de-uso",
        nome="Casos de Uso",
        largura=1450,
        altura=900,
        titulo="Casos de Uso — Sistema de RPG",
    )

    diagrama.faixa(
        "sistema",
        "Sistema de RPG (console)",
        440,
        50,
        560,
        700,
        fundo="#fbfbfb",
        contorno="#555555",
        tracejado=False,
    )
    diagrama.ator("jogador", "Jogador", 110, 330)
    diagrama.ator("sistema-ator", "Sistema", 1080, 330)

    for indice, (codigo, nome) in enumerate(CASOS, start=1):
        y = 100 + (indice - 1) * 76
        diagrama.elipse(
            f"uc{indice}",
            f"{codigo} · {nome}",
            480,
            y,
            480,
            62,
            fundo=AZUL,
            fonte=11,
        )
        diagrama.conectar(
            f"associa-jogador-{indice}",
            "jogador",
            f"uc{indice}",
            "associacao",
            saida=(1.0, 0.5),
            entrada=(0.0, 0.5),
        )

    for indice in CASOS_DO_SISTEMA:
        diagrama.conectar(
            f"associa-sistema-{indice}",
            "sistema-ator",
            f"uc{indice}",
            "associacao",
            saida=(0.0, 0.5),
            entrada=(1.0, 0.5),
        )

    diagrama.nota(
        "nota-rn06",
        (
            "RN06 — ambiente favorece o tipo",
            "Floresta → Arqueiro · Caverna → Guerreiro",
            "Castelo → Mago · +20% no ataque",
        ),
        120,
        790,
        520,
        80,
    )
    diagrama.nota(
        "nota-rn02",
        (
            "UC08 — o aldeão não é combatente",
            "Aldeao não realiza Combatente; o Combate",
            "recusa com AlvoInvalidoError.",
        ),
        700,
        790,
        520,
        80,
    )

    return diagrama


def gerar() -> tuple[Path, Path]:
    """Gera os arquivos ``.drawio`` e ``.svg`` a partir do modelo."""
    return construir().gerar()
