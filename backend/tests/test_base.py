from flask_testing import TestCase

from app import ExpApp

class MainTest(TestCase):
    def create_app(self):
        ExpApp.config['TESTING'] = True
        return ExpApp