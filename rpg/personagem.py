"""Personagens — abstração, herança e polimorfismo.

Aula 02 — Classes e objetos: cada personagem é uma instância com estado próprio.
Aula 03 — Atributos, métodos e interação: ``atacar(alvo)`` envia mensagem a outro objeto.
Aula 05 — Abstração: :class:`Personagem` não pode ser instanciada diretamente.
Aula 06 — Interface: a classe realiza o contrato :class:`~rpg.interfaces.Combatente`.
Aula 07 — Composição: ficha e inventário nascem no construtor.
Aula 08 — Herança e *overriding*: as subclasses redefinem ``atacar``.
"""

from __future__ import annotations

from abc import abstractmethod

from rpg.excecoes import (
    AlvoInvalidoError,
    DanoInvalidoError,
    PersonagemMortoError,
    SemManaError,
    ValorInvalidoError,
    VidaInvalidaError,
)
from rpg.ficha import FichaDeStatus
from rpg.interfaces import Combatente
from rpg.inventario import Inventario
from rpg.itens import Item


class Personagem(Combatente):
    """Classe abstrata que representa qualquer personagem do RPG.

    Não pode ser instanciada: só as subclasses concretas
    (:class:`Guerreiro`, :class:`Mago`, :class:`Arqueiro`) existem de fato.

    Attributes:
        ficha: progressão do personagem — **composta**, criada aqui dentro.
        inventario: itens do personagem — **composto**, criado aqui dentro.

    Example:
        >>> guerreiro = Guerreiro("Aragorn")
        >>> guerreiro.vida
        120
        >>> guerreiro.ficha.nivel
        1
    """

    def __init__(self, nome: str, vida: int, forca: int, defesa: int) -> None:
        """Inicializa o estado comum a todos os personagens.

        Args:
            nome: nome do personagem.
            vida: vida inicial e máxima (deve ser positiva).
            forca: força base (deve ser positiva).
            defesa: defesa base (não pode ser negativa).

        Raises:
            ValorInvalidoError: nome vazio, força ≤ 0 ou defesa < 0.
            VidaInvalidaError: vida ≤ 0.
        """
        if not nome or not nome.strip():
            raise ValorInvalidoError("o nome do personagem não pode ser vazio")
        if vida <= 0:
            raise VidaInvalidaError("a vida inicial deve ser maior que zero")
        if forca <= 0:
            raise ValorInvalidoError("a força deve ser maior que zero")
        if defesa < 0:
            raise ValorInvalidoError("a defesa não pode ser negativa")

        self._nome = nome.strip()
        self._vida = vida
        self._vida_maxima = vida
        self._forca = forca
        self._defesa = defesa
        self._bonus_ataque = 0
        self._bonus_defesa = 0
        self._defendendo = False

        # Composição (Aula 07): as partes nascem junto com o todo.
        self.ficha = FichaDeStatus()
        self.inventario = Inventario()

    # ------------------------------------------------------------------ estado

    @property
    def nome(self) -> str:
        """Nome do personagem."""
        return self._nome

    @property
    def tipo(self) -> str:
        """Nome da classe concreta (usado em menus e no resumo)."""
        return type(self).__name__

    @property
    def vida(self) -> int:
        """Vida atual."""
        return self._vida

    @property
    def vida_maxima(self) -> int:
        """Vida máxima do personagem."""
        return self._vida_maxima

    @property
    def forca(self) -> int:
        """Força base."""
        return self._forca

    @property
    def defesa(self) -> int:
        """Defesa base."""
        return self._defesa

    @property
    def bonus_ataque(self) -> int:
        """Bônus de ataque acumulado por armas."""
        return self._bonus_ataque

    @property
    def bonus_defesa(self) -> int:
        """Bônus de defesa acumulado por armaduras."""
        return self._bonus_defesa

    @property
    def defendendo(self) -> bool:
        """Indica se o personagem está em postura defensiva."""
        return self._defendendo

    def esta_vivo(self) -> bool:
        """Informa se o personagem ainda tem vida."""
        return self._vida > 0

    # ------------------------------------------------------------- combate

    def _validar_ataque(self, alvo: "Personagem") -> None:
        """Valida atacante, alvo e estado de ambos antes de calcular o dano.

        Args:
            alvo: personagem que receberá o ataque.

        Raises:
            PersonagemMortoError: atacante ou alvo com vida zero.
            AlvoInvalidoError: alvo que não é ``Personagem``.
        """
        if not isinstance(alvo, Personagem):
            raise AlvoInvalidoError("o alvo do ataque deve ser um personagem")
        if not self.esta_vivo():
            raise PersonagemMortoError(f"{self._nome} está morto e não pode atacar")
        if not alvo.esta_vivo():
            raise PersonagemMortoError(f"{alvo.nome} já está morto")

    @abstractmethod
    def atacar(self, alvo: "Personagem") -> int:
        """Calcula o poder de ataque contra ``alvo``.

        Args:
            alvo: personagem que receberá o dano.

        Returns:
            Poder de ataque bruto, antes da defesa do alvo.
        """

    def defender(self) -> int:
        """Assume postura defensiva: o próximo dano recebido cai pela metade.

        Returns:
            Defesa total (base + bônus de armadura).

        Raises:
            PersonagemMortoError: se o personagem estiver morto.
        """
        if not self.esta_vivo():
            raise PersonagemMortoError(f"{self._nome} está morto e não pode defender")
        self._defendendo = True
        return self._defesa + self._bonus_defesa

    def receber_dano(self, dano: int) -> int:
        """Aplica dano, descontando defesa e respeitando o piso de 1.

        A vida **nunca** fica negativa: o resultado é limitado a zero.

        Args:
            dano: poder de ataque recebido (deve ser positivo).

        Returns:
            Dano efetivamente aplicado.

        Raises:
            DanoInvalidoError: se ``dano`` for menor ou igual a zero.
            PersonagemMortoError: se o personagem já estiver morto.
        """
        if dano <= 0:
            raise DanoInvalidoError("o dano recebido deve ser maior que zero")
        if not self.esta_vivo():
            raise PersonagemMortoError(f"{self._nome} já está morto")

        defesa_total = self._defesa + self._bonus_defesa
        efetivo = max(1, dano - defesa_total)
        if self._defendendo:
            efetivo = max(1, efetivo // 2)
            self._defendendo = False

        self._vida = max(0, self._vida - efetivo)
        return efetivo

    # ------------------------------------------------------------- cura/itens

    def curar(self, valor: int) -> int:
        """Recupera vida, limitado à vida máxima.

        Args:
            valor: quantidade de cura (deve ser positiva).

        Returns:
            Quanto de vida foi realmente recuperado.

        Raises:
            DanoInvalidoError: se ``valor`` for menor ou igual a zero.
            PersonagemMortoError: se o personagem estiver morto.
        """
        if valor <= 0:
            raise DanoInvalidoError("a cura deve ser maior que zero")
        if not self.esta_vivo():
            raise PersonagemMortoError(f"{self._nome} está morto e não pode ser curado")

        recuperado = min(valor, self._vida_maxima - self._vida)
        self._vida += recuperado
        return recuperado

    def usar_item(self, nome: str) -> str:
        """Usa um item do inventário, removendo-o se for consumível.

        Args:
            nome: nome do item.

        Returns:
            Mensagem do efeito aplicado.

        Raises:
            PersonagemMortoError: se o personagem estiver morto.
            ItemNaoEncontradoError: se o item não estiver no inventário.
        """
        if not self.esta_vivo():
            raise PersonagemMortoError(f"{self._nome} está morto e não pode usar itens")

        item: Item = self.inventario.buscar(nome)  # levanta ItemNaoEncontradoError
        mensagem = item.usar(self)
        if item.consumivel:
            self.inventario.remover(item.nome)
        return mensagem

    def receber_bonus_ataque(self, valor: int) -> None:
        """Soma bônus permanente de ataque (usado por armas).

        Args:
            valor: bônus a somar (não pode ser negativo).

        Raises:
            ValorInvalidoError: se ``valor`` for negativo.
        """
        if valor < 0:
            raise ValorInvalidoError("o bônus de ataque não pode ser negativo")
        self._bonus_ataque += valor

    def receber_bonus_defesa(self, valor: int) -> None:
        """Soma bônus permanente de defesa (usado por armaduras).

        Args:
            valor: bônus a somar (não pode ser negativo).

        Raises:
            ValorInvalidoError: se ``valor`` for negativo.
        """
        if valor < 0:
            raise ValorInvalidoError("o bônus de defesa não pode ser negativo")
        self._bonus_defesa += valor

    # ------------------------------------------------------------- exibição

    def resumo(self) -> str:
        """Linha única com estado completo do personagem."""
        return (
            f"{self._nome} ({self.tipo}) — vida {self._vida}/{self._vida_maxima} | "
            f"força {self._forca} | defesa {self._defesa} | "
            f"ataque +{self._bonus_ataque} | defesa +{self._bonus_defesa} | "
            f"{self.ficha.resumo()}"
        )

    def __str__(self) -> str:
        return self.resumo()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(nome={self._nome!r}, vida={self._vida})"


class Guerreiro(Personagem):
    """Especialista em combate corpo a corpo: golpe pesado (força dobrada)."""

    def __init__(self, nome: str) -> None:
        """Cria um guerreiro com vida 120, força 18 e defesa 12."""
        super().__init__(nome, vida=120, forca=18, defesa=12)

    def atacar(self, alvo: Personagem) -> int:
        """Golpe pesado: dobra a força somada ao bônus de arma."""
        self._validar_ataque(alvo)
        return (self._forca + self._bonus_ataque) * 2


class Mago(Personagem):
    """Conjurador: ataque ampliado pela mana, que é consumida a cada golpe."""

    MANA_INICIAL: int = 40
    CUSTO_DE_MANA: int = 5

    def __init__(self, nome: str) -> None:
        """Cria um mago com vida 80, força 14, defesa 6 e 40 de mana."""
        super().__init__(nome, vida=80, forca=14, defesa=6)
        self._mana = self.MANA_INICIAL

    @property
    def mana(self) -> int:
        """Mana disponível."""
        return self._mana

    def atacar(self, alvo: Personagem) -> int:
        """Conjura: força + metade da mana atual; consome 5 de mana.

        Raises:
            SemManaError: se a mana for menor que :attr:`CUSTO_DE_MANA`.
        """
        self._validar_ataque(alvo)
        if self._mana < self.CUSTO_DE_MANA:
            raise SemManaError(f"{self._nome} não tem mana suficiente para atacar")

        poder = self._forca + self._bonus_ataque + self._mana // 2
        self._mana -= self.CUSTO_DE_MANA
        return poder

    def recarregar_mana(self, quantidade: int) -> int:
        """Recupera mana.

        Args:
            quantidade: mana recuperada (deve ser positiva).

        Returns:
            Mana resultante.

        Raises:
            ValorInvalidoError: se ``quantidade`` for menor ou igual a zero.
        """
        if quantidade <= 0:
            raise ValorInvalidoError("a mana recuperada deve ser maior que zero")
        self._mana += quantidade
        return self._mana


class Arqueiro(Personagem):
    """Atirador: soma a precisão ao poder de ataque."""

    def __init__(self, nome: str) -> None:
        """Cria um arqueiro com vida 95, força 15, defesa 8 e precisão 6."""
        super().__init__(nome, vida=95, forca=15, defesa=8)
        self._precisao = 6

    @property
    def precisao(self) -> int:
        """Precisão somada ao ataque."""
        return self._precisao

    def atacar(self, alvo: Personagem) -> int:
        """Tiro preciso: força + bônus de arma + precisão."""
        self._validar_ataque(alvo)
        return self._forca + self._bonus_ataque + self._precisao
