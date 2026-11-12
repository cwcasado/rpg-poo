"""Testes de Item, Pocao, Arma e Armadura — abstração e polimorfismo (Aulas 05 e 08).

Os testes usam um dublê (``PersonagemDuble``) que cumpre a parte da API de
``Personagem`` que os itens consomem — exemplo prático de duck typing (Aula 06).
"""

import unittest

from rpg.excecoes import ValorInvalidoError
from rpg.itens import Arma, Armadura, Item, Pocao


class PersonagemDuble:
    """Dublê de personagem para testar itens sem acoplar à hierarquia real."""

    def __init__(self, nome: str = "Dublê", vida: int = 50, vida_maxima: int = 100) -> None:
        self.nome = nome
        self.vida = vida
        self.vida_maxima = vida_maxima
        self.bonus_ataque = 0
        self.bonus_defesa = 0

    def curar(self, valor: int) -> int:
        recuperado = min(valor, self.vida_maxima - self.vida)
        self.vida += recuperado
        return recuperado

    def receber_bonus_ataque(self, valor: int) -> None:
        self.bonus_ataque += valor

    def receber_bonus_defesa(self, valor: int) -> None:
        self.bonus_defesa += valor


class TestAbstracaoDeItem(unittest.TestCase):
    """Item é abstrata: só subclasses concretas existem."""

    def test_item_abstrato_nao_pode_ser_instanciado(self) -> None:
        with self.assertRaises(TypeError):
            Item("Item genérico")  # type: ignore[abstract]

    def test_item_sem_nome_lanca_excecao(self) -> None:
        with self.assertRaises(ValorInvalidoError):
            Pocao("   ", 10)


class TestPocao(unittest.TestCase):
    """Poção cura e é consumível."""

    def test_pocao_cura_personagem(self) -> None:
        # Arrange
        personagem = PersonagemDuble(vida=40, vida_maxima=100)
        pocao = Pocao("Poção de Vida", 30)

        # Act
        mensagem = pocao.usar(personagem)

        # Assert
        self.assertEqual(personagem.vida, 70)
        self.assertIn("30", mensagem)
        self.assertIn("Poção de Vida", mensagem)

    def test_pocao_nao_ultrapassa_vida_maxima(self) -> None:
        # Arrange
        personagem = PersonagemDuble(vida=90, vida_maxima=100)
        pocao = Pocao("Poção Grande", 50)

        # Act
        pocao.usar(personagem)

        # Assert
        self.assertEqual(personagem.vida, 100)

    def test_pocao_e_consumivel(self) -> None:
        self.assertTrue(Pocao("Poção", 10).consumivel)

    def test_pocao_com_cura_invalida_lanca_excecao(self) -> None:
        with self.assertRaises(ValorInvalidoError):
            Pocao("Poção Quebrada", 0)

    def test_pocao_com_cura_negativa_lanca_excecao(self) -> None:
        with self.assertRaises(ValorInvalidoError):
            Pocao("Poção Venenosa", -5)


class TestArma(unittest.TestCase):
    """Arma soma bônus de ataque e permanece equipada."""

    def test_arma_aumenta_bonus_ataque(self) -> None:
        # Arrange
        personagem = PersonagemDuble()
        arma = Arma("Espada Longa", 7)

        # Act
        mensagem = arma.usar(personagem)

        # Assert
        self.assertEqual(personagem.bonus_ataque, 7)
        self.assertIn("+7", mensagem)

    def test_arma_nao_e_consumivel(self) -> None:
        self.assertFalse(Arma("Adaga", 2).consumivel)

    def test_arma_com_bonus_negativo_lanca_excecao(self) -> None:
        with self.assertRaises(ValorInvalidoError):
            Arma("Arma Amaldiçoada", -1)


class TestArmadura(unittest.TestCase):
    """Armadura soma bônus de defesa e permanece equipada."""

    def test_armadura_aumenta_bonus_defesa(self) -> None:
        # Arrange
        personagem = PersonagemDuble()
        armadura = Armadura("Cota de Malha", 6)

        # Act
        mensagem = armadura.usar(personagem)

        # Assert
        self.assertEqual(personagem.bonus_defesa, 6)
        self.assertIn("+6", mensagem)

    def test_armadura_com_bonus_negativo_lanca_excecao(self) -> None:
        with self.assertRaises(ValorInvalidoError):
            Armadura("Armadura Quebrada", -3)


class TestPolimorfismoDeUso(unittest.TestCase):
    """A mesma chamada ``item.usar`` produz efeitos diferentes por subtipo."""

    def test_usar_itens_diferentes_muda_estado_diferente(self) -> None:
        # Arrange
        personagem = PersonagemDuble(vida=50, vida_maxima=100)
        itens = [Pocao("Poção", 20), Arma("Espada", 5), Armadura("Escudo", 4)]

        # Act
        for item in itens:
            item.usar(personagem)

        # Assert
        self.assertEqual(personagem.vida, 70)
        self.assertEqual(personagem.bonus_ataque, 5)
        self.assertEqual(personagem.bonus_defesa, 4)


if __name__ == "__main__":
    unittest.main()
