"""Testes de Combate — interface, consumo de classe e exceções (Aulas 03, 06, 08)."""

import unittest

from rpg.aldeao import Aldeao
from rpg.cenario import Castelo, Caverna, Floresta
from rpg.combate import Combate, RegistroTurno
from rpg.excecoes import (
    AlvoInvalidoError,
    CenarioInvalidoError,
    CombateInfinitoError,
    ItemNaoEncontradoError,
    PersonagemMortoError,
    ValorInvalidoError,
)
from rpg.itens import Arma, Pocao
from rpg.personagem import Arqueiro, Guerreiro, Mago


class TestValidacaoDoCombate(unittest.TestCase):
    """Só entra quem cumpre o contrato e está vivo (Aula 06)."""

    def test_combate_rejeita_nao_combatente(self) -> None:
        # Arrange
        aldeao = Aldeao("Tobias")
        guerreiro = Guerreiro("Aragorn")

        # Act / Assert
        with self.assertRaises(AlvoInvalidoError):
            Combate(aldeao, guerreiro, Caverna())  # type: ignore[arg-type]

    def test_combate_rejeita_morto(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")
        mago = Mago("Gandalf")
        mago.receber_dano(9999)

        # Act / Assert
        with self.assertRaises(PersonagemMortoError):
            Combate(guerreiro, mago, Caverna())

    def test_combate_rejeita_personagem_contra_si_mesmo(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")

        # Act / Assert
        with self.assertRaises(AlvoInvalidoError):
            Combate(guerreiro, guerreiro, Caverna())

    def test_combate_rejeita_cenario_invalido(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")
        mago = Mago("Gandalf")

        # Act / Assert
        with self.assertRaises(CenarioInvalidoError):
            Combate(guerreiro, mago, "caverna")  # type: ignore[arg-type]

    def test_executar_max_turnos_invalido(self) -> None:
        # Arrange
        combate = Combate(Guerreiro("Aragorn"), Mago("Gandalf"), Caverna())

        # Act / Assert
        with self.assertRaises(ValorInvalidoError):
            combate.executar(max_turnos=0)


class TestBonusDoCenario(unittest.TestCase):
    """O cenário consome Personagem e o Combate aplica o bônus (RN06)."""

    def test_combate_aplica_bonus_do_cenario(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")
        alvo = Guerreiro("Boromir")
        combate = Combate(guerreiro, alvo, Caverna())  # Caverna favorece Guerreiro

        # Act
        registro = combate.executar_turno(guerreiro, alvo)

        # Assert
        self.assertEqual(registro.poder, 36)
        self.assertEqual(registro.bonus, 0.20)
        self.assertEqual(registro.dano, 31)  # round(36 * 1.2) = 43; 43 - 12

    def test_combate_sem_bonus_para_tipo_nao_favorecido(self) -> None:
        # Arrange
        mago = Mago("Gandalf")
        alvo = Guerreiro("Aragorn")
        combate = Combate(mago, alvo, Caverna())  # Caverna não favorece Mago

        # Act
        registro = combate.executar_turno(mago, alvo)

        # Assert
        self.assertEqual(registro.poder, 34)
        self.assertEqual(registro.bonus, 0.0)
        self.assertEqual(registro.dano, 22)  # 34 - 12

    def test_floresta_favorece_arqueiro_no_dano(self) -> None:
        # Arrange
        arqueiro = Arqueiro("Legolas")
        alvo = Guerreiro("Aragorn")
        combate = Combate(arqueiro, alvo, Floresta())

        # Act
        registro = combate.executar_turno(arqueiro, alvo)

        # Assert
        self.assertEqual(registro.poder, 21)
        self.assertEqual(registro.dano, 13)  # round(21 * 1.2) = 25; 25 - 12


class TestResolucaoDoCombate(unittest.TestCase):
    """Turnos alternados, morte, XP e log."""

    def test_combate_termina_com_vencedor(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")
        arqueiro = Arqueiro("Legolas")
        combate = Combate(guerreiro, arqueiro, Caverna())

        # Act
        resultado = combate.executar()

        # Assert
        self.assertIs(resultado.vencedor, guerreiro)
        self.assertIs(resultado.perdedor, arqueiro)
        self.assertEqual(resultado.turnos, 5)  # 3 golpes do guerreiro, 2 do arqueiro
        self.assertIn("Aragorn", resultado.resumo())
        self.assertIn("Caverna", resultado.resumo())

    def test_combate_nao_deixa_vida_negativa(self) -> None:
        # Arrange
        combate = Combate(Guerreiro("Aragorn"), Arqueiro("Legolas"), Caverna())

        # Act
        resultado = combate.executar()

        # Assert
        self.assertEqual(resultado.perdedor.vida, 0)
        self.assertFalse(resultado.perdedor.esta_vivo())

    def test_vencedor_recebe_xp(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")
        combate = Combate(guerreiro, Arqueiro("Legolas"), Caverna())

        # Act
        combate.executar()

        # Assert
        self.assertEqual(guerreiro.ficha.nivel, 2)
        self.assertEqual(guerreiro.ficha.xp, 0)

    def test_log_registra_todos_os_turnos(self) -> None:
        # Arrange
        combate = Combate(Guerreiro("Aragorn"), Arqueiro("Legolas"), Caverna())

        # Act
        resultado = combate.executar()

        # Assert
        self.assertEqual(len(resultado.log), 5)
        self.assertIsInstance(resultado.log[0], RegistroTurno)
        self.assertIn("Turno 1", resultado.log[0].descricao())

    def test_combate_infinito_lanca_excecao(self) -> None:
        # Arrange
        combate = Combate(Guerreiro("Aragorn"), Guerreiro("Boromir"), Caverna())

        # Act / Assert
        with self.assertRaises(CombateInfinitoError):
            combate.executar(max_turnos=1)

    def test_castelo_aumenta_o_dano_do_mago(self) -> None:
        """O bônus do Castelo vale no dano, mesmo quando não decide a luta."""
        # Arrange
        mago_castelo = Mago("Gandalf")
        alvo_castelo = Guerreiro("Aragorn")
        combate_castelo = Combate(mago_castelo, alvo_castelo, Castelo())

        mago_caverna = Mago("Saruman")
        alvo_caverna = Guerreiro("Boromir")
        combate_caverna = Combate(mago_caverna, alvo_caverna, Caverna())

        # Act
        no_castelo = combate_castelo.executar_turno(mago_castelo, alvo_castelo)
        na_caverna = combate_caverna.executar_turno(mago_caverna, alvo_caverna)

        # Assert
        self.assertEqual(no_castelo.poder, na_caverna.poder)
        self.assertGreater(no_castelo.dano, na_caverna.dano)
        self.assertEqual(no_castelo.dano, 29)  # round(34 * 1.2) = 41; 41 - 12
        self.assertEqual(na_caverna.dano, 22)


class TestPocaoNoCombate(unittest.TestCase):
    """O combate consome Item do inventário (consumo de classe)."""

    def test_usar_pocao_durante_combate(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")
        guerreiro.receber_dano(50)  # vida 82
        guerreiro.inventario.adicionar(Pocao("Poção de Vida", 30))
        combate = Combate(guerreiro, Arqueiro("Legolas"), Caverna())

        # Act
        mensagem = combate.usar_pocao(guerreiro, "Poção de Vida")

        # Assert
        self.assertEqual(guerreiro.vida, 112)
        self.assertIn("Poção de Vida", mensagem)
        self.assertTrue(guerreiro.inventario.vazio())

    def test_usar_pocao_inexistente_no_combate(self) -> None:
        # Arrange
        combate = Combate(Guerreiro("Aragorn"), Arqueiro("Legolas"), Caverna())

        # Act / Assert
        with self.assertRaises(ItemNaoEncontradoError):
            combate.usar_pocao(combate.combatente_a, "Poção")  # type: ignore[arg-type]

    def test_usar_item_que_nao_e_pocao(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")
        guerreiro.inventario.adicionar(Arma("Andúril", 7))
        combate = Combate(guerreiro, Arqueiro("Legolas"), Caverna())

        # Act / Assert
        with self.assertRaises(ValorInvalidoError):
            combate.usar_pocao(guerreiro, "Andúril")

    def test_usar_pocao_em_nao_personagem(self) -> None:
        # Arrange
        combate = Combate(Guerreiro("Aragorn"), Arqueiro("Legolas"), Caverna())
        aldeao = Aldeao("Tobias")

        # Act / Assert
        with self.assertRaises(AlvoInvalidoError):
            combate.usar_pocao(aldeao, "Poção")  # type: ignore[arg-type]


class TestAldeao(unittest.TestCase):
    """Aldeão fala, mas não luta."""

    def test_aldeao_fala(self) -> None:
        # Arrange
        aldeao = Aldeao("Tobias")

        # Act
        fala = aldeao.falar()

        # Assert
        self.assertIn("Tobias", fala)
        self.assertIn("viajante", fala)

    def test_aldeao_nao_e_combatente(self) -> None:
        from rpg.interfaces import Combatente

        self.assertNotIsInstance(Aldeao("Tobias"), Combatente)


if __name__ == "__main__":
    unittest.main()
