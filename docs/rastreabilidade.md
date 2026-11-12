# Rastreabilidade — conceito da aula → classe → teste

Este é o documento de conferência: para cada exigência de `regras.md` e para cada aula
do portal da disciplina, existe **código** e **teste executável**.

Comandos de prova:

```bash
python -m unittest discover -s testes -v     # todos os testes
python demo.py                               # demonstração no console
```

---

## 1. Exigências de `regras.md`

| # | Exigência | Onde está implementado | Teste que prova |
|---|---|---|---|
| 1 | **Classes e Objetos** — personagens, itens e cenários | `personagem.py`, `itens.py`, `cenario.py` | `test_personagem.py::test_guerreiro_ataca_com_forca_dobrada` |
| 2 | **Atributos, Métodos e Interação** — vida/força/defesa + atacar/defender/usar item | `personagem.py` (atributos e `atacar`/`receber_dano`/`usar_item`) | `test_personagem.py::test_atacar_interage_com_receber_dano` |
| 3 | **Abstração** — classe que não pode ser instanciada | `Personagem(ABC)`, `Item(ABC)`, `Cenario(ABC)` | `test_personagem.py::test_personagem_abstrata_nao_pode_ser_instanciada`, `test_itens.py::test_item_abstrato_nao_pode_ser_instanciado` |
| 4 | **Interface** — contrato `Combatente.atacar()` | `interfaces.py` | `test_combate.py::test_combate_rejeita_nao_combatente` |
| 5 | **Herança** — Guerreiro/Mago/Arqueiro de Personagem | `personagem.py` | `test_personagem.py::test_subclasses_sao_personagens` |
| 6 | **Tratamento de Exceções** — dano inválido, vida negativa, item inexistente | `excecoes.py` + `raise` no domínio | `test_excecoes.py` (4 testes) |
| 7 | **Agregação** — Personagem em Grupo/Guilda sobrevive ao grupo | `grupo.py` | `test_grupo.py::test_personagem_sobrevive_ao_grupo` |
| 8 | **Composição** — Inventario e FichaDeStatus nascem com o Personagem | `inventario.py`, `ficha.py`, construtor de `personagem.py` | `test_personagem.py::test_personagem_cria_ficha_e_inventario` |
| 9 | **Consumo de classe** — quem usa os métodos de quem | tabela em `visao-de-projeto.md` §4; `combate.py` | `test_combate.py::test_combate_aplica_bonus_do_cenario` |
| 10 | **Ambiente que favorece o usuário** — Floresta/Caverna/Castelo com vantagem | `cenario.py` | `test_cenario.py` (6 testes) |
| 11 | **Sem back-end / sem front-end / sem gráfico** | apenas `input()`/`print()` em `cli.py`, `demo.py` | inspeção + `test_cli.py` |

---

## 2. Conceitos das aulas 01–09

| Aula | Tema | Arquivo | Evidência concreta |
|---|---|---|---|
| 01 | Conceitos e paradigmas | `docs/visao-de-projeto.md` §2 | arquitetura em 2 camadas, ADRs |
| 02 | Classes e objetos, construtor, instância | `personagem.py`, `itens.py` | `Guerreiro("Aragorn")` cria objeto com estado próprio |
| 03 | Atributos, métodos, passagem de mensagem | `personagem.atacar()` → `alvo.receber_dano()` | teste de interação entre dois objetos |
| 04 | Sintaxe e vocabulário (composição/agregação/consumo) | `grupo.py`, `inventario.py`, `combate.py` | diagrama + testes de ciclo de vida |
| 05 | Abstração (`ABC`, métodos abstratos) | `personagem.py`, `itens.py`, `cenario.py` | `TypeError` ao instanciar a base |
| 06 | Interfaces, polimorfismo, duck typing, segregação | `interfaces.py`, `combate.py`, `aldeao.py` | `Aldeao` recusado; `isinstance(x, Combatente)` |
| 07 | Agregação × composição, UML | `grupo.py`, `ficha.py`, `inventario.py` | testes de ciclo de vida + Mermaid |
| 08 | Herança, overriding, exceções personalizadas | `personagem.py`, `excecoes.py` | `atacar()` sobrescrito nas 3 subclasses; 11 exceções |
| 09 | Testes (`unittest`, AAA) | `testes/` | 122 testes Arrange-Act-Assert |

---

## 3. Mapa das exceções de domínio

| Exceção | Disparada quando | Teste |
|---|---|---|
| `ValorInvalidoError` | nome vazio, bônus negativo, XP negativo, objeto inválido | `test_personagem.py::test_nome_vazio_lanca_excecao`, `test_ficha_inventario.py::test_xp_negativo_lanca_excecao` |
| `VidaInvalidaError` | vida inicial ≤ 0 | `test_personagem.py::test_vida_inicial_invalida_lanca_excecao` |
| `DanoInvalidoError` | `receber_dano(0)` ou negativo | `test_personagem.py::test_receber_dano_invalido_lanca_excecao` |
| `ItemNaoEncontradoError` | item ausente no inventário | `test_ficha_inventario.py::test_inventario_busca_inexistente` |
| `GrupoCheioError` | sexto membro | `test_grupo.py::test_grupo_limite_cinco` |
| `AlvoInvalidoError` | alvo que não é `Personagem`/`Combatente`, duplicado | `test_grupo.py::test_grupo_rejeita_objeto_invalido` |
| `PersonagemMortoError` | agir com vida 0 | `test_personagem.py::test_personagem_morto_nao_ataca` |
| `SemManaError` | mago ataca com mana < 5 | `test_personagem.py::test_mago_sem_mana_lanca_excecao` |
| `CenarioInvalidoError` | opção de cenário inexistente | `test_cenario.py::test_criar_cenario_opcao_invalida` |
| `CombateInfinitoError` | estourou `max_turnos` | `test_combate.py::test_combate_infinito_lanca_excecao` |

---

## 4. Como demonstrar em 30 segundos

```bash
python demo.py
```

O roteiro imprime, na ordem:

1. `Personagem()` direto → `TypeError` (abstração).
2. Criação de Guerreiro, Mago e Arqueiro (herança + construtores).
3. Ficha e inventário nascendo junto (composição).
4. Poção usada e consumida (polimorfismo de `Item`).
5. Grupo com os três e dissolução, com personagens intactos (agregação).
6. Bônus de cada cenário: Floresta→Arqueiro, Caverna→Guerreiro, Castelo→Mago.
7. Combate Guerreiro × Mago na Caverna, com log turno a turno e XP do vencedor.
8. `Aldeao` sendo recusado em combate (interface).
9. Cada exceção de domínio capturada e exibida.
