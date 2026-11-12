"""Combate — orquestração de turnos e consumo de classe.

Aula 03 — Interação: o combate só envia mensagens; quem calcula o golpe é o
personagem (``atacar``) e quem aplica o dano é o alvo (``receber_dano``).
Aula 06 — Interface: só entra quem realiza :class:`~rpg.interfaces.Combatente`.
Aula 08 — Exceções: alvo inválido, morto, combate infinito.

Este módulo é a evidência do **consumo de classe** exigido pelo trabalho:
``Combate`` consome ``Combatente``, ``Cenario``, ``Item``, ``FichaDeStatus`` e
``Personagem`` — a relação de uso está explícita nos imports e nas chamadas.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from rpg.cenario import Cenario
from rpg.excecoes import (
    AlvoInvalidoError,
    CenarioInvalidoError,
    CombateInfinitoError,
    PersonagemMortoError,
    ValorInvalidoError,
)
from rpg.interfaces import Combatente
from rpg.itens import Pocao
from rpg.personagem import Personagem


@dataclass(frozen=True)
class RegistroTurno:
    """Uma linha do log de combate.

    Attributes:
        numero: ordem do turno (1, 2, 3...).
        atacante: nome de quem atacou.
        defensor: nome de quem recebeu o golpe.
        poder: poder bruto devolvido por ``atacar()``.
        bonus: bônus de cenário aplicado (0.20 = +20%).
        dano: dano efetivamente aplicado após defesa.
        vida_restante: vida do defensor depois do golpe.
    """

    numero: int
    atacante: str
    defensor: str
    poder: int
    bonus: float
    dano: int
    vida_restante: int

    def descricao(self) -> str:
        """Texto legível do turno."""
        bonus_txt = f" x{1 + self.bonus:.2f}" if self.bonus else ""
        return (
            f"Turno {self.numero}: {self.atacante} ataca {self.defensor} "
            f"(poder {self.poder}{bonus_txt}) -> {self.dano} de dano | "
            f"vida de {self.defensor}: {self.vida_restante}"
        )


@dataclass(frozen=True)
class ResultadoCombate:
    """Resultado final de um combate resolvido."""

    vencedor: Personagem
    perdedor: Personagem
    cenario: Cenario
    turnos: int
    xp_concedido: int
    log: tuple[RegistroTurno, ...] = field(default_factory=tuple)

    def resumo(self) -> str:
        """Texto com vencedor, cenário e duração."""
        return (
            f"{self.vencedor.nome} ({self.vencedor.tipo}) venceu "
            f"{self.perdedor.nome} ({self.perdedor.tipo}) em {self.turnos} turnos "
            f"no cenário {self.cenario.nome} — +{self.xp_concedido} XP."
        )


class Combate:
    """Resolve a luta entre dois ``Combatente`` dentro de um ``Cenario``.

    Attributes:
        XP_VITORIA: experiência entregue ao vencedor.
        MAX_TURNOS: limite de turnos antes de considerar o combate infinito.

    Example:
        >>> combate = Combate(Guerreiro("Aragorn"), Mago("Gandalf"), Caverna())
        >>> resultado = combate.executar()
        >>> resultado.vencedor.nome
        'Aragorn'
    """

    XP_VITORIA: int = 100
    MAX_TURNOS: int = 50

    def __init__(
        self,
        combatente_a: Combatente,
        combatente_b: Combatente,
        cenario: Cenario,
    ) -> None:
        """Valida os participantes e guarda o cenário.

        Args:
            combatente_a: primeiro participante.
            combatente_b: segundo participante.
            cenario: cenário que concede bônus ao tipo favorecido.

        Raises:
            AlvoInvalidoError: participante que não realiza ``Combatente``,
                que não é ``Personagem`` ou que é o mesmo objeto dos dois lados.
            PersonagemMortoError: participante com vida zero.
            CenarioInvalidoError: objeto que não é ``Cenario``.
        """
        if not isinstance(combatente_a, Combatente) or not isinstance(
            combatente_b, Combatente
        ):
            raise AlvoInvalidoError(
                "só quem implementa o contrato Combatente participa de combate"
            )
        if not isinstance(combatente_a, Personagem) or not isinstance(
            combatente_b, Personagem
        ):
            raise AlvoInvalidoError("os combatentes precisam ser personagens completos")
        if combatente_a is combatente_b:
            raise AlvoInvalidoError("um personagem não pode lutar contra si mesmo")
        if not combatente_a.esta_vivo() or not combatente_b.esta_vivo():
            raise PersonagemMortoError("nenhum combatente pode entrar morto na arena")
        if not isinstance(cenario, Cenario):
            raise CenarioInvalidoError("informe um cenário válido para o combate")

        self._combatente_a = combatente_a
        self._combatente_b = combatente_b
        self._cenario = cenario
        self._log: list[RegistroTurno] = []

    @property
    def combatente_a(self) -> Combatente:
        """Primeiro participante."""
        return self._combatente_a

    @property
    def combatente_b(self) -> Combatente:
        """Segundo participante."""
        return self._combatente_b

    @property
    def cenario(self) -> Cenario:
        """Cenário do combate."""
        return self._cenario

    @property
    def log(self) -> list[RegistroTurno]:
        """Cópia do log de turnos já executados."""
        return list(self._log)

    def executar_turno(
        self, atacante: Personagem, defensor: Personagem, numero: int | None = None
    ) -> RegistroTurno:
        """Executa um golpe: bônus de cenário, ataque e dano.

        Args:
            atacante: quem ataca.
            defensor: quem recebe.
            numero: número do turno (padrão: próximo do log).

        Returns:
            Registro do turno.

        Raises:
            AlvoInvalidoError: participante que não é personagem/combatente.
        """
        if not isinstance(atacante, Combatente) or not isinstance(defensor, Combatente):
            raise AlvoInvalidoError("participante não cumpre o contrato Combatente")

        bonus = self._cenario.bonus_para(atacante)
        poder = atacante.atacar(defensor)
        poder_com_bonus = int(round(poder * (1 + bonus)))
        dano = defensor.receber_dano(poder_com_bonus)

        registro = RegistroTurno(
            numero=numero if numero is not None else len(self._log) + 1,
            atacante=atacante.nome,
            defensor=defensor.nome,
            poder=poder,
            bonus=bonus,
            dano=dano,
            vida_restante=defensor.vida,
        )
        self._log.append(registro)
        return registro

    def executar(self, max_turnos: int | None = None) -> ResultadoCombate:
        """Alterna turnos até um combatente morrer.

        Args:
            max_turnos: limite de turnos (padrão: :attr:`MAX_TURNOS`).

        Returns:
            Resultado com vencedor, perdedor, log e XP concedido.

        Raises:
            ValorInvalidoError: ``max_turnos`` menor ou igual a zero.
            CombateInfinitoError: ninguém morreu dentro do limite.
        """
        limite = self.MAX_TURNOS if max_turnos is None else max_turnos
        if limite <= 0:
            raise ValorInvalidoError("o limite de turnos deve ser maior que zero")

        atacante: Personagem = self._combatente_a  # type: ignore[assignment]
        defensor: Personagem = self._combatente_b  # type: ignore[assignment]

        for numero in range(1, limite + 1):
            self.executar_turno(atacante, defensor, numero)
            if not defensor.esta_vivo():
                vencedor, perdedor = atacante, defensor
                break
            atacante, defensor = defensor, atacante
        else:
            raise CombateInfinitoError(
                f"o combate passou de {limite} turnos sem um vencedor"
            )

        vencedor.ficha.ganhar_xp(self.XP_VITORIA)
        return ResultadoCombate(
            vencedor=vencedor,
            perdedor=perdedor,
            cenario=self._cenario,
            turnos=numero,
            xp_concedido=self.XP_VITORIA,
            log=tuple(self._log),
        )

    def usar_pocao(self, combatente: Personagem, nome: str) -> str:
        """Consome uma poção do inventário durante o combate.

        Args:
            combatente: personagem que usa a poção.
            nome: nome da poção.

        Returns:
            Mensagem do efeito.

        Raises:
            AlvoInvalidoError: se ``combatente`` não for personagem.
            ValorInvalidoError: se o item não for uma poção.
            ItemNaoEncontradoError: se o item não estiver no inventário.
        """
        if not isinstance(combatente, Personagem):
            raise AlvoInvalidoError("apenas personagens podem usar poções")
        item = combatente.inventario.buscar(nome)
        if not isinstance(item, Pocao):
            raise ValorInvalidoError(f"{nome} não é uma poção")
        return combatente.usar_item(nome)

    def __str__(self) -> str:
        return (
            f"Combate: {self._combatente_a.nome} x {self._combatente_b.nome} "
            f"no cenário {self._cenario.nome}"
        )
