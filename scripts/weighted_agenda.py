#!/usr/bin/env python3
"""Command-line weighted agenda manager.

This tool lets you register activities with a weight/priority and keeps
reordering each day so the heavier tasks stay at the top.  Incomplete
activities are automatically postponed to the next planned day and will be
re-sorted alongside the existing tasks.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
from typing import Any, Dict, List

DATA_FILE = Path("files/weighted_agenda.json")


def _ensure_data_shape(data: Dict[str, Any]) -> Dict[str, Any]:
    data.setdefault("tasks", [])
    data.setdefault("next_id", 1)
    return data


def load_data() -> Dict[str, Any]:
    if not DATA_FILE.exists():
        return {"tasks": [], "next_id": 1}
    return _ensure_data_shape(json.loads(DATA_FILE.read_text(encoding="utf-8")))


def save_data(data: Dict[str, Any]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_date(date_str: str) -> _dt.date:
    return _dt.date.fromisoformat(date_str)


def format_date(date: _dt.date) -> str:
    return date.isoformat()


def rollover_tasks(data: Dict[str, Any], target_date: _dt.date) -> bool:
    """Move every unfinished task scheduled before ``target_date`` to that day.

    Returns True when the data has been mutated.
    """
    mutated = False
    for task in data["tasks"]:
        if task.get("completed"):
            continue
        scheduled = parse_date(task["scheduled_date"])
        if scheduled < target_date:
            task["scheduled_date"] = format_date(target_date)
            task["rollovers"] = task.get("rollovers", 0) + 1
            mutated = True
    if mutated:
        save_data(data)
    return mutated


def add_task(description: str, weight: int, scheduled_date: _dt.date) -> Dict[str, Any]:
    data = load_data()
    rollover_tasks(data, min(scheduled_date, _dt.date.today()))
    task = {
        "id": data["next_id"],
        "description": description.strip(),
        "weight": weight,
        "scheduled_date": format_date(scheduled_date),
        "completed": False,
        "created_at": _dt.datetime.now().isoformat(),
        "rollovers": 0,
    }
    data["tasks"].append(task)
    data["next_id"] += 1
    save_data(data)
    return task


def list_tasks(target_date: _dt.date, include_other_days: bool = False) -> List[Dict[str, Any]]:
    data = load_data()
    rollover_tasks(data, target_date)
    tasks = data["tasks"]
    if include_other_days:
        filtered = tasks
    else:
        filtered = [task for task in tasks if task["scheduled_date"] == format_date(target_date)]
    filtered.sort(key=lambda t: (-t["weight"], t["created_at"]))
    return filtered


def complete_task(task_id: int) -> Dict[str, Any]:
    data = load_data()
    for task in data["tasks"]:
        if task["id"] == task_id:
            if task.get("completed"):
                return task
            task["completed"] = True
            save_data(data)
            return task
    raise SystemExit(f"Tarefa {task_id} não encontrada.")


def postpone_task(task_id: int, days: int = 1) -> Dict[str, Any]:
    if days < 1:
        raise SystemExit("A quantidade de dias precisa ser positiva.")
    data = load_data()
    for task in data["tasks"]:
        if task["id"] == task_id:
            date = parse_date(task["scheduled_date"]) + _dt.timedelta(days=days)
            task["scheduled_date"] = format_date(date)
            save_data(data)
            return task
    raise SystemExit(f"Tarefa {task_id} não encontrada.")


def print_tasks(tasks: List[Dict[str, Any]], target_date: _dt.date, include_other_days: bool) -> None:
    if not tasks:
        scope = "todas as datas" if include_other_days else f"dia {format_date(target_date)}"
        print(f"Nenhuma tarefa pendente para {scope}.")
        return

    header = f"Agenda para {format_date(target_date)}" if not include_other_days else "Agenda completa"
    print(header)
    print("=" * len(header))
    for task in tasks:
        status = "✔" if task.get("completed") else "✗"
        carry = task.get("rollovers", 0)
        line = (
            f"[{status}] #{task['id']:03d} | Peso {task['weight']} | {task['scheduled_date']}"  # noqa: E501
        )
        if carry:
            line += f" (+{carry} dia(s))"
        line += f"\n    {task['description']}"
        print(line)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agenda ponderada com postergação automática.")
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Cadastrar uma nova atividade")
    add_p.add_argument("description", help="Descrição da atividade")
    add_p.add_argument("weight", type=int, help="Peso (prioridade) - quanto maior, mais prioridade")
    add_p.add_argument(
        "--date",
        type=parse_date,
        default=_dt.date.today(),
        help="Data alvo no formato AAAA-MM-DD (padrão: hoje)",
    )

    list_p = sub.add_parser("list", help="Mostrar a agenda ordenada por peso")
    list_p.add_argument(
        "--date",
        type=parse_date,
        default=_dt.date.today(),
        help="Dia a ser exibido no formato AAAA-MM-DD (padrão: hoje)",
    )
    list_p.add_argument(
        "--all",
        action="store_true",
        help="Inclui tarefas de todas as datas (útil para revisão geral)",
    )

    done_p = sub.add_parser("done", help="Marca uma tarefa como concluída")
    done_p.add_argument("task_id", type=int, help="Identificador numérico da tarefa")

    move_p = sub.add_parser("postpone", help="Adia manualmente uma tarefa para outro dia")
    move_p.add_argument("task_id", type=int)
    move_p.add_argument(
        "--days",
        type=int,
        default=1,
        help="Quantos dias mover para frente (padrão: 1)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "add":
        task = add_task(args.description, args.weight, args.date)
        print(
            "Atividade cadastrada: "
            f"#{task['id']} para {task['scheduled_date']} com peso {task['weight']}."
        )
    elif args.command == "list":
        tasks = list_tasks(args.date, include_other_days=args.all)
        print_tasks(tasks, args.date, args.all)
    elif args.command == "done":
        task = complete_task(args.task_id)
        print(f"Tarefa #{task['id']} marcada como concluída.")
    elif args.command == "postpone":
        task = postpone_task(args.task_id, args.days)
        print(
            f"Tarefa #{task['id']} reagendada para {task['scheduled_date']} "
            f"(peso {task['weight']})."
        )
    else:
        parser.error("Comando desconhecido")


if __name__ == "__main__":
    main()
