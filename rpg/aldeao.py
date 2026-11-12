"""Aldeão — objeto que **não** é combatente.

Aula 06 — Interfaces e segregação: nem todo objeto do domínio participa de um
combate. ``Aldeao`` tem seu próprio comportamento (falar) e **não** realiza o
contrato :class:`~rpg.interfaces.Combatente`, por isso o
:class:`~rpg.combate.Combate` o recusa com ``AlvoInvalidoError``.
"""

from __future__ import annotations

from rpg.excecoes import ValorInvalidoError


class Aldeao:
    """Morador da vila: conversa, mas não luta.

    Example:
        >>> Aldeao("Tobias").falar()
        'Tobias: bem-vindo, viajante. Cuidado com a caverna ao norte.'
    """

    def __init__(self, nome: str = "Tobias") -> None:
        """Cria o aldeão.

        Args:
            nome: nome do aldeão.

        Raises:
            ValorInvalidoError: se o nome for vazio.
        """
        if not nome or not nome.strip():
            raise ValorInvalidoError("o nome do aldeão não pode ser vazio")
        self._nome = nome.strip()

    @property
    def nome(self) -> str:
        """Nome do aldeão."""
        return self._nome

    def falar(self) -> str:
        """Devolve a fala do aldeão."""
        return f"{self._nome}: bem-vindo, viajante. Cuidado com a caverna ao norte."

    def __str__(self) -> str:
        return self._nome

    def __repr__(self) -> str:
        return f"Aldeao(nome={self._nome!r})"
