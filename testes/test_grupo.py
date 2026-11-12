"""Testes de Grupo — agregação (Aula 07)."""

import unittest

from rpg.excecoes import AlvoInvalidoError, GrupoCheioError, ValorInvalidoError
from rpg.grupo import Grupo
from rpg.personagem import Arqueiro, Guerreiro, Mago


class TestGrupo(unittest.TestCase):
    """O grupo referencia personagens; não os cria nem os destrói."""

    def test_grupo_comeca_vazio(self) -> None:
        # Arrange / Act
        grupo = Grupo("Companhia")

        # Assert
        self.assertEqual(len(grupo), 0)
        self.assertEqual(grupo.media_nivel(), 0.0)
        self.assertIn("vazio", grupo.resumo())

    def test_grupo_sem_nome_lanca_excecao(self) -> None:
        with self.assertRaises(ValorInvalidoError):
            Grupo("  ")

    def test_grupo_agrega_personagem(self) -> None:
        # Arrange
        grupo = Grupo("Companhia")
        guerreiro = Guerreiro("Aragorn")

        # Act
        grupo.adicionar(guerreiro)

        # Assert
        self.assertEqual(len(grupo), 1)
        self.assertIs(grupo.membros[0], guerreiro)  # referência, não cópia
        self.assertTrue(grupo.contem("Aragorn"))

    def test_grupo_limite_cinco(self) -> None:
        # Arrange
        grupo = Grupo("Companhia")
        for nome in ("A", "B", "C", "D", "E"):
            grupo.adicionar(Guerreiro(nome))

        # Act / Assert
        self.assertEqual(len(grupo), 5)
        with self.assertRaises(GrupoCheioError):
            grupo.adicionar(Guerreiro("F"))

    def test_grupo_rejeita_objeto_invalido(self) -> None:
        # Arrange
        grupo = Grupo("Companhia")

        # Act / Assert
        with self.assertRaises(AlvoInvalidoError):
            grupo.adicionar("Aragorn")  # type: ignore[arg-type]

    def test_grupo_rejeita_membro_duplicado(self) -> None:
        # Arrange
        grupo = Grupo("Companhia")
        guerreiro = Guerreiro("Aragorn")
        grupo.adicionar(guerreiro)

        # Act / Assert
        with self.assertRaises(AlvoInvalidoError):
            grupo.adicionar(guerreiro)

    def test_grupo_remove_personagem(self) -> None:
        # Arrange
        grupo = Grupo("Companhia")
        grupo.adicionar(Guerreiro("Aragorn"))
        grupo.adicionar(Mago("Gandalf"))

        # Act
        removido = grupo.remover("Aragorn")

        # Assert
        self.assertEqual(removido.nome, "Aragorn")
        self.assertEqual(len(grupo), 1)
        self.assertFalse(grupo.contem("Aragorn"))

    def test_grupo_remover_inexistente(self) -> None:
        # Arrange
        grupo = Grupo("Companhia")

        # Act / Assert
        with self.assertRaises(AlvoInvalidoError):
            grupo.remover("Aragorn")

    def test_personagem_sobrevive_ao_grupo(self) -> None:
        """Prova da agregação: dissolver o grupo não destrói os personagens."""
        # Arrange
        guerreiro = Guerreiro("Aragorn")
        mago = Mago("Gandalf")
        grupo = Grupo("Companhia")
        grupo.adicionar(guerreiro)
        grupo.adicionar(mago)

        # Act
        del grupo

        # Assert
        self.assertTrue(guerreiro.esta_vivo())
        self.assertEqual(guerreiro.vida, 120)
        self.assertEqual(guerreiro.ficha.nivel, 1)
        self.assertTrue(mago.esta_vivo())

    def test_media_nivel(self) -> None:
        # Arrange
        grupo = Grupo("Companhia")
        guerreiro = Guerreiro("Aragorn")
        guerreiro.ficha.ganhar_xp(100)  # nível 2
        grupo.adicionar(guerreiro)
        grupo.adicionar(Mago("Gandalf"))  # nível 1

        # Act
        media = grupo.media_nivel()

        # Assert
        self.assertEqual(media, 1.5)

    def test_membros_devolve_copia(self) -> None:
        # Arrange
        grupo = Grupo("Companhia")
        grupo.adicionar(Arqueiro("Legolas"))

        # Act
        lista = grupo.membros
        lista.clear()

        # Assert
        self.assertEqual(len(grupo), 1)

    def test_resumo_lista_membros_e_tipos(self) -> None:
        # Arrange
        grupo = Grupo("Companhia")
        grupo.adicionar(Guerreiro("Aragorn"))
        grupo.adicionar(Arqueiro("Legolas"))

        # Act
        resumo = grupo.resumo()

        # Assert
        self.assertIn("Companhia", resumo)
        self.assertIn("Aragorn (Guerreiro)", resumo)
        self.assertIn("Legolas (Arqueiro)", resumo)


if __name__ == "__main__":
    unittest.main()
