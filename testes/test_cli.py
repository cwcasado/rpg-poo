"""Testes do menu de console — fluxo de telas sem teclado real.

As funções de entrada e saída são injetadas, então o teste é determinístico.
"""

import unittest

from rpg.cli import CLI
from rpg.personagem import Guerreiro, Mago


def rodar_cli(entradas: list[str]) -> tuple[CLI, list[str]]:
    """Executa a CLI com uma fila de respostas e captura a saída."""
    fila = iter(entradas)
    saida: list[str] = []

    def entrada(_prompt: str = "") -> str:
        return next(fila)

    cli = CLI(input_fn=entrada, print_fn=lambda msg="": saida.append(str(msg)))
    cli.executar()
    return cli, saida


class TestFluxoBasico(unittest.TestCase):
    """Menu, saída e opção inválida."""

    def test_cli_sai(self) -> None:
        # Act
        _, saida = rodar_cli(["0"])

        # Assert
        self.assertIn("Até a próxima aventura!", saida[-1])

    def test_opcao_invalida_mostra_erro(self) -> None:
        # Act
        _, saida = rodar_cli(["x", "0"])

        # Assert
        self.assertTrue(any("[erro]" in linha for linha in saida))

    def test_listar_sem_personagens(self) -> None:
        # Act
        _, saida = rodar_cli(["2", "0"])

        # Assert
        self.assertIn("Nenhum personagem criado ainda.", saida)


class TestCriacaoDePersonagem(unittest.TestCase):
    """UC01 e UC02 pela CLI."""

    def test_criar_personagem_via_cli(self) -> None:
        # Act
        cli, saida = rodar_cli(["1", "1", "Aragorn", "0"])

        # Assert
        self.assertIn("Aragorn", cli.personagens)
        self.assertEqual(cli.personagens["Aragorn"].tipo, "Guerreiro")
        self.assertTrue(any("vida 120/120" in linha for linha in saida))

    def test_tipo_invalido_nao_cria_personagem(self) -> None:
        # Act
        cli, saida = rodar_cli(["1", "9", "0"])

        # Assert
        self.assertEqual(cli.personagens, {})
        self.assertTrue(any("inválido" in linha for linha in saida))

    def test_nome_duplicado_e_recusado(self) -> None:
        # Act
        cli, saida = rodar_cli(["1", "1", "Aragorn", "1", "2", "Aragorn", "0"])

        # Assert
        self.assertEqual(len(cli.personagens), 1)
        self.assertTrue(any("já existe" in linha for linha in saida))

    def test_ver_ficha(self) -> None:
        # Act
        _, saida = rodar_cli(["1", "2", "Gandalf", "3", "Gandalf", "0"])

        # Assert
        self.assertTrue(any("Mago" in linha and "nível 1" in linha for linha in saida))


class TestItens(unittest.TestCase):
    """UC03 e UC04 pela CLI."""

    def test_adicionar_e_usar_pocao(self) -> None:
        # Act
        cli, saida = rodar_cli(
            ["1", "1", "Aragorn", "4", "Aragorn", "1", "Poção de Vida", "30",
             "5", "Aragorn", "Poção de Vida", "0"]
        )

        # Assert
        guerreiro = cli.personagens["Aragorn"]
        self.assertTrue(guerreiro.inventario.vazio())
        self.assertTrue(any("Poção de Vida" in linha for linha in saida))

    def test_item_com_valor_invalido_mostra_erro(self) -> None:
        # Act
        _, saida = rodar_cli(
            ["1", "1", "Aragorn", "4", "Aragorn", "1", "Poção", "muito", "0"]
        )

        # Assert
        self.assertTrue(any("não é um número inteiro" in linha for linha in saida))


class TestGrupoECenario(unittest.TestCase):
    """UC05 e UC06 pela CLI."""

    def test_montar_grupo(self) -> None:
        # Act
        cli, _ = rodar_cli(
            ["1", "1", "Aragorn", "1", "3", "Legolas", "6", "Companhia", "1", "Aragorn", "0"]
        )

        # Assert
        self.assertIn("Companhia", cli.grupos)
        self.assertTrue(cli.grupos["Companhia"].contem("Aragorn"))

    def test_escolher_cenario(self) -> None:
        # Act
        cli, saida = rodar_cli(["7", "2", "0"])

        # Assert
        self.assertIsNotNone(cli.cenario)
        self.assertEqual(cli.cenario.nome, "Caverna")  # type: ignore[union-attr]
        self.assertTrue(any("Caverna" in linha for linha in saida))


class TestCombate(unittest.TestCase):
    """UC07 pela CLI, com log e XP."""

    def test_combate_completo(self) -> None:
        # Act
        cli, saida = rodar_cli(
            ["1", "1", "Aragorn", "1", "2", "Gandalf", "7", "2",
             "8", "Aragorn", "Gandalf", "n", "0"]
        )

        # Assert
        self.assertEqual(cli.personagens["Aragorn"].ficha.nivel, 2)
        self.assertTrue(any("venceu" in linha for linha in saida))
        self.assertTrue(any("Turno 1" in linha for linha in saida))

    def test_combate_sem_cenario_mostra_erro(self) -> None:
        # Act
        _, saida = rodar_cli(["1", "1", "Aragorn", "1", "2", "Gandalf", "8", "0"])

        # Assert
        self.assertTrue(any("cenário" in linha for linha in saida))

    def test_combate_com_pocao_antes_da_luta(self) -> None:
        # Act
        cli, _ = rodar_cli(
            ["1", "1", "Aragorn", "4", "Aragorn", "1", "Poção", "20",
             "1", "3", "Legolas", "7", "2", "8", "Aragorn", "Legolas", "s",
             "Poção", "0"]
        )

        # Assert
        self.assertTrue(cli.personagens["Aragorn"].inventario.vazio())


class TestAldeao(unittest.TestCase):
    """UC08 pela CLI."""

    def test_conversar_com_aldeao(self) -> None:
        # Act
        _, saida = rodar_cli(["9", "0"])

        # Assert
        self.assertTrue(any("Tobias" in linha for linha in saida))


if __name__ == "__main__":
    unittest.main()
