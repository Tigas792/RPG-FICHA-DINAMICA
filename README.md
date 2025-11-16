# **RPG**
---
### Projeto de ficha dinamica de RPG
---
Sobre o projeto:
 Ficha para suporte na jogabilidade de qualquer tipo de **RPG**, facilitando para jogadores que não tem dados apropriados para o jogo.
	
Sistemas que calculam automaticamente o sucesso do jogador em qualquer tipo de teste, os classificando em:

| Tipos de resultado | relativo | Número do dado |
|---|---|---|
| Desastre | == | 1 |
| Normal | >= | péricia |
| Bom | >= | 1/2 da perícia |
| Extremo | >= | 1/5 da perícia |

Logicamente quanto maior o número do dado, melhores serão os tipos de resultados.

Mais informações [aqui](https://www.youtube.com/watch?v=3L3dY1zBO3c)

Bases para criação dos Icons do personagem do usuário nos formatos .psd .mdp e .png

![Base do personagem](https://cdn.discordapp.com/attachments/601118494527848498/800105691049230406/face_base_rpg.png)

Interface dinâmica e totalmente personalizavel para agrado do úsuario.

![Interface](https://cdn.discordapp.com/attachments/601118494527848498/817618601980067870/unknown.png)

## Agenda ponderada em linha de comando

Além da aplicação principal, o repositório agora inclui um utilitário simples
para organizar atividades diárias com pesos/prioridades. O script
`scripts/weighted_agenda.py` mantém um arquivo `files/weighted_agenda.json`
(ou qualquer outro caminho apontado pela variável de ambiente
`WEIGHTED_AGENDA_FILE`) com todas as tarefas, sempre reordenando o dia atual
para que os itens de peso maior apareçam primeiro e adiando automaticamente as
atividades que ficaram pendentes.

### Como usar

```bash
# Adiciona uma atividade para hoje com peso 5
python3 scripts/weighted_agenda.py add "Revisar personagem" 5

# Lista o dia atual (já com tarefas remanescentes de dias anteriores movidas)
python3 scripts/weighted_agenda.py list

# Marca uma atividade como concluída
python3 scripts/weighted_agenda.py done 1

# Opcional: adia manualmente uma tarefa específica em 2 dias
python3 scripts/weighted_agenda.py postpone 1 --days 2

# Ajusta peso, descrição e/ou data caso tenha mudado de ideia
python3 scripts/weighted_agenda.py edit 1 --weight 8 --date 2024-02-10

# Remove definitivamente uma entrada
python3 scripts/weighted_agenda.py remove 1
```

Use `python3 scripts/weighted_agenda.py list --all` para visualizar toda a
agenda ordenada por peso independentemente da data agendada. Para manter os
dados em outro local (por exemplo, fora do repositório), defina
`WEIGHTED_AGENDA_FILE=/caminho/para/agenda.json` antes de executar qualquer
comando.
