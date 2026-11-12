"""Cenários — o ambiente que favorece um tipo de personagem.

Aula 04/Aula 06 — Abstração e interface de uso. Todo cenário responde à mesma
mensagem ``bonus_para(personagem)``, mas o resultado depende do tipo favorecido.

Regra de negócio RN06: o cenário concede **+20% de ataque** ao tipo que ele
favorece e 0% aos demais.

O cenário apenas **consulta** o personagem; quem aplica o bônus é o
:class:`~rpg.combate.Combate` (consumo de classe).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from rpg.excecoes import AlvoInvalidoError, CenarioInvalidoError
from rpg.personagem import Arqueiro, Guerreiro, Mago, Personagem


class Cenario(ABC):
    """Classe abstrata de cenário.

    Não pode ser instanciada diretamente: só ``Floresta``, ``Caverna`` e
    ``Castelo`` existem de fato.

    Example:
        >>> Caverna().bonus_para(Guerreiro("Aragorn"))
        0.2
        >>> Caverna().bonus_para(Mago("Gandalf"))
        0.0
    """

    def __init__(
        self,
        nome: str,
        classe_favorecida: type[Personagem],
        bonus: float = 0.20,
    ) -> None:
        """Inicializa o cenário.

        Args:
            nome: nome do cenário.
            classe_favorecida: subclasse de ``Personagem`` que recebe o bônus.
            bonus: fração de bônus (0.20 = +20%).
        """
        self._nome = nome
        self._classe_favorecida = classe_favorecida
        self._bonus = bonus

    @property
    def nome(self) -> str:
        """Nome do cenário."""
        return self._nome

    @property
    def classe_favorecida(self) -> type[Personagem]:
        """Classe que recebe o bônus."""
        return self._classe_favorecida

    @property
    def bonus(self) -> float:
        """Fração de bônus concedida ao tipo favorecido."""
        return self._bonus

    def bonus_para(self, personagem: Personagem) -> float:
        """Calcula o bônus de ataque para ``personagem``.

        Args:
            personagem: personagem consultado.

        Returns:
            ``bonus`` (0.20) se o personagem for da classe favorecida; 0.0 caso contrário.

        Raises:
            AlvoInvalidoError: se ``personagem`` não for um ``Personagem``.
        """
        if not isinstance(personagem, Personagem):
            raise AlvoInvalidoError("o cenário só avalia personagens")
        if isinstance(personagem, self._classe_favorecida):
            return self._bonus
        return 0.0

    @abstractmethod
    def descricao(self) -> str:
        """Texto que explica quem o cenário favorece."""

    def __str__(self) -> str:
        return self._nome

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class Floresta(Cenario):
    """Floresta: favorece o Arqueiro (+20% de ataque)."""

    def __init__(self) -> None:
        super().__init__("Floresta", Arqueiro)
        self._descricao = "Floresta — cobertura natural: +20% de ataque para Arqueiros."

    def descricao(self) -> str:
        return self._descricao


class Caverna(Cenario):
    """Caverna: favorece o Guerreiro (+20% de ataque)."""

    def __init__(self) -> None:
        super().__init__("Caverna", Guerreiro)
        self._descricao = "Caverna — espaço fechado: +20% de ataque para Guerreiros."

    def descricao(self) -> str:
        return self._descricao


class Castelo(Cenario):
    """Castelo: favorece o Mago (+20% de ataque)."""

    def __init__(self) -> None:
        super().__init__("Castelo", Mago)
        self._descricao = "Castelo — energia arcana: +20% de ataque para Magos."

    def descricao(self) -> str:
        return self._descricao


_CENARIOS: dict[str, type[Cenario]] = {
    "1": Floresta,
    "2": Caverna,
    "3": Castelo,
    "floresta": Floresta,
    "caverna": Caverna,
    "castelo": Castelo,
}


def criar_cenario(opcao: str) -> Cenario:
    """Fábrica de cenários por número ou nome.

    Args:
        opcao: ``"1"``/``"floresta"``, ``"2"``/``"caverna"`` ou ``"3"``/``"castelo"``.

    Returns:
        Instância do cenário correspondente.

    Raises:
        CenarioInvalidoError: se a opção não existir.

    Example:
        >>> criar_cenario("2").nome
        'Caverna'
    """
    chave = str(opcao).strip().casefold()
    if chave not in _CENARIOS:
        raise CenarioInvalidoError(
            f"cenário '{opcao}' não existe — use 1 Floresta, 2 Caverna ou 3 Castelo"
        )
    return _CENARIOS[chave]()
