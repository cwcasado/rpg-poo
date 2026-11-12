"""Menu de console — camada de apresentação.

Aula 01 — visão geral do paradigma: a CLI apenas **orquestra** objetos do domínio;
nenhuma regra de negócio vive aqui. Também é a prova de RNF04: sem HTTP, sem
servidor, sem interface gráfica — só ``input()`` e ``print()``.

As funções de entrada e saída são injetáveis (``input_fn`` / ``print_fn``) para
permitir teste automatizado do fluxo de telas.
"""

from __future__ import annotations

import sys
from typing import Callable

from rpg.aldeao import Aldeao
from rpg.cenario import Cenario, criar_cenario
from rpg.combate import Combate
from rpg.excecoes import AlvoInvalidoError, CenarioInvalidoError, RPGError, ValorInvalidoError
from rpg.grupo import Grupo
from rpg.itens import Arma, Armadura, Item, Pocao
from rpg.personagem import Arqueiro, Guerreiro, Mago, Personagem

Entrada = Callable[[str], str]
Saida = Callable[[str], None]

MENU = """
=============== RPG POO ===============
1 - Criar personagem
2 - Listar personagens
3 - Ver ficha
4 - Adicionar item ao inventario
5 - Usar item
6 - Montar grupo
7 - Escolher cenario
8 - Iniciar combate
9 - Conversar com aldeao
0 - Sair
=======================================
"""

TIPOS: dict[str, type[Personagem]] = {
    "1": Guerreiro,
    "2": Mago,
    "3": Arqueiro,
}


