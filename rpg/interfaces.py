"""Contrato de combate — interface explícita do sistema.

Aula 06 — Interfaces. Em Python a interface é uma classe abstrata sem estado:
um contrato que obriga as subclasses a implementarem as assinaturas. Quem não
realiza :class:`Combatente` não participa de combate (ver ``rpg/combate.py``).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # apenas para tipagem — evita import circular
    from rpg.personagem import Personagem


class Combatente(ABC):
    """Contrato obrigatório de quem participa de um combate.

    Implementar esta interface significa prometer duas operações: atacar e
    defender. O :class:`~rpg.combate.Combate` valida ``isinstance(x, Combatente)``
    antes de iniciar a luta.

    Example:
        >>> isinstance(Guerreiro("Aragorn"), Combatente)
        True
    """

    @abstractmethod
    def atacar(self, alvo: "Personagem") -> int:
        """Calcula e devolve o poder de ataque contra ``alvo``.

        Args:
            alvo: personagem que receberá o dano.

        Returns:
            Poder de ataque bruto (antes da defesa do alvo).
        """

    @abstractmethod
    def defender(self) -> int:
        """Assume postura defensiva até o próximo dano recebido.

        Returns:
            Valor de defesa ativo no turno.
        """
