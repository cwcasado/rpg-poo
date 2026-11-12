"""Testes de FichaDeStatus e Inventario — as duas composições do personagem (Aula 07)."""

import unittest

from rpg.excecoes import ItemNaoEncontradoError, ValorInvalidoError
from rpg.ficha import FichaDeStatus
from rpg.inventario import Inventario
from rpg.itens import Arma, Pocao


class TestFichaDeStatus(unittest.TestCase):
    """Progressão de nível e experiência."""

    def test_ficha_inicia_nivel_um(self) -> None:
        # Arrange / Act
        ficha = FichaDeStatus()

        # Assert
        self.assertEqual(ficha.nivel, 1)
        self.assertEqual(ficha.xp, 0)

    def test_ganhar_xp_sobe_de_nivel(self) -> None:
        # Arrange
        ficha = FichaDeStatus()

        # Act
        nivel = ficha.ganhar_xp(100)

        # Assert
        self.assertEqual(nivel, 2)
        self.assertEqual(ficha.nivel, 2)
        self.assertEqual(ficha.xp, 0)

    def test_ganhar_xp_acumula_resto(self) -> None:
        # Arrange
        ficha = FichaDeStatus()

        # Act
        ficha.ganhar_xp(150)

        # Assert
        self.assertEqual(ficha.nivel, 2)
        self.assertEqual(ficha.xp, 50)

    def test_ganhar_muito_xp_sobe_varios_niveis(self) -> None:
        # Arrange
        ficha = FichaDeStatus()

        # Act
        nivel = ficha.ganhar_xp(350)

        # Assert
        self.assertEqual(nivel, 4)
        self.assertEqual(ficha.xp, 50)

    def test_xp_negativo_lanca_excecao(self) -> None:
        # Arrange
        ficha = FichaDeStatus()

        # Act / Assert
        with self.assertRaises(ValorInvalidoError):
            ficha.ganhar_xp(-10)

    def test_xp_zero_lanca_excecao(self) -> None:
        # Arrange
        ficha = FichaDeStatus()

        # Act / Assert
        with self.assertRaises(ValorInvalidoError):
            ficha.ganhar_xp(0)

    def test_resumo_mostra_nivel_e_xp(self) -> None:
        # Arrange
        ficha = FichaDeStatus()

        # Act
        resumo = ficha.resumo()

        # Assert
        self.assertIn("nível 1", resumo)
        self.assertIn("0/100", resumo)


class TestInventario(unittest.TestCase):
    """Coleção de itens: adicionar, buscar, remover, listar."""

    def test_inventario_comeca_vazio(self) -> None:
        # Arrange / Act
        inventario = Inventario()

        # Assert
        self.assertTrue(inventario.vazio())
        self.assertEqual(len(inventario), 0)

    def test_inventario_adiciona_e_busca(self) -> None:
        # Arrange
        inventario = Inventario()
        pocao = Pocao("Poção de Vida", 30)

        # Act
        inventario.adicionar(pocao)
        encontrado = inventario.buscar("Poção de Vida")

        # Assert
        self.assertIs(encontrado, pocao)
        self.assertEqual(len(inventario), 1)

    def test_inventario_busca_sem_diferenciar_maiusculas(self) -> None:
        # Arrange
        inventario = Inventario()
        inventario.adicionar(Arma("Espada Longa", 5))

        # Act
        encontrado = inventario.buscar("espada longa")

        # Assert
        self.assertEqual(encontrado.nome, "Espada Longa")

    def test_inventario_remove(self) -> None:
        # Arrange
        inventario = Inventario()
        inventario.adicionar(Pocao("Poção", 10))

        # Act
        removido = inventario.remover("Poção")

        # Assert
        self.assertEqual(removido.nome, "Poção")
        self.assertTrue(inventario.vazio())

    def test_inventario_busca_inexistente(self) -> None:
        # Arrange
        inventario = Inventario()

        # Act / Assert
        with self.assertRaises(ItemNaoEncontradoError):
            inventario.buscar("Machado")

    def test_inventario_remove_inexistente(self) -> None:
        # Arrange
        inventario = Inventario()

        # Act / Assert
        with self.assertRaises(ItemNaoEncontradoError):
            inventario.remover("Machado")

    def test_inventario_rejeita_objeto_que_nao_e_item(self) -> None:
        # Arrange
        inventario = Inventario()

        # Act / Assert
        with self.assertRaises(ValorInvalidoError):
            inventario.adicionar("espada")  # type: ignore[arg-type]

    def test_inventario_lista_nomes(self) -> None:
        # Arrange
        inventario = Inventario()
        inventario.adicionar(Pocao("Poção", 10))
        inventario.adicionar(Arma("Adaga", 2))

        # Act
        nomes = inventario.nomes()

        # Assert
        self.assertEqual(nomes, ["Poção", "Adaga"])

    def test_listar_devolve_copia(self) -> None:
        # Arrange
        inventario = Inventario()
        inventario.adicionar(Pocao("Poção", 10))

        # Act
        lista = inventario.listar()
        lista.clear()

        # Assert
        self.assertEqual(len(inventario), 1)


if __name__ == "__main__":
    unittest.main()
