"""Ficha de status — parte composta do personagem.

Aula 07 — Composição: a ficha é criada **dentro** do construtor de
:class:`~rpg.personagem.Personagem`. Ela não é passada de fora e não tem sentido
sem o personagem dono.
"""

from __future__ import annotations

from rpg.excecoes import ValorInvalidoError


class FichaDeStatus:
    """Progressão do personagem: nível e experiência.

    Attributes:
        XP_POR_NIVEL: experiência necessária para subir um nível.

    Example:
        >>> ficha = FichaDeStatus()
        >>> ficha.ganhar_xp(100)
        2
        >>> ficha.nivel
        2
    """

    XP_POR_NIVEL: int = 100

    def __init__(self) -> None:
        """Cria a ficha no nível 1, com zero de experiência."""
        self._nivel = 1
        self._xp = 0

    @property
    def nivel(self) -> int:
        """Nível atual do personagem."""
        return self._nivel

    @property
    def xp(self) -> int:
        """Experiência acumulada dentro do nível atual."""
        return self._xp

    def ganhar_xp(self, quantidade: int) -> int:
        """Soma experiência e sobe de nível enquanto houver XP suficiente.

        Args:
            quantidade: experiência recebida (deve ser positiva).

        Returns:
            Nível resultante.

        Raises:
            ValorInvalidoError: se ``quantidade`` for menor ou igual a zero.
        """
        if quantidade <= 0:
            raise ValorInvalidoError("a experiência recebida deve ser maior que zero")

        self._xp += quantidade
        while self._xp >= self.XP_POR_NIVEL:
            self._xp -= self.XP_POR_NIVEL
            self.subir_nivel()
        return self._nivel

    def subir_nivel(self) -> int:
        """Incrementa o nível em 1.

        Returns:
            Novo nível.
        """
        self._nivel += 1
        return self._nivel

    def resumo(self) -> str:
        """Texto de uma linha com nível e XP."""
        return f"nível {self._nivel} ({self._xp}/{self.XP_POR_NIVEL} XP)"

    def __str__(self) -> str:
        return self.resumo()
