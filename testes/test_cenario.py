"""Testes de Cenario — ambiente que favorece um tipo (Aula 04/Aula 06, RN06)."""

import unittest

from rpg.cenario import Castelo, Caverna, Cenario, Floresta, criar_cenario
from rpg.excecoes import AlvoInvalidoError, CenarioInvalidoError
from rpg.personagem import Arqueiro, Guerreiro, Mago


class TestAbstracaoDeCenario(unittest.TestCase):
    """Cenario é abstrata; só os concretos existem."""

    def test_cenario_abstrato_nao_pode_ser_instanciado(self) -> None:
        with self.assertRaises(TypeError):
            Cenario("Planície", Guerreiro)  # type: ignore[abstract]


class TestBonusPorTipo(unittest.TestCase):
    """RN06: +20% para o tipo favorecido, 0% para os demais."""

    def test_floresta_favorece_arqueiro(self) -> None:
        # Arrange
        floresta = Floresta()

        # Act / Assert
        self.assertEqual(floresta.bonus_para(Arqueiro("Legolas")), 0.20)

    def test_floresta_nao_favorece_guerreiro(self) -> None:
        self.assertEqual(Floresta().bonus_para(Guerreiro("Aragorn")), 0.0)

    def test_caverna_favorece_guerreiro(self) -> None:
        self.assertEqual(Caverna().bonus_para(Guerreiro("Aragorn")), 0.20)

    def test_caverna_nao_favorece_mago(self) -> None:
        self.assertEqual(Caverna().bonus_para(Mago("Gandalf")), 0.0)

    def test_castelo_favorece_mago(self) -> None:
        self.assertEqual(Castelo().bonus_para(Mago("Gandalf")), 0.20)

    def test_castelo_nao_favorece_arqueiro(self) -> None:
        self.assertEqual(Castelo().bonus_para(Arqueiro("Legolas")), 0.0)

    def test_bonus_para_alvo_invalido_lanca_excecao(self) -> None:
        with self.assertRaises(AlvoInvalidoError):
            Floresta().bonus_para("Legolas")  # type: ignore[arg-type]


class TestDescricaoECriacao(unittest.TestCase):
    """Cada cenário se descreve e pode ser criado por número ou nome."""

    def test_descricoes_mencionam_o_tipo_favorecido(self) -> None:
        self.assertIn("Arqueiros", Floresta().descricao())
        self.assertIn("Guerreiros", Caverna().descricao())
        self.assertIn("Magos", Castelo().descricao())

    def test_criar_cenario_por_numero(self) -> None:
        self.assertIsInstance(criar_cenario("1"), Floresta)
        self.assertIsInstance(criar_cenario("2"), Caverna)
        self.assertIsInstance(criar_cenario("3"), Castelo)

    def test_criar_cenario_por_nome_sem_diferenciar_caixa(self) -> None:
        self.assertIsInstance(criar_cenario("CaVeRnA"), Caverna)

    def test_criar_cenario_opcao_invalida(self) -> None:
        with self.assertRaises(CenarioInvalidoError):
            criar_cenario("deserto")


if __name__ == "__main__":
    unittest.main()