class CLI:
    """Aplicação de console do RPG.

    Example:
        >>> cli = CLI(input_fn=lambda _: "0", print_fn=print)
        >>> cli.executar()
    """

    def __init__(self, input_fn: Entrada = input, print_fn: Saida = print) -> None:
        """Inicializa a CLI com as funções de entrada e saída.

        Args:
            input_fn: função de leitura (padrão: ``input``).
            print_fn: função de escrita (padrão: ``print``).
        """
        self._input = input_fn
        self._print = print_fn
        self.personagens: dict[str, Personagem] = {}
        self.grupos: dict[str, Grupo] = {}
        self.cenario: Cenario | None = None
        self.aldeao = Aldeao("Tobias")

    # ------------------------------------------------------------- infraestrutura

    def _ler(self, prompt: str) -> str:
        """Lê uma linha, sem espaços nas pontas."""
        return str(self._input(prompt)).strip()

    def _ler_inteiro(self, prompt: str) -> int:
        """Lê um inteiro, convertendo erro de digitação em erro de domínio."""
        texto = self._ler(prompt)
        try:
            return int(texto)
        except ValueError as erro:
            raise ValorInvalidoError(f"'{texto}' não é um número inteiro") from erro

    def _buscar_personagem(self, nome: str) -> Personagem:
        """Localiza um personagem pelo nome.

        Raises:
            ValorInvalidoError: se nenhum personagem foi criado.
            AlvoInvalidoError: se o nome não existir.
        """
        if not self.personagens:
            raise ValorInvalidoError("nenhum personagem criado ainda")
        procurado = nome.strip().casefold()
        for chave, personagem in self.personagens.items():
            if chave.casefold() == procurado:
                return personagem
        raise AlvoInvalidoError(f"personagem '{nome}' não existe")

    # ------------------------------------------------------------- loop principal

    def executar(self) -> None:
        """Executa o menu até o jogador escolher sair."""
        self._print(MENU)
        while True:
            opcao = self._ler("Escolha uma opção: ")
            if opcao == "0":
                break
            try:
                self._despachar(opcao)
            except RPGError as erro:
                self._print(f"[erro] {erro}")
            except (TypeError, ValueError) as erro:  # entrada malformada
                self._print(f"[erro] entrada inválida: {erro}")
        self._print("Até a próxima aventura!")

    def _despachar(self, opcao: str) -> None:
        """Direciona a opção do menu para o caso de uso correspondente."""
        acoes = {
            "1": self._criar_personagem,
            "2": self._listar_personagens,
            "3": self._ver_ficha,
            "4": self._adicionar_item,
            "5": self._usar_item,
            "6": self._montar_grupo,
            "7": self._escolher_cenario,
            "8": self._iniciar_combate,
            "9": self._conversar_com_aldeao,
        }
        acao = acoes.get(opcao)
        if acao is None:
            raise ValorInvalidoError(f"opção '{opcao}' não existe")
        acao()

    # ------------------------------------------------------------- casos de uso

    def _criar_personagem(self) -> None:
        """UC01 — cria Guerreiro, Mago ou Arqueiro."""
        tipo = self._ler("Tipo (1 Guerreiro, 2 Mago, 3 Arqueiro): ")
        if tipo not in TIPOS:
            raise AlvoInvalidoError(f"tipo '{tipo}' inválido")

        nome = self._ler("Nome do personagem: ")
        if any(chave.casefold() == nome.casefold() for chave in self.personagens):
            raise ValorInvalidoError(f"já existe um personagem chamado '{nome}'")

        personagem = TIPOS[tipo](nome)
        self.personagens[personagem.nome] = personagem
        self._print(f"[ok] {personagem.resumo()}")

    def _listar_personagens(self) -> None:
        """UC02 — lista todos os personagens criados."""
        if not self.personagens:
            self._print("Nenhum personagem criado ainda.")
            return
        self._print("Personagens:")
        for personagem in self.personagens.values():
            self._print(f"- {personagem.resumo()}")

    def _ver_ficha(self) -> None:
        """UC02 — mostra ficha, inventário e nível."""
        personagem = self._buscar_personagem(self._ler("Nome do personagem: "))
        self._print(personagem.resumo())
        self._print(f"Inventário: {personagem.inventario}")

    def _adicionar_item(self) -> None:
        """UC03 — cria um item e o entrega ao inventário do personagem."""
        personagem = self._buscar_personagem(self._ler("Nome do personagem: "))
        tipo = self._ler("Item (1 Poção, 2 Arma, 3 Armadura): ")
        nome_item = self._ler("Nome do item: ")

        item: Item
        if tipo == "1":
            cura = self._ler_inteiro("Cura da poção: ")
            item = Pocao(nome_item, cura)
        elif tipo == "2":
            bonus = self._ler_inteiro("Bônus de ataque: ")
            item = Arma(nome_item, bonus)
        elif tipo == "3":
            bonus = self._ler_inteiro("Bônus de defesa: ")
            item = Armadura(nome_item, bonus)
        else:
            raise AlvoInvalidoError(f"tipo de item '{tipo}' inválido")

        personagem.inventario.adicionar(item)
        self._print(f"[ok] {item.nome} guardado no inventário de {personagem.nome}.")

    def _usar_item(self) -> None:
        """UC04 — usa um item do inventário (polimorfismo de Item)."""
        personagem = self._buscar_personagem(self._ler("Nome do personagem: "))
        nome_item = self._ler("Nome do item: ")
        self._print(f"[ok] {personagem.usar_item(nome_item)}")
        self._print(f"Vida atual: {personagem.vida}/{personagem.vida_maxima}")

    def _montar_grupo(self) -> None:
        """UC05 — cria grupo e agrega/remove personagens."""
        nome_grupo = self._ler("Nome do grupo: ")
        grupo = self.grupos.get(nome_grupo)
        if grupo is None:
            grupo = Grupo(nome_grupo)
            self.grupos[grupo.nome] = grupo

        acao = self._ler("1 adicionar | 2 remover | 3 listar: ")
        if acao == "1":
            personagem = self._buscar_personagem(self._ler("Nome do personagem: "))
            grupo.adicionar(personagem)
            self._print(f"[ok] {personagem.nome} entrou no grupo {grupo.nome}.")
        elif acao == "2":
            removido = grupo.remover(self._ler("Nome do personagem: "))
            self._print(f"[ok] {removido.nome} saiu do grupo {grupo.nome}.")
        elif acao == "3":
            pass
        else:
            raise ValorInvalidoError(f"opção '{acao}' inválida")

        self._print(grupo.resumo())

    def _escolher_cenario(self) -> None:
        """UC06 — escolhe o ambiente que favorece um tipo."""
        self._print("1 Floresta (Arqueiro) | 2 Caverna (Guerreiro) | 3 Castelo (Mago)")
        self.cenario = criar_cenario(self._ler("Cenário: "))
        self._print(f"[ok] {self.cenario.descricao()}")

    def _iniciar_combate(self) -> None:
        """UC07 — resolve o combate e imprime o log."""
        if self.cenario is None:
            raise CenarioInvalidoError("escolha um cenário antes do combate")
        if len(self.personagens) < 2:
            raise AlvoInvalidoError("crie pelo menos dois personagens para lutar")

        primeiro = self._buscar_personagem(self._ler("Primeiro combatente: "))
        segundo = self._buscar_personagem(self._ler("Segundo combatente: "))

        combate = Combate(primeiro, segundo, self.cenario)

        if self._ler("Usar poção antes da luta? (s/n): ").casefold().startswith("s"):
            nome_pocao = self._ler("Nome da poção: ")
            self._print(f"[ok] {combate.usar_pocao(primeiro, nome_pocao)}")

        resultado = combate.executar()
        self._print("--- log do combate ---")
        for registro in resultado.log:
            self._print(f"  {registro.descricao()}")
        self._print(f"[fim] {resultado.resumo()}")

    def _conversar_com_aldeao(self) -> None:
        """UC08 — aldeão fala e não entra em combate."""
        self._print(self.aldeao.falar())


def main() -> None:
    """Ponto de entrada de ``python -m rpg``."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        pass
    CLI().executar()


if __name__ == "__main__":
    main()
