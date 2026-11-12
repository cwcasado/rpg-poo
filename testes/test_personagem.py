"""Testes de Personagem, Guerreiro, Mago e Arqueiro (Aulas 02, 03, 05, 06, 08)."""

import unittest

from rpg.excecoes import (
    AlvoInvalidoError,
    DanoInvalidoError,
    ItemNaoEncontradoError,
    PersonagemMortoError,
    SemManaError,
    ValorInvalidoError,
    VidaInvalidaError,
)
from rpg.ficha import FichaDeStatus
from rpg.interfaces import Combatente
from rpg.inventario import Inventario
from rpg.itens import Arma, Pocao
from rpg.personagem import Arqueiro, Guerreiro, Mago, Personagem


class TestAbstracaoEHeranca(unittest.TestCase):
    """A classe base não existe sozinha; as filhas são personagens."""

    def test_personagem_abstrata_nao_pode_ser_instanciada(self) -> None:
        with self.assertRaises(TypeError):
            Personagem("Fantasma", 10, 10, 10)  # type: ignore[abstract]

    def test_subclasses_sao_personagens(self) -> None:
        # Arrange
        personagens = [Guerreiro("Aragorn"), Mago("Gandalf"), Arqueiro("Legolas")]

        # Act / Assert
        for personagem in personagens:
            with self.subTest(tipo=personagem.tipo):
                self.assertIsInstance(personagem, Personagem)
                self.assertIsInstance(personagem, Combatente)

    def test_cada_personagem_tem_estado_proprio(self) -> None:
        # Arrange
        primeiro = Guerreiro("Aragorn")
        segundo = Guerreiro("Boromir")

        # Act
        primeiro.receber_dano(50)  # defesa 12 → 38 de dano efetivo

        # Assert
        self.assertEqual(primeiro.vida, 82)
        self.assertEqual(segundo.vida, 120)

    def test_nome_vazio_lanca_excecao(self) -> None:
        with self.assertRaises(ValorInvalidoError):
            Guerreiro("   ")

    def test_vida_inicial_invalida_lanca_excecao(self) -> None:
        # Arrange: a classe é abstrata, então testamos o construtor base
        # através de uma instância concreta.
        guerreiro = Guerreiro("Aragorn")

        # Act / Assert
        with self.assertRaises(VidaInvalidaError):
            Personagem.__init__(guerreiro, "Sem Vida", 0, 10, 10)

    def test_resumo_contem_nome_e_tipo(self) -> None:
        # Arrange
        arqueiro = Arqueiro("Legolas")

        # Act
        resumo = arqueiro.resumo()

        # Assert
        self.assertIn("Legolas", resumo)
        self.assertIn("Arqueiro", resumo)
        self.assertIn("vida 95/95", resumo)


