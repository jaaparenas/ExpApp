import os
import secrets
import unittest

import click
from flask.cli import with_appcontext

from app import ExpApp, db
from app.auth.models import User

app = ExpApp()


@app.cli.command('test')
def test():
    """Ejecuta las pruebas sin cobertura."""
    tests = unittest.TestLoader().discover('./tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if not result.wasSuccessful():
        raise SystemExit(1)


@app.cli.command('coverage')
def coverage_report():
    """Ejecuta las pruebas con cobertura."""
    import coverage

    cov = coverage.coverage(branch=True, include='app/*', omit=['tests/', 'static/*'])
    cov.start()
    tests = unittest.TestLoader().discover('./tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    cov.stop()
    cov.save()
    cov.report()
    cov.erase()
    if not result.wasSuccessful():
        raise SystemExit(1)


@app.cli.command('create-db')
@with_appcontext
def create_db():
    """Crea las tablas de la base de datos."""
    db.create_all()


@app.cli.command('drop-db')
@with_appcontext
def drop_db():
    """Elimina las tablas de la base de datos."""
    db.drop_all()


@app.cli.command('purge-tokens')
@with_appcontext
def purge_tokens():
    """Elimina de la lista negra los tokens ya expirados."""
    from app.auth.models import BlacklistToken
    deleted = BlacklistToken.purge_expired()
    db.session.commit()
    click.echo('Tokens expirados eliminados: {}'.format(deleted))


@app.cli.command('create-su')
@with_appcontext
def create_su():
    """Crea el superusuario desde ADMIN_USERNAME / ADMIN_EMAIL / ADMIN_PASSWORD."""
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    email = os.environ.get('ADMIN_EMAIL', 'admin@local.com')
    password = os.environ.get('ADMIN_PASSWORD')

    existing = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing is not None:
        raise click.ClickException('Ya existe un usuario con ese username o email.')

    generated = False
    if not password:
        password = secrets.token_urlsafe(18)
        generated = True

    user = User(
        username=username,
        email=email,
        password=password,
        is_active=True,
        is_admin=True
    )
    db.session.add(user)
    db.session.commit()

    click.echo('Superusuario creado: {}'.format(username))
    if generated:
        click.echo('Contraseña generada (guárdala ahora): {}'.format(password))


if __name__ == '__main__':
    app.run()
