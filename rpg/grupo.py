"""Grupo de personagens — agregação.

Aula 07 — Agregação: o grupo **referencia** personagens criados fora dele.
Se o grupo deixar de existir, os personagens continuam existindo (losango vazio
no diagrama). O grupo nunca cria nem destrói personagens.
"""

from __future__ import annotations

from rpg.excecoes import AlvoInvalidoError, GrupoCheioError, ValorInvalidoError
from rpg.personagem import Personagem


class Grupo:
    """Grupo (guilda) que agrega até cinco personagens.

    Attributes:
        LIMITE: número máximo de membros.

    Example:
        >>> grupo = Grupo("Companhia")
        >>> grupo.adicionar(Guerreiro("Aragorn"))
        >>> len(grupo)
        1
    """

    LIMITE: int = 5

    def __init__(self, nome: str) -> None:
        """Cria um grupo vazio.

        Args:
            nome: nome do grupo.

        Raises:
            ValorInvalidoError: se o nome for vazio.
        """
        if not nome or not nome.strip():
            raise ValorInvalidoError("o nome do grupo não pode ser vazio")
        self._nome = nome.strip()
        self._membros: list[Personagem] = []

    @property
    def nome(self) -> str:
        """Nome do grupo."""
        return self._nome

    @property
    def membros(self) -> list[Personagem]:
        """Cópia da lista de membros (protege o estado interno)."""
        return list(self._membros)

    def adicionar(self, personagem: Personagem) -> None:
        """Agrega um personagem já existente ao grupo.

        Args:
            personagem: personagem criado fora do grupo.

        Raises:
            AlvoInvalidoError: objeto que não é personagem ou já está no grupo.
            GrupoCheioError: grupo já tem :attr:`LIMITE` membros.
        """
        if not isinstance(personagem, Personagem):
            raise AlvoInvalidoError("apenas personagens podem entrar em um grupo")
        if personagem in self._membros:
            raise AlvoInvalidoError(f"{personagem.nome} já está no grupo {self._nome}")
        if len(self._membros) >= self.LIMITE:
            raise GrupoCheioError(
                f"o grupo {self._nome} já tem {self.LIMITE} membros"
            )
        self._membros.append(personagem)

    def remover(self, nome: str) -> Personagem:
        """Remove um membro pelo nome.

        Args:
            nome: nome do personagem.

        Returns:
            O personagem removido (ele continua existindo).

        Raises:
            AlvoInvalidoError: se o personagem não estiver no grupo.
        """
        procurado = nome.strip().casefold()
        for membro in self._membros:
            if membro.nome.casefold() == procurado:
                self._membros.remove(membro)
                return membro
        raise AlvoInvalidoError(f"{nome} não faz parte do grupo {self._nome}")

    def contem(self, nome: str) -> bool:
        """Informa se o grupo tem um membro com esse nome."""
        procurado = nome.strip().casefold()
        return any(membro.nome.casefold() == procurado for membro in self._membros)

    def media_nivel(self) -> float:
        """Média de nível dos membros (0.0 se o grupo estiver vazio)."""
        if not self._membros:
            return 0.0
        total = sum(membro.ficha.nivel for membro in self._membros)
        return total / len(self._membros)

    def resumo(self) -> str:
        """Texto com nome, quantidade e membros."""
        if not self._membros:
            return f"Grupo {self._nome} (vazio)"
        nomes = ", ".join(f"{m.nome} ({m.tipo})" for m in self._membros)
        return (
            f"Grupo {self._nome} ({len(self._membros)}/{self.LIMITE}) — {nomes} | "
            f"média de nível {self.media_nivel():.1f}"
        )

    def __len__(self) -> int:
        return len(self._membros)

    def __iter__(self):
        return iter(self._membros)

    def __str__(self) -> str:
        return self.resumo()
