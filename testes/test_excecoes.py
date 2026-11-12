"""Testes da hierarquia de exceções do domínio (Aula 08).

Padrão AAA — Arrange, Act, Assert.
"""

import unittest

from rpg.excecoes import (
    AlvoInvalidoError,
    CenarioInvalidoError,
    CombateInfinitoError,
    DanoInvalidoError,
    GrupoCheioError,
    ItemNaoEncontradoError,
    PersonagemMortoError,
    RPGError,
    SemManaError,
    ValorInvalidoError,
    VidaInvalidaError,
)


class TestHierarquiaDeExcecoes(unittest.TestCase):
    """Toda exceção de domínio deve ser capturável como RPGError."""

    FILHAS = (
        ValorInvalidoError,
        VidaInvalidaError,
        DanoInvalidoError,
        ItemNaoEncontradoError,
        GrupoCheioError,
        AlvoInvalidoError,
        PersonagemMortoError,
        SemManaError,
        CenarioInvalidoError,
        CombateInfinitoError,
    )

    def test_todas_herdam_de_rpg_error(self) -> None:
        # Arrange
        for classe in self.FILHAS:
            with self.subTest(excecao=classe.__name__):
                # Act / Assert
                self.assertTrue(issubclass(classe, RPGError))

    def test_rpg_error_herda_de_exception(self) -> None:
        self.assertTrue(issubclass(RPGError, Exception))

    def test_mensagem_e_preservada(self) -> None:
        # Arrange / Act
        erro = DanoInvalidoError("dano deve ser positivo")

        # Assert
        self.assertEqual(str(erro), "dano deve ser positivo")

    def test_captura_generica_pega_erro_especifico(self) -> None:
        # Arrange
        capturado = None

        # Act
        try:
            raise ItemNaoEncontradoError("item ausente")
        except RPGError as erro:
            capturado = erro

        # Assert
        self.assertIsInstance(capturado, ItemNaoEncontradoError)


if __name__ == "__main__":
    unittest.main()
