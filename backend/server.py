# manage.py
import os
import unittest
import coverage

from flask_script import Manager
from flask_migrate import MigrateCommand
from app import ExpApp, db, migrate
from app.auth.models import User

COV = coverage.coverage(
    branch=True,
    include='app/*',
    omit=[
        'tests/',
        'static/*'
    ]
)
COV.start()

manager = Manager(ExpApp)
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('./tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def coverage():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('./tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.erase()
        return 0
    return 1


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()

    
@manager.command
def create_su():
    """Create the super User."""
    user = User(username='admin', email='admin@local.com', password='admin', is_active=1, is_admin=1)
    db.session.add(user)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
