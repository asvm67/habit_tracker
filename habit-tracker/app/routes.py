"""
Маршруты (routes) приложения «Трекер привычек».

Маршруты:
- GET  /                        — главная страница со списком привычек
- GET  /habit/new                — форма добавления привычки
- POST /habit/new                — добавление привычки в БД
- GET  /habit/<id>               — детальная страница привычки
- GET  /habit/<id>/edit          — форма редактирования
- POST /habit/<id>/edit          — сохранение изменений
- POST /habit/<id>/delete        — удаление привычки
- POST /habit/<id>/log           — отметить выполнение за сегодня
"""
from datetime import date, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for, abort

from app.db import get_db
from app.validation import validate_habit_name, validate_target_count

bp = Blueprint("habits", __name__)


def get_habit_or_404(habit_id):
    """Возвращает привычку по id или прерывает запрос с кодом 404."""
    db = get_db()
    habit = db.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
    if habit is None:
        abort(404)
    return habit


def get_progress_today(db, habit_id, target_count):
    """Возвращает количество отметок за сегодня и прогресс в процентах."""
    today = date.today().isoformat()
    count = db.execute(
        "SELECT COUNT(*) AS c FROM logs WHERE habit_id = ? AND log_date = ?",
        (habit_id, today),
    ).fetchone()["c"]
    percent = min(100, round(100 * count / target_count)) if target_count else 0
    return count, percent


def get_history(db, habit_id, days=7):
    """Возвращает список из последних `days` дней с отметкой,
    выполнялась ли привычка в этот день (хотя бы один раз)."""
    history = []
    for i in range(days - 1, -1, -1):
        day = date.today() - timedelta(days=i)
        day_str = day.isoformat()
        done = db.execute(
            "SELECT COUNT(*) AS c FROM logs WHERE habit_id = ? AND log_date = ?",
            (habit_id, day_str),
        ).fetchone()["c"]
        history.append({"date": day_str, "label": day.strftime("%d.%m"), "done": done > 0})
    return history


@bp.route("/")
def index():
    """Главная страница: список привычек с прогрессом за сегодня.
    Поддерживает поиск по названию через параметр ?q=..."""
    db = get_db()
    query = request.args.get("q", "").strip()

    if query:
        habits = db.execute(
            "SELECT * FROM habits WHERE name LIKE ? ORDER BY created_at DESC",
            (f"%{query}%",),
        ).fetchall()
    else:
        habits = db.execute("SELECT * FROM habits ORDER BY created_at DESC").fetchall()

    habits_with_progress = []
    for h in habits:
        count, percent = get_progress_today(db, h["id"], h["target_count"])
        habits_with_progress.append(
            {"habit": h, "count_today": count, "percent": percent}
        )

    return render_template(
        "index.html", habits=habits_with_progress, query=query
    )


@bp.route("/habit/new", methods=["GET", "POST"])
def new_habit():
    """Форма и обработка добавления новой привычки."""
    if request.method == "POST":
        name = request.form.get("name", "")
        description = request.form.get("description", "").strip()
        target_count_raw = request.form.get("target_count", "1")

        ok_name, err_name = validate_habit_name(name)
        ok_target, err_target, target_count = validate_target_count(target_count_raw)

        if not ok_name:
            flash(err_name)
        elif not ok_target:
            flash(err_target)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO habits (name, description, target_count) VALUES (?, ?, ?)",
                (name.strip(), description, target_count),
            )
            db.commit()
            flash("Привычка добавлена!")
            return redirect(url_for("habits.index"))

    return render_template("habit_form.html", habit=None)


@bp.route("/habit/<int:habit_id>")
def habit_detail(habit_id):
    """Детальная страница привычки: прогресс за сегодня и история за 7 дней."""
    db = get_db()
    habit = get_habit_or_404(habit_id)
    count_today, percent = get_progress_today(db, habit_id, habit["target_count"])
    history = get_history(db, habit_id, days=7)
    return render_template(
        "habit_detail.html",
        habit=habit,
        count_today=count_today,
        percent=percent,
        history=history,
    )


@bp.route("/habit/<int:habit_id>/edit", methods=["GET", "POST"])
def edit_habit(habit_id):
    """Форма и обработка редактирования привычки."""
    habit = get_habit_or_404(habit_id)

    if request.method == "POST":
        name = request.form.get("name", "")
        description = request.form.get("description", "").strip()
        target_count_raw = request.form.get("target_count", "1")

        ok_name, err_name = validate_habit_name(name)
        ok_target, err_target, target_count = validate_target_count(target_count_raw)

        if not ok_name:
            flash(err_name)
        elif not ok_target:
            flash(err_target)
        else:
            db = get_db()
            db.execute(
                "UPDATE habits SET name = ?, description = ?, target_count = ? WHERE id = ?",
                (name.strip(), description, target_count, habit_id),
            )
            db.commit()
            flash("Привычка обновлена!")
            return redirect(url_for("habits.habit_detail", habit_id=habit_id))

    return render_template("habit_form.html", habit=habit)


@bp.route("/habit/<int:habit_id>/delete", methods=["POST"])
def delete_habit(habit_id):
    """Удаление привычки (и связанных отметок через ON DELETE CASCADE)."""
    get_habit_or_404(habit_id)
    db = get_db()
    db.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    db.commit()
    flash("Привычка удалена.")
    return redirect(url_for("habits.index"))


@bp.route("/habit/<int:habit_id>/log", methods=["POST"])
def log_habit(habit_id):
    """Отметка о выполнении привычки за сегодня (можно несколько раз в день,
    если target_count > 1)."""
    habit = get_habit_or_404(habit_id)
    db = get_db()
    today = date.today().isoformat()

    count_today, _ = get_progress_today(db, habit_id, habit["target_count"])

    # Не позволяем отмечать больше, чем целевое количество раз в день
    if count_today < habit["target_count"]:
        db.execute(
            "INSERT INTO logs (habit_id, log_date) VALUES (?, ?)",
            (habit_id, today),
        )
        db.commit()
    else:
        flash("Цель на сегодня уже достигнута!")

    return redirect(request.referrer or url_for("habits.index"))
