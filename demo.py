"""Demonstração roteirizada — cada conceito de POO em execução.

Execute com::

    python demo.py

O roteiro é determinístico: mesma saída a cada execução, sem `input()`.
"""

from rpg.aldeao import Aldeao
from rpg.cenario import Castelo, Caverna, Cenario, Floresta, criar_cenario
from rpg.combate import Combate
from rpg.excecoes import (
    AlvoInvalidoError,
    CenarioInvalidoError,
    GrupoCheioError,
    ItemNaoEncontradoError,
    RPGError,
    VidaInvalidaError,
)
from rpg.grupo import Grupo
from rpg.itens import Arma, Armadura, Item, Pocao
from rpg.personagem import Arqueiro, Guerreiro, Mago, Personagem


def titulo(numero: int, texto: str) -> None:
    """Imprime o cabeçalho de uma seção."""
    print()
    print("=" * 70)
    print(f"{numero}. {texto}")
    print("=" * 70)


def demonstrar_abstracao() -> None:
    """Aula 05 — classes abstratas não podem ser instanciadas."""
    titulo(1, "ABSTRACAO — Personagem, Item e Cenario sao abstratas")
    for classe, argumentos in (
        (Personagem, ("Fantasma", 10, 10, 10)),
        (Item, ("Item genérico",)),
        (Cenario, ("Planície", Guerreiro)),
    ):
        try:
            classe(*argumentos)  # type: ignore[abstract]
        except TypeError:
            print(f"  {classe.__name__}() -> TypeError: classe abstrata, nao instanciavel.")

    print("  Só as subclasses concretas existem: Guerreiro, Mago, Arqueiro,")
    print("  Pocao, Arma, Armadura, Floresta, Caverna e Castelo.")


def demonstrar_classes_e_objetos() -> tuple[Guerreiro, Mago, Arqueiro]:
    """Aulas 02/03 — objetos com estado próprio."""
    titulo(2, "CLASSES E OBJETOS — tres instancias, tres estados")
    guerreiro = Guerreiro("Aragorn")
    mago = Mago("Gandalf")
    arqueiro = Arqueiro("Legolas")
    for personagem in (guerreiro, mago, arqueiro):
        print(f"  {personagem.resumo()}")
    print("  Cada objeto tem vida, força, defesa, ficha e inventário próprios.")
    return guerreiro, mago, arqueiro


def demonstrar_composicao(guerreiro: Guerreiro, mago: Mago) -> None:
    """Aula 07 — ficha e inventário nascem com o personagem."""
    titulo(3, "COMPOSICAO — FichaDeStatus e Inventario nascem com o Personagem")
    print(f"  ficha do guerreiro .......... {id(guerreiro.ficha)}")
    print(f"  ficha do mago ............... {id(mago.ficha)}")
    print(f"  inventario do guerreiro ..... {id(guerreiro.inventario)}")
    print(f"  inventario do mago .......... {id(mago.inventario)}")
    print("  Objetos distintos: não há compartilhamento. Morrendo o dono, as partes somem.")


def demonstrar_itens(guerreiro: Guerreiro) -> None:
    """Aula 05/08 — polimorfismo: mesma mensagem, efeitos diferentes."""
    titulo(4, "POLIMORFISMO — item.usar(personagem)")
    guerreiro.receber_dano(60)
    print(f"  vida antes: {guerreiro.vida}/{guerreiro.vida_maxima}")

    pocao = Pocao("Poção de Vida", 30)
    arma = Arma("Andúril", 7)
    armadura = Armadura("Cota de Mithril", 5)
    for item in (pocao, arma, armadura):
        guerreiro.inventario.adicionar(item)
        print(f"  {guerreiro.usar_item(item.nome)}")

    print(f"  vida depois: {guerreiro.vida}/{guerreiro.vida_maxima}")
    print(f"  bônus de ataque: +{guerreiro.bonus_ataque} | defesa: +{guerreiro.bonus_defesa}")
    print(f"  inventário: {guerreiro.inventario} (a poção foi consumida)")


def demonstrar_agregacao(guerreiro: Guerreiro, mago: Mago, arqueiro: Arqueiro) -> None:
    """Aula 07 — o grupo referencia; não é dono."""
    titulo(5, "AGREGACAO — Grupo nao destrói os personagens")
    grupo = Grupo("Companhia do Anel")
    for personagem in (guerreiro, mago, arqueiro):
        grupo.adicionar(personagem)
    print(f"  {grupo.resumo()}")

    removido = grupo.remover("Gandalf")
    print(f"  removido do grupo: {removido.nome}")
    print(f"  {removido.nome} continua vivo: {removido.esta_vivo()} | vida {removido.vida}")
    del grupo
    print("  grupo dissolvido; os três personagens continuam existindo.")


