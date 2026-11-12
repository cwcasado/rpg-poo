"""Exceções de domínio do RPG.

Toda falha de regra de negócio herda de :class:`RPGError`, o que permite à camada de
console capturar apenas erros do domínio — sem mascarar bugs de programação
(``TypeError``, ``AttributeError`` etc.).

Aula 08 — Herança e tratamento de exceções.
"""


class RPGError(Exception):
    """Erro base do domínio do RPG.

    Example:
        >>> try:
        ...     raise DanoInvalidoError("dano deve ser positivo")
        ... except RPGError as erro:
        ...     print(erro)
        dano deve ser positivo
    """


class ValorInvalidoError(RPGError):
    """Valor de entrada inválido (nome vazio, bônus negativo, XP negativo)."""


class VidaInvalidaError(RPGError):
    """Vida inicial menor ou igual a zero."""


class DanoInvalidoError(RPGError):
    """Dano (ou cura) menor ou igual a zero."""


class ItemNaoEncontradoError(RPGError):
    """Item procurado não existe no inventário."""


class GrupoCheioError(RPGError):
    """Tentativa de adicionar um sexto membro a um grupo de cinco."""


class AlvoInvalidoError(RPGError):
    """Alvo que não é personagem, não é combatente ou já está no grupo."""


class PersonagemMortoError(RPGError):
    """Ação tentada por ou contra um personagem com vida zero."""


class SemManaError(RPGError):
    """Mago sem mana suficiente para conjurar o ataque."""


class CenarioInvalidoError(RPGError):
    """Opção de cenário inexistente."""


class CombateInfinitoError(RPGError):
    """O combate excedeu o número máximo de turnos permitido."""
