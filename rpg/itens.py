"""Itens do RPG — abstração e polimorfismo.

Aula 05 — Abstração: :class:`Item` não existe por si só; só as subclasses concretas
podem ser instanciadas.
Aula 08 — *Overriding*: cada subclasse implementa ``usar`` com seu próprio efeito.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from rpg.excecoes import ValorInvalidoError

if TYPE_CHECKING:  # evita import circular em tempo de execução
    from rpg.personagem import Personagem


class Item(ABC):
    """Item genérico de inventário.

    Attributes:
        consumivel: indica se o item deve ser removido do inventário após o uso.

    Example:
        >>> Pocao("Poção de Vida", 30).usar(guerreiro)
        'Aragorn recuperou 30 de vida com Poção de Vida.'
    """

    consumivel: bool = False

    def __init__(self, nome: str, descricao: str = "") -> None:
        """Inicializa o item.

        Args:
            nome: nome exibido no inventário.
            descricao: texto livre opcional.

        Raises:
            ValorInvalidoError: se ``nome`` for vazio ou só espaços.
        """
        if not nome or not nome.strip():
            raise ValorInvalidoError("o nome do item não pode ser vazio")
        self._nome = nome.strip()
        self._descricao = descricao.strip()

    @property
    def nome(self) -> str:
        """Nome do item."""
        return self._nome

    def descricao(self) -> str:
        """Descrição legível do item (usa o nome quando não há descrição)."""
        return self._descricao or self._nome

    @abstractmethod
    def usar(self, personagem: "Personagem") -> str:
        """Aplica o efeito do item em ``personagem``.

        Args:
            personagem: alvo do efeito.

        Returns:
            Mensagem descrevendo o que aconteceu.
        """

    def __str__(self) -> str:
        return self._nome

    def __repr__(self) -> str:
        return f"{type(self).__name__}(nome={self._nome!r})"


class Pocao(Item):
    """Poção que recupera vida e é consumida no uso."""

    consumivel = True

    def __init__(self, nome: str, cura: int, descricao: str = "") -> None:
        """Inicializa a poção.

        Args:
            nome: nome do item.
            cura: quantidade de vida recuperada (deve ser positiva).
            descricao: texto livre opcional.

        Raises:
            ValorInvalidoError: se ``cura`` for menor ou igual a zero.
        """
        super().__init__(nome, descricao)
        if cura <= 0:
            raise ValorInvalidoError("a cura da poção deve ser maior que zero")
        self._cura = cura

    @property
    def cura(self) -> int:
        """Quantidade de vida recuperada."""
        return self._cura

    def usar(self, personagem: "Personagem") -> str:
        """Cura o personagem, limitado à vida máxima dele."""
        recuperado = personagem.curar(self._cura)
        return f"{personagem.nome} recuperou {recuperado} de vida com {self._nome}."


class Arma(Item):
    """Arma que aumenta permanentemente o bônus de ataque do personagem."""

    def __init__(self, nome: str, bonus_ataque: int, descricao: str = "") -> None:
        """Inicializa a arma.

        Args:
            nome: nome do item.
            bonus_ataque: bônus somado ao ataque (deve ser ≥ 0).
            descricao: texto livre opcional.

        Raises:
            ValorInvalidoError: se ``bonus_ataque`` for negativo.
        """
        super().__init__(nome, descricao)
        if bonus_ataque < 0:
            raise ValorInvalidoError("o bônus de ataque não pode ser negativo")
        self._bonus_ataque = bonus_ataque

    @property
    def bonus_ataque(self) -> int:
        """Bônus de ataque concedido."""
        return self._bonus_ataque

    def usar(self, personagem: "Personagem") -> str:
        """Equipa a arma, somando o bônus ao personagem (não é consumida)."""
        personagem.receber_bonus_ataque(self._bonus_ataque)
        return f"{personagem.nome} equipou {self._nome} (+{self._bonus_ataque} de ataque)."


class Armadura(Item):
    """Armadura que aumenta permanentemente o bônus de defesa do personagem."""

    def __init__(self, nome: str, bonus_defesa: int, descricao: str = "") -> None:
        """Inicializa a armadura.

        Args:
            nome: nome do item.
            bonus_defesa: bônus somado à defesa (deve ser ≥ 0).
            descricao: texto livre opcional.

        Raises:
            ValorInvalidoError: se ``bonus_defesa`` for negativo.
        """
        super().__init__(nome, descricao)
        if bonus_defesa < 0:
            raise ValorInvalidoError("o bônus de defesa não pode ser negativo")
        self._bonus_defesa = bonus_defesa

    @property
    def bonus_defesa(self) -> int:
        """Bônus de defesa concedido."""
        return self._bonus_defesa

    def usar(self, personagem: "Personagem") -> str:
        """Equipa a armadura, somando o bônus ao personagem (não é consumida)."""
        personagem.receber_bonus_defesa(self._bonus_defesa)
        return f"{personagem.nome} equipou {self._nome} (+{self._bonus_defesa} de defesa)."
