# RPG POO — sistema de RPG em console

Trabalho da disciplina de **Programação Orientada a Objetos** (Univassouras).
Sistema de RPG **sem interface gráfica e sem back-end**: tudo roda no terminal e serve
para demonstrar, em execução, **todos os conceitos de POO vistos em aula**.

> Enunciado original: [`regras.md`](regras.md)

## O que o sistema faz

- Cria personagens (`Guerreiro`, `Mago`, `Arqueiro`) a partir de uma classe **abstrata**.
- Cada personagem nasce com **ficha de status** e **inventário** próprios (composição).
- Gerencia itens (`Poção`, `Arma`, `Armadura`) com efeitos polimórficos.
- Monta **grupos** que agregam personagens (os personagens sobrevivem ao grupo).
- Escolhe um **cenário** que concede +20% ao tipo favorecido:
  **Floresta → Arqueiro**, **Caverna → Guerreiro**, **Castelo → Mago**.
- Resolve **combates por turnos**, com defesa, mana, limite de turnos e XP.
- Valida tudo com **exceções de domínio** próprias.

## Documentação

| Documento | Conteúdo |
|---|---|
| [`docs/caso-de-uso.md`](docs/caso-de-uso.md) | atores, 8 casos de uso, fluxos alternativos, regras de negócio |
| [`docs/visao-de-projeto.md`](docs/visao-de-projeto.md) | arquitetura, classes, atributos/métodos, consumo de classe, ADRs |
| [`docs/diagrama-de-classes.md`](docs/diagrama-de-classes.md) | UML em Mermaid + ASCII, multiplicidades, justificativa de cada relação |
| [`docs/rastreabilidade.md`](docs/rastreabilidade.md) | conceito da aula → arquivo → teste que prova |

## Requisitos

- Python **3.10+** (testado em 3.13)
- Nenhuma dependência externa

## Como executar

```bash
# menu interativo no terminal
python -m rpg

# demonstração roteirizada (mostra cada conceito em ação)
python demo.py

# testes
python -m unittest discover -s testes -v
```

## Estrutura

```
rpg/
├── excecoes.py      hierarquia de erros de domínio
├── interfaces.py    contrato Combatente
├── itens.py         Item (abstrata) + Pocao, Arma, Armadura
├── ficha.py         FichaDeStatus (composição)
├── inventario.py    Inventario (composição)
├── personagem.py    Personagem (abstrata) + Guerreiro, Mago, Arqueiro
├── aldeao.py        objeto que NÃO é combatente
├── grupo.py         Grupo (agregação)
├── cenario.py       Cenario (abstrata) + Floresta, Caverna, Castelo
├── combate.py       orquestração de turnos (consumo de classe)
├── cli.py           menu de console
└── __main__.py      python -m rpg
testes/              unittest, padrão Arrange-Act-Assert
docs/                modelagem
demo.py              demonstração executável
```

## Conceitos e onde estão

| Conceito | Arquivo | Prova |
|---|---|---|
| Classes e objetos | `personagem.py`, `itens.py`, `cenario.py` | testes de criação |
| Atributos, métodos e interação | `personagem.atacar()` → `alvo.receber_dano()` | `test_atacar_interage_com_receber_dano` |
| Abstração | `Personagem`, `Item`, `Cenario` com `ABC` | `test_personagem_abstrata_nao_pode_ser_instanciada` |
| Interface | `Combatente` | `test_combate_rejeita_nao_combatente` |
| Herança e overriding | `Guerreiro`, `Mago`, `Arqueiro` | `test_subclasses_sao_personagens` |
| Exceções | `excecoes.py` | `test_excecoes.py` |
| Agregação | `Grupo` | `test_personagem_sobrevive_ao_grupo` |
| Composição | `FichaDeStatus`, `Inventario` | `test_personagem_cria_ficha_e_inventario` |
| Consumo de classe | `Combate`, `Cenario` | `test_combate_aplica_bonus_do_cenario` |
| Ambiente favorece tipo | `cenario.py` | `test_cenario.py` |
| Testes (A09) | `testes/` | `python -m unittest` |

## Status das etapas

| Etapa | Entrega | Situação |
|---|---|---|
| 1 | Modelagem (caso de uso, visão, diagrama, rastreabilidade) | concluída |
| 2 | Fundação (exceções, interface, itens, ficha, inventário) | em andamento |
| 3 | Personagens (abstrata + subclasses) | pendente |
| 4 | Grupo e cenário | pendente |
| 5 | Combate | pendente |
| 6 | CLI, demo, README e validação final | pendente |
