"""Inventário — parte composta do personagem.

Aula 07 — Composição: o inventário nasce junto com o personagem e morre com ele.
Aula 08 — Exceção própria quando o item procurado não existe.

O inventário **agrega** itens: os itens são criados fora e apenas referenciados
aqui (losango vazio no diagrama).
"""

from __future__ import annotations

from rpg.excecoes import ItemNaoEncontradoError, ValorInvalidoError
from rpg.itens import Item


class Inventario:
    """Coleção de itens de um personagem.

    Example:
        >>> inventario = Inventario()
        >>> inventario.adicionar(Pocao("Poção", 20))
        >>> inventario.buscar("poção").nome
        'Poção'
    """

    def __init__(self) -> None:
        """Cria um inventário vazio."""
        self._itens: list[Item] = []

    def adicionar(self, item: Item) -> None:
        """Adiciona um item ao inventário.

        Args:
            item: instância de :class:`~rpg.itens.Item`.

        Raises:
            ValorInvalidoError: se ``item`` não for um ``Item``.
        """
        if not isinstance(item, Item):
            raise ValorInvalidoError("apenas itens podem ser guardados no inventário")
        self._itens.append(item)

    def buscar(self, nome: str) -> Item:
        """Procura um item pelo nome (sem diferenciar maiúsculas de minúsculas).

        Args:
            nome: nome procurado.

        Returns:
            O primeiro item com esse nome.

        Raises:
            ItemNaoEncontradoError: se não houver item com o nome informado.
        """
        procurado = nome.strip().casefold()
        for item in self._itens:
            if item.nome.casefold() == procurado:
                return item
        raise ItemNaoEncontradoError(f"o item '{nome}' não está no inventário")

    def remover(self, nome: str) -> Item:
        """Remove e devolve um item pelo nome.

        Args:
            nome: nome do item a remover.

        Returns:
            O item removido.

        Raises:
            ItemNaoEncontradoError: se o item não existir no inventário.
        """
        item = self.buscar(nome)
        self._itens.remove(item)
        return item

    def listar(self) -> list[Item]:
        """Devolve uma cópia da lista de itens (protege o estado interno)."""
        return list(self._itens)

    def nomes(self) -> list[str]:
        """Nomes dos itens na ordem em que foram guardados."""
        return [item.nome for item in self._itens]

    def vazio(self) -> bool:
        """Indica se o inventário está vazio."""
        return not self._itens

    def __len__(self) -> int:
        return len(self._itens)

    def __iter__(self):
        return iter(self._itens)

    def __str__(self) -> str:
        return ", ".join(self.nomes()) if self._itens else "vazio"