class TestComposicao(unittest.TestCase):
    """Ficha e inventário nascem com o personagem e são exclusivos dele."""

    def test_personagem_cria_ficha_e_inventario(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")

        # Act / Assert
        self.assertIsInstance(guerreiro.ficha, FichaDeStatus)
        self.assertIsInstance(guerreiro.inventario, Inventario)
        self.assertEqual(guerreiro.ficha.nivel, 1)
        self.assertTrue(guerreiro.inventario.vazio())

    def test_partes_nao_sao_compartilhadas_entre_personagens(self) -> None:
        # Arrange
        primeiro = Guerreiro("Aragorn")
        segundo = Guerreiro("Boromir")

        # Act
        primeiro.inventario.adicionar(Pocao("Poção", 10))

        # Assert
        self.assertIsNot(primeiro.ficha, segundo.ficha)
        self.assertIsNot(primeiro.inventario, segundo.inventario)
        self.assertEqual(len(primeiro.inventario), 1)
        self.assertEqual(len(segundo.inventario), 0)


class TestAtaquePorSubclasse(unittest.TestCase):
    """Polimorfismo: a mesma mensagem gera poderes diferentes."""

    def test_guerreiro_ataca_com_forca_dobrada(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")
        alvo = Mago("Gandalf")

        # Act
        poder = guerreiro.atacar(alvo)

        # Assert
        self.assertEqual(poder, 36)  # 18 * 2

    def test_mago_consome_mana_ao_atacar(self) -> None:
        # Arrange
        mago = Mago("Gandalf")
        alvo = Guerreiro("Aragorn")

        # Act
        poder = mago.atacar(alvo)

        # Assert
        self.assertEqual(poder, 34)  # 14 + 40 // 2
        self.assertEqual(mago.mana, 35)

    def test_arqueiro_soma_precisao_ao_dano(self) -> None:
        # Arrange
        arqueiro = Arqueiro("Legolas")
        alvo = Guerreiro("Aragorn")

        # Act
        poder = arqueiro.atacar(alvo)

        # Assert
        self.assertEqual(poder, 21)  # 15 + 6

    def test_mago_sem_mana_lanca_excecao(self) -> None:
        # Arrange
        mago = Mago("Gandalf")
        alvo = Guerreiro("Aragorn")
        for _ in range(8):
            mago.atacar(alvo)

        # Act / Assert
        self.assertEqual(mago.mana, 0)
        with self.assertRaises(SemManaError):
            mago.atacar(alvo)

    def test_mago_recarrega_mana(self) -> None:
        # Arrange
        mago = Mago("Gandalf")
        mago.atacar(Guerreiro("Aragorn"))

        # Act
        mana = mago.recarregar_mana(15)

        # Assert
        self.assertEqual(mana, 50)

    def test_mago_recarrega_mana_invalida(self) -> None:
        # Arrange
        mago = Mago("Gandalf")

        # Act / Assert
        with self.assertRaises(ValorInvalidoError):
            mago.recarregar_mana(0)


class TestInteracao(unittest.TestCase):
    """Passagem de mensagem entre dois objetos (Aula 03)."""

    def test_atacar_interage_com_receber_dano(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")
        arqueiro = Arqueiro("Legolas")

        # Act
        poder = guerreiro.atacar(arqueiro)
        dano = arqueiro.receber_dano(poder)

        # Assert
        self.assertEqual(poder, 36)
        self.assertEqual(dano, 28)  # 36 - defesa 8
        self.assertEqual(arqueiro.vida, 67)

    def test_atacar_alvo_invalido_lanca_excecao(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")

        # Act / Assert
        with self.assertRaises(AlvoInvalidoError):
            guerreiro.atacar("dragão")  # type: ignore[arg-type]


class TestDanoEDefesa(unittest.TestCase):
    """Regras de dano: piso 1, vida nunca negativa, defesa reduz."""

    def test_receber_dano_aplica_defesa_com_piso_um(self) -> None:
        # Arrange
        arqueiro = Arqueiro("Legolas")

        # Act
        dano = arqueiro.receber_dano(5)  # defesa 8

        # Assert
        self.assertEqual(dano, 1)
        self.assertEqual(arqueiro.vida, 94)

    def test_receber_dano_nao_deixa_vida_negativa(self) -> None:
        # Arrange
        arqueiro = Arqueiro("Legolas")

        # Act
        arqueiro.receber_dano(9999)

        # Assert
        self.assertEqual(arqueiro.vida, 0)
        self.assertFalse(arqueiro.esta_vivo())

    def test_receber_dano_invalido_lanca_excecao(self) -> None:
        # Arrange
        arqueiro = Arqueiro("Legolas")

        # Act / Assert
        with self.assertRaises(DanoInvalidoError):
            arqueiro.receber_dano(0)

    def test_defender_reduz_proximo_dano(self) -> None:
        # Arrange
        arqueiro = Arqueiro("Legolas")

        # Act
        defesa = arqueiro.defender()
        dano = arqueiro.receber_dano(20)

        # Assert
        self.assertEqual(defesa, 8)
        self.assertEqual(dano, 6)  # (20 - 8) // 2
        self.assertEqual(arqueiro.vida, 89)

    def test_defesa_vale_apenas_um_golpe(self) -> None:
        # Arrange
        arqueiro = Arqueiro("Legolas")
        arqueiro.defender()

        # Act
        arqueiro.receber_dano(20)
        segundo_dano = arqueiro.receber_dano(20)

        # Assert
        self.assertEqual(segundo_dano, 12)

    def test_personagem_morto_nao_ataca(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")
        alvo = Mago("Gandalf")
        guerreiro.receber_dano(9999)

        # Act / Assert
        with self.assertRaises(PersonagemMortoError):
            guerreiro.atacar(alvo)

    def test_personagem_morto_nao_defende(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")
        guerreiro.receber_dano(9999)

        # Act / Assert
        with self.assertRaises(PersonagemMortoError):
            guerreiro.defender()


class TestCuraEItens(unittest.TestCase):
    """Cura limitada e uso de itens via polimorfismo."""

    def test_curar_nao_ultrapassa_vida_maxima(self) -> None:
        # Arrange
        arqueiro = Arqueiro("Legolas")
        arqueiro.receber_dano(30)  # defesa 8 → 22 de dano

        # Act
        recuperado = arqueiro.curar(500)

        # Assert
        self.assertEqual(recuperado, 22)
        self.assertEqual(arqueiro.vida, 95)

    def test_curar_com_valor_invalido_lanca_excecao(self) -> None:
        # Arrange
        arqueiro = Arqueiro("Legolas")

        # Act / Assert
        with self.assertRaises(DanoInvalidoError):
            arqueiro.curar(0)

    def test_usar_item_delega_para_item(self) -> None:
        # Arrange
        arqueiro = Arqueiro("Legolas")
        arqueiro.receber_dano(40)  # defesa 8 → 32 de dano
        arqueiro.inventario.adicionar(Pocao("Poção de Vida", 25))

        # Act
        mensagem = arqueiro.usar_item("Poção de Vida")

        # Assert
        self.assertEqual(arqueiro.vida, 88)
        self.assertIn("Poção de Vida", mensagem)
        self.assertTrue(arqueiro.inventario.vazio())  # consumível saiu

    def test_usar_item_inexistente_lanca_excecao(self) -> None:
        # Arrange
        arqueiro = Arqueiro("Legolas")

        # Act / Assert
        with self.assertRaises(ItemNaoEncontradoError):
            arqueiro.usar_item("Machado")

    def test_arma_nao_e_consumida_e_aumenta_dano(self) -> None:
        # Arrange
        guerreiro = Guerreiro("Aragorn")
        guerreiro.inventario.adicionar(Arma("Andúril", 7))

        # Act
        guerreiro.usar_item("Andúril")
        poder = guerreiro.atacar(Mago("Gandalf"))

        # Assert
        self.assertEqual(guerreiro.bonus_ataque, 7)
        self.assertEqual(poder, 50)  # (18 + 7) * 2
        self.assertEqual(len(guerreiro.inventario), 1)

    def test_personagem_morto_nao_usa_item(self) -> None:
        # Arrange
        arqueiro = Arqueiro("Legolas")
        arqueiro.inventario.adicionar(Pocao("Poção", 10))
        arqueiro.receber_dano(9999)

        # Act / Assert
        with self.assertRaises(PersonagemMortoError):
            arqueiro.usar_item("Poção")

    def test_bonus_negativo_lanca_excecao(self) -> None:
        # Arrange
        arqueiro = Arqueiro("Legolas")

        # Act / Assert
        with self.assertRaises(ValorInvalidoError):
            arqueiro.receber_bonus_ataque(-1)


if __name__ == "__main__":
    unittest.main()
