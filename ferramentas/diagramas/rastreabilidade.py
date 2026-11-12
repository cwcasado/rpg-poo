"""Diagrama de rastreabilidade: exigência → arquivo → teste que prova.

Fonte: ``docs/rastreabilidade.md`` §1 (exigências de ``regras.md``).
Cada linha é uma exigência; as setas mostram o caminho da prova.
"""

from __future__ import annotations

from pathlib import Path

from drawio_comum import AMARELO, AZUL, Diagrama, VERDE

LINHAS: tuple[tuple[str, str, str], ...] = (
    (
        "1. Classes e objetos",
        "personagem.py · itens.py · cenario.py",
        "test_personagem.py::test_guerreiro_ataca_com_forca_dobrada",
    ),
    (
        "2. Atributos, métodos e interação",
        "personagem.py\n(atacar · receber_dano · usar_item)",
        "test_personagem.py::test_atacar_interage_com_receber_dano",
    ),
    (
        "3. Abstração (ABC)",
        "personagem.py · itens.py · cenario.py",
        "test_personagem.py::test_personagem_abstrata_nao_pode_ser_instanciada",
    ),
    (
        "4. Interface Combatente",
        "interfaces.py · personagem.py",
        "test_combate.py::test_combate_rejeita_nao_combatente",
    ),
    (
        "5. Herança",
        "personagem.py\n(Guerreiro/Mago/Arqueiro)",
        "test_personagem.py::test_subclasses_sao_personagens",
    ),
    (
        "6. Exceções",
        "excecoes.py + raise no domínio",
        "test_excecoes.py (4 testes)",
    ),
    (
        "7. Agregação",
        "grupo.py",
        "test_grupo.py::test_personagem_sobrevive_ao_grupo",
    ),
    (
        "8. Composição",
        "ficha.py · inventario.py · personagem.py",
        "test_personagem.py::test_personagem_cria_ficha_e_inventario",
    ),
    (
        "9. Consumo de classe",
        "combate.py",
        "test_combate.py::test_combate_aplica_bonus_do_cenario",
    ),
    (
        "10. Ambiente favorecido",
        "cenario.py",
        "test_cenario.py (12 testes)",
    ),
    (
        "11. Sem back-end / front-end",
        "cli.py · demo.py (só input/print)",
        "test_cli.py",
    ),
)

COLUNAS = (
    ("Conceito (regras.md)", 40, 300, AZUL),
    ("Onde está no código", 380, 340, VERDE),
    ("Teste que prova", 760, 600, AMARELO),
)


def construir() -> Diagrama:
    """Monta o modelo do diagrama de rastreabilidade."""
    diagrama = Diagrama(
        arquivo="diagrama-rastreabilidade",
        id_diagrama="rastreabilidade",
        nome="Rastreabilidade",
        largura=1400,
        altura=930,
        titulo="Rastreabilidade — conceito · código · teste",
    )

    for indice, (rotulo, x, largura, cor) in enumerate(COLUNAS, start=1):
        diagrama.caixa(
            f"cabecalho-{indice}",
            rotulo,
            x,
            64,
            largura,
            40,
            fundo=cor,
            negrito=True,
            fonte=11,
        )

    for indice, (conceito, codigo, teste) in enumerate(LINHAS):
        y = 116 + indice * 66
        diagrama.caixa(
            f"conceito-{indice + 1}",
            conceito,
            40,
            y,
            300,
            46,
            fundo=AZUL,
        )
        diagrama.caixa(
            f"codigo-{indice + 1}",
            codigo.split("\n"),
            380,
            y,
            340,
            46,
            fundo=VERDE,
        )
        diagrama.caixa(
            f"teste-{indice + 1}",
            teste,
            760,
            y,
            600,
            46,
            fundo=AMARELO,
        )
        diagrama.conectar(
            f"prova-codigo-{indice + 1}",
            f"conceito-{indice + 1}",
            f"codigo-{indice + 1}",
            "fluxo",
            saida=(1.0, 0.5),
            entrada=(0.0, 0.5),
            cor="#888888",
            largura=1.0,
        )
        diagrama.conectar(
            f"prova-teste-{indice + 1}",
            f"codigo-{indice + 1}",
            f"teste-{indice + 1}",
            "fluxo",
            saida=(1.0, 0.5),
            entrada=(0.0, 0.5),
            cor="#888888",
            largura=1.0,
        )

    diagrama.nota(
        "nota-como-provar",
        (
            "Como provar",
            "python -m unittest discover -s testes   ·   python demo.py",
        ),
        40,
        850,
        760,
        50,
    )

    return diagrama


def gerar() -> tuple[Path, Path]:
    """Gera os arquivos ``.drawio`` e ``.svg`` a partir do modelo."""
    return construir().gerar()
