# RPG API 

API RESTful assíncrona de RPG construída com **FastAPI** e **SQLite**, com autenticação via **JWT**. O sistema de batalha é baseado no projeto `RPG_OOP.py`, com inimigos escalados por nível, sistema de loot, inventário e morte permanente.

---

## Tecnologias

- Python 3.14
- FastAPI
- SQLite + SQLAlchemy + databases
- PyJWT
- Pydantic v2
- Uvicorn

---

## Instalação

```bash
# Instalar dependências com Poetry
poetry add fastapi uvicorn databases sqlalchemy aiosqlite PyJWT pydantic

# Rodar o servidor
poetry run uvicorn main:app --reload
```

> O banco de dados `rpg.db` é criado automaticamente na primeira execução.

Coloque o arquivo `RPG_OOP.py` na raiz do projeto junto com o `main.py`.

---

## Estrutura do Projeto

```
rpg_api/
├── main.py
├── database.py
├── security.py
├── RPG_OOP.py
├── controllers/
│   ├── auth.py
│   ├── player.py
│   ├── battle.py
│   └── inventory_ctrl.py
├── models/
│   ├── player.py
│   ├── battle.py
│   └── inventory.py
├── schemas/
│   ├── player.py
│   ├── battle.py
│   └── inventory.py
├── services/
│   ├── player.py
│   ├── battle.py
│   └── inventory.py
└── views/
    ├── player.py
    ├── battle.py
    └── inventory.py
```

---

## Autenticação

A API usa **JWT Bearer Token**. Para acessar endpoints protegidos, inclua o header:

```
Authorization: Bearer <seu_token>
```

O token é obtido no endpoint `/auth/login` e expira em **30 minutos**.

---

## Endpoints

###  Auth — sem token necessário

#### `POST /auth/register`
Cria um novo personagem com nome único.

**Body:**
```json
{ "name": "Player" }
```

**Resposta:**
```json
{
  "id": 1,
  "name": "Player",
  "health": 100,
  "damage": 10,
  "critical": 5,
  "defense": 0,
  "level": 1,
  "coins": 0,
  "victories": 0,
  "weapon_name": null,
  "armor_name": null
}
```

---

#### `POST /auth/login`
Recebe o ID do personagem e retorna o token de acesso.

**Body:**
```json
{ "player_id": 1 }
```

**Resposta:**
```json
{ "access_token": "exemployJhbGciOiJIUzI1NiIs..." }
```

---

### 👤 Players

#### `GET /players/`
Lista todos os personagens ordenados por nível (ranking).

#### `GET /players/me` 
Retorna os dados do personagem autenticado.

#### `GET /players/{player_id}`
Retorna os dados de qualquer personagem pelo ID.

#### `POST /players/revive` 
Ressuscita o personagem após uma derrota, restaurando o HP para 100.
Só funciona se o personagem estiver morto (HP = 0).

---

###  Battle 

#### `POST /battle/start`
Inicia uma batalha contra um inimigo aleatório escalado ao nível do personagem.

**Resposta:**
```json
{
  "message": "Um Bandido apareceu!",
  "enemy_name": "Bandido",
  "enemy_health": 45,
  "enemy_damage": 12,
  "enemy_defense": 2,
  "player_health": 100
}
```

---

#### `POST /battle/action`
Executa uma ação na batalha ativa.

**Body:**
```json
{ "action": "attack" }
```
ou
```json
{ "action": "flee" }
```

**Resposta (vitória):**
```json
{
  "message": "Você derrotou Bandido! (+1 nível)",
  "player_health": 72,
  "enemy_health": 0,
  "result": "victory",
  "loot": ["Cachaça Roubada", "Palito de dente"],
  "level_up": true,
  "new_level": 2
}
```

O campo `result` pode ser: `ongoing`, `victory`, `defeat` ou `fled`.

---

#### `GET /battle/history`
Retorna o histórico de batalhas do personagem autenticado.

---

### Inventory 

#### `GET /inventory/`
Lista todos os itens do inventário do personagem.

**Resposta:**
```json
[
  {
    "id": 1,
    "item_name": "Espada Enferrujada",
    "item_type": "weapon",
    "rarity": "COMMON",
    "damage_bonus": 5,
    "crit_rate": 2,
    "defense_bonus": null,
    "heal": null,
    "equipped": false
  }
]
```

---

#### `POST /inventory/equip`
Equipa uma arma ou armadura. Desequipa automaticamente o item anterior do mesmo tipo.

**Body:**
```json
{ "item_id": 1 }
```

---

#### `POST /inventory/use`
Usa uma poção do inventário. O item é consumido após o uso.

**Body:**
```json
{ "item_id": 2 }
```

---

#### `DELETE /inventory/{item_id}`
Descarta um item do inventário. Se o item estiver equipado, o slot é limpo automaticamente.

---

## Como o RPG Funciona

### Personagem
Todo personagem começa com os atributos base:

| Atributo | Valor inicial |
|----------|--------------|
| HP | 100 |
| Dano | 10 |
| Crítico | 5% |
| Defesa | 0 |
| Nível | 1 |

### Batalha
- Cada vitória concede **+1 nível** ao personagem.
- O inimigo é sorteado aleatoriamente com força proporcional ao nível do jogador.
- A batalha é por turnos: você age primeiro, depois o inimigo contra-ataca.
- Fugir tem **40% de chance** de sucesso. Se falhar, o inimigo ataca.
- Só é possível ter **uma batalha ativa por vez**.

### Morte
- Ao ser derrotado, o personagem morre (HP = 0).
- Todo o inventário é perdido na morte.
- Equipamentos são removidos.
- Use `POST /players/revive` para ressuscitar com HP 100.

### Loot
- Ao derrotar inimigos, itens são dropados automaticamente para o inventário.
- Itens podem ser do tipo `weapon`, `armor` ou `potion`.
- Armas e armaduras podem ser equipadas via `POST /inventory/equip`.
- Poções são consumidas ao usar via `POST /inventory/use`.
- Itens indesejados podem ser descartados via `DELETE /inventory/{item_id}`.

### Documentação interativa
Com o servidor rodando, acesse:
```
http://localhost:8000/docs
```

### Notas
- É um sistema simples, porém foi meu caminho de aprendizado, aprendi muito com ele.
- Pretendo adicionar mais conteúdo no futuro, conforme vou evoluindo meu conhecimento, porém acredito que essa versão seja uma boa base simples para aprender e testar.
- Ele é meio dificil e pode ser desbalanceado, pretendo resolver isso no futuro.
