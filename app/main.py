from celery import Celery, Task
from flask import Flask
from lib.routes.api import routes


def celery_init_app(f_app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with f_app.app_context():
                return self.run(*args, **kwargs)

    c_app = Celery(f_app.name, task_cls=FlaskTask)
    c_app.config_from_object(f_app.config["CELERY"])
    c_app.set_default()
    f_app.extensions["celery"] = c_app
    return c_app


flask_app = Flask(__name__)
flask_app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://redis-queue",
        result_backend="redis://redis-queue",
        task_ignore_result=True,
    ),
)
celery_app = celery_init_app(flask_app)
flask_app.register_blueprint(routes)
