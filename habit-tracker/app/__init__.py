"""
Инициализация Flask-приложения.
Здесь создаётся приложение, подключается база данных
и регистрируются маршруты (routes).
"""
import os
from flask import Flask

from app.db import init_db, close_db


def create_app(test_config=None):
    """Фабрика приложения. Позволяет создавать как обычное приложение,
    так и тестовый экземпляр с отдельной базой данных (для pytest)."""
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="dev",  # дляflash-сообщений
        DATABASE=os.path.join(app.instance_path, "habits.sqlite"),
    )

    if test_config is not None:
        # Тестовая конфигурация переопределяет стандартную
        app.config.update(test_config)

    # Создаём папку instance, если её ещё нет
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Регистрируем функцию закрытия соединения с БД после каждого запроса
    app.teardown_appcontext(close_db)

    # Инициализация БД (создание таблиц, если их нет)
    with app.app_context():
        init_db(app)

    # Регистрируем маршруты
    from app import routes
    app.register_blueprint(routes.bp)

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("404.html"), 404

    return app