def demonstrar_cenarios() -> None:
    """Aula 04/06 + RN06 — ambiente que favorece um tipo."""
    titulo(6, "CENARIO — o ambiente favorece um tipo (+20%)")
    pessoas = (Guerreiro("Aragorn"), Mago("Gandalf"), Arqueiro("Legolas"))
    for cenario in (Floresta(), Caverna(), Castelo()):
        print(f"  {cenario.descricao()}")
        for pessoa in pessoas:
            bonus = cenario.bonus_para(pessoa)
            marca = "FAVORECIDO" if bonus else "-"
            print(f"    {pessoa.nome:<10} {pessoa.tipo:<10} +{bonus:.0%}  {marca}")


def demonstrar_combate() -> None:
    """Aula 03/06/08 — combate por turnos com bônus de cenário."""
    titulo(7, "COMBATE — consumo de classe, turnos e XP")
    guerreiro = Guerreiro("Aragorn")
    mago = Mago("Gandalf")
    cenario = Caverna()  # favorece Guerreiro

    combate = Combate(guerreiro, mago, cenario)
    print(f"  {combate}")
    print(f"  bônus do cenário para {guerreiro.nome}: +{cenario.bonus_para(guerreiro):.0%}")
    print(f"  bônus do cenário para {mago.nome}: +{cenario.bonus_para(mago):.0%}")

    resultado = combate.executar()
    print("  --- log ---")
    for registro in resultado.log:
        print(f"  {registro.descricao()}")
    print(f"  {resultado.resumo()}")
    print(f"  ficha do vencedor: {resultado.vencedor.nome} - {resultado.vencedor.ficha.resumo()}")


def demonstrar_interface() -> None:
    """Aula 06 — quem não implementa Combatente não entra na arena."""
    titulo(8, "INTERFACE — Combatente tem contrato, Aldeao nao")
    aldeao = Aldeao("Tobias")
    print(f"  {aldeao.falar()}")
    try:
        Combate(aldeao, Guerreiro("Aragorn"), Caverna())  # type: ignore[arg-type]
    except AlvoInvalidoError as erro:
        print(f"  Combate recusou o aldeao: {erro}")


def demonstrar_excecoes(guerreiro: Guerreiro) -> None:
    """Aula 08 — cada erro de domínio tem tipo próprio."""
    titulo(9, "EXCECOES — erros do dominio, todos filhos de RPGError")
    casos = (
        ("vida inicial invalida", lambda: Personagem.__init__(guerreiro, "X", 0, 10, 10)),
        ("item inexistente", lambda: guerreiro.usar_item("Machado")),
        ("dano invalido", lambda: guerreiro.receber_dano(0)),
        ("cenario inexistente", lambda: criar_cenario("deserto")),
        ("alvo invalido", lambda: guerreiro.atacar("dragão")),
    )
    for descricao, acao in casos:
        try:
            acao()
        except RPGError as erro:
            print(f"  {descricao:<24} -> {type(erro).__name__}: {erro}")

    grupo = Grupo("Cheio")
    for nome in ("A", "B", "C", "D", "E"):
        grupo.adicionar(Guerreiro(nome))
    try:
        grupo.adicionar(Guerreiro("F"))
    except GrupoCheioError as erro:
        print(f"  {'grupo cheio':<24} -> {type(erro).__name__}: {erro}")


def main() -> None:
    """Executa o roteiro completo."""
    print("SISTEMA DE RPG EM CONSOLE - DEMONSTRACAO DE POO")
    print("Cada seção abaixo corresponde a um conceito exigido no trabalho.")

    demonstrar_abstracao()
    guerreiro, mago, arqueiro = demonstrar_classes_e_objetos()
    demonstrar_composicao(guerreiro, mago)
    demonstrar_itens(guerreiro)
    demonstrar_agregacao(guerreiro, mago, arqueiro)
    demonstrar_cenarios()
    demonstrar_combate()
    demonstrar_interface()
    demonstrar_excecoes(guerreiro)

    print()
    print("FIM — execute 'python -m rpg' para o menu interativo.")
    print("Testes: python -m unittest discover -s testes -v")


if __name__ == "__main__":
    main()
