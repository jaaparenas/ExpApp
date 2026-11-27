import datetime
import hashlib
import io
import os
import re
import shutil
import tempfile
import unittest
from unittest.mock import patch

import jwt

from app import ExpApp, db, limiter
from app.auth.models import BlacklistToken, User
from config import TestingConfig


class MainTest(unittest.TestCase):

    def setUp(self):
        self.app = ExpApp(TestingConfig)
        self.upload_dir = tempfile.mkdtemp(prefix='expapp-upload-')
        self.app.config.update(UPLOAD_FOLDER=self.upload_dir)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        shutil.rmtree(self.upload_dir, ignore_errors=True)

    # ------------------------------------------------------------------ helpers

    def _create_user(self, username='tester', email='tester@example.com',
                     password='secret123', is_active=True, is_admin=False):
        with self.app.app_context():
            user = User(
                username=username,
                email=email,
                password=password,
                is_active=is_active,
                is_admin=is_admin
            )
            db.session.add(user)
            db.session.commit()
            return user.id

    def _login(self, username='tester', password='secret123'):
        response = self.client.post('/1.0/user/login', json={
            'username': username,
            'password': password
        })
        self.assertEqual(response.status_code, 200, response.get_json())
        return response.get_json()

    def _auth(self, token):
        return {'Authorization': 'Bearer {}'.format(token)}

    def _datatable_params(self, columns=7):
        params = {
            'draw': '1',
            'start': '0',
            'length': '10',
            'search[value]': '',
            'search[regex]': 'false',
            'order[0][column]': '0',
            'order[0][dir]': 'asc',
        }
        for index in range(columns):
            params['columns[{}][data]'.format(index)] = str(index)
            params['columns[{}][name]'.format(index)] = ''
            params['columns[{}][searchable]'.format(index)] = 'true'
            params['columns[{}][orderable]'.format(index)] = 'true'
            params['columns[{}][search][value]'.format(index)] = ''
            params['columns[{}][search][regex]'.format(index)] = 'false'
        return params

    # -------------------------------------------------------------------- basic

    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'ok')

    def test_security_headers(self):
        response = self.client.get('/health')
        self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response.headers['X-Frame-Options'], 'DENY')
        self.assertIn("default-src 'none'", response.headers['Content-Security-Policy'])

    def test_unknown_route_returns_json(self):
        response = self.client.get('/no-existe')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()['msg'], '_NOT_FOUND')

    # --------------------------------------------------------------------- auth

    def test_login_requires_credentials(self):
        response = self.client.post('/1.0/user/login', json={})
        self.assertEqual(response.status_code, 400)

    def test_login_rejects_bad_password(self):
        self._create_user()
        response = self.client.post('/1.0/user/login', json={
            'username': 'tester',
            'password': 'incorrecta'
        })
        self.assertEqual(response.status_code, 400)

    def test_login_and_read_profile(self):
        self._create_user()
        tokens = self._login()

        profile = self.client.get('/1.0/user/data', headers=self._auth(tokens['access']))
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.get_json()['username'], 'tester')
        self.assertFalse(profile.get_json()['is_admin'])

    def test_profile_rejects_anonymous(self):
        response = self.client.get('/1.0/user/data')
        self.assertEqual(response.status_code, 401)

    def test_tampered_token_is_rejected(self):
        self._create_user()
        access = self._login()['access']
        tampered = access[:-2] + ('a' if access[-2] != 'a' else 'b') + access[-1]
        response = self.client.get('/1.0/user/data', headers=self._auth(tampered))
        self.assertEqual(response.status_code, 401)

    def test_expired_token_is_rejected(self):
        user_id = self._create_user()
        now = datetime.datetime.now(datetime.timezone.utc)
        token = jwt.encode({
            'token_type': 'access',
            'user_id': user_id,
            'ver': 0,
            'jti': 'expired-jti',
            'iss': 'expapp',
            'iat': now - datetime.timedelta(hours=2),
            'exp': now - datetime.timedelta(hours=1),
        }, self.app.config['JWT_SECRET_KEY'], algorithm='HS256')

        response = self.client.get('/1.0/user/data', headers=self._auth(token))
        self.assertEqual(response.status_code, 401)

    # ------------------------------------------------------------------- roles

    def test_users_endpoint_requires_admin(self):
        self._create_user()
        access = self._login()['access']
        response = self.client.post(
            '/1.0/user/users',
            json={'params': self._datatable_params()},
            headers=self._auth(access)
        )
        self.assertEqual(response.status_code, 403)

    def test_users_endpoint_rejects_anonymous(self):
        response = self.client.post('/1.0/user/users', json={'params': {}})
        self.assertEqual(response.status_code, 401)

    def test_admin_can_list_users(self):
        self._create_user(username='admin', email='admin@example.com', is_admin=True)
        access = self._login('admin')['access']

        response = self.client.post(
            '/1.0/user/users',
            json={'params': self._datatable_params()},
            headers=self._auth(access)
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        payload = response.get_json()
        self.assertEqual(int(payload['recordsTotal']), 1)
        self.assertEqual(payload['data'][0]['1'], 'admin')

    # ------------------------------------------------------------------ tokens

    def test_refresh_rotates_token(self):
        self._create_user()
        tokens = self._login()

        first = self.client.post('/1.0/user/refresh', json={'refresh': tokens['refresh']})
        self.assertEqual(first.status_code, 200)
        new_tokens = first.get_json()
        self.assertNotEqual(new_tokens['refresh'], tokens['refresh'])

        second = self.client.post('/1.0/user/refresh', json={'refresh': tokens['refresh']})
        self.assertEqual(second.status_code, 401)

        profile = self.client.get('/1.0/user/data', headers=self._auth(new_tokens['access']))
        self.assertEqual(profile.status_code, 200)

    def test_logout_invalidates_access_and_refresh(self):
        self._create_user()
        tokens = self._login()

        logout = self.client.post(
            '/1.0/user/logout',
            json={'refresh': tokens['refresh']},
            headers=self._auth(tokens['access'])
        )
        self.assertEqual(logout.status_code, 200)

        profile = self.client.get('/1.0/user/data', headers=self._auth(tokens['access']))
        self.assertEqual(profile.status_code, 401)

        refresh = self.client.post('/1.0/user/refresh', json={'refresh': tokens['refresh']})
        self.assertEqual(refresh.status_code, 401)

    def test_logout_with_expired_access_revokes_refresh(self):
        user_id = self._create_user()
        tokens = self._login()

        now = datetime.datetime.now(datetime.timezone.utc)
        expired_access = jwt.encode({
            'token_type': 'access',
            'user_id': user_id,
            'ver': 0,
            'jti': 'expired-access-jti',
            'iss': 'expapp',
            'iat': now - datetime.timedelta(hours=2),
            'exp': now - datetime.timedelta(hours=1),
        }, self.app.config['JWT_SECRET_KEY'], algorithm='HS256')

        logout = self.client.post(
            '/1.0/user/logout',
            json={'refresh': tokens['refresh']},
            headers=self._auth(expired_access)
        )
        self.assertEqual(logout.status_code, 200)

        refresh = self.client.post(
            '/1.0/user/refresh',
            json={'refresh': tokens['refresh']}
        )
        self.assertEqual(refresh.status_code, 401)

    def test_change_password_invalidates_old_sessions(self):
        self._create_user()
        tokens = self._login()

        response = self.client.post(
            '/1.0/user/change_password',
            json={
                'current_password': 'secret123',
                'password': 'nuevaClave123',
                'confirm': 'nuevaClave123'
            },
            headers=self._auth(tokens['access'])
        )
        self.assertEqual(response.status_code, 200)

        old_session = self.client.get('/1.0/user/data', headers=self._auth(tokens['access']))
        self.assertEqual(old_session.status_code, 401)

        self.assertEqual(self.client.post('/1.0/user/login', json={
            'username': 'tester', 'password': 'secret123'
        }).status_code, 400)
        self._login(password='nuevaClave123')

    # -------------------------------------------------------------- registration

    def test_registration_disabled_by_default(self):
        response = self.client.post('/1.0/user/register', json={
            'username': 'nuevo', 'email': 'nuevo@example.com', 'password': 'secret123'
        })
        self.assertEqual(response.status_code, 403)

    def test_registration_validates_and_creates_active_user(self):
        self.app.config['ALLOW_REGISTRATION'] = True

        weak = self.client.post('/1.0/user/register', json={
            'username': 'nuevo', 'email': 'nuevo@example.com', 'password': 'corta'
        })
        self.assertEqual(weak.status_code, 400)

        created = self.client.post('/1.0/user/register', json={
            'username': 'nuevo', 'email': 'nuevo@example.com', 'password': 'secret123'
        })
        self.assertEqual(created.status_code, 201)

        duplicate = self.client.post('/1.0/user/register', json={
            'username': 'nuevo', 'email': 'otro@example.com', 'password': 'secret123'
        })
        self.assertEqual(duplicate.status_code, 409)

        self._login('nuevo')

    # ------------------------------------------------------------------- reset

    def test_reset_password_flow(self):
        self._create_user()
        old_access = self._login()['access']

        with patch('app.auth.routes.mail.send') as send:
            response = self.client.post(
                '/1.0/user/reset_password_request',
                json={'email': 'tester@example.com'}
            )
            self.assertEqual(response.status_code, 200)
            send.assert_called_once()
            message = send.call_args[0][0]
            token = re.search(r'token=([A-Za-z0-9_\-]+)', message.html).group(1)

        reset = self.client.post(
            '/1.0/user/reset_password/{}'.format(token),
            json={'password': 'otraClave123', 'confirm': 'otraClave123'}
        )
        self.assertEqual(reset.status_code, 200)

        self.assertEqual(
            self.client.get('/1.0/user/data', headers=self._auth(old_access)).status_code,
            401
        )
        self.assertEqual(self.client.post('/1.0/user/login', json={
            'username': 'tester', 'password': 'secret123'
        }).status_code, 400)
        self._login(password='otraClave123')

        reuse = self.client.post(
            '/1.0/user/reset_password/{}'.format(token),
            json={'password': 'x' * 12, 'confirm': 'x' * 12}
        )
        self.assertEqual(reuse.status_code, 400)

    def test_reset_request_does_not_reveal_emails(self):
        with patch('app.auth.routes.mail.send') as send:
            response = self.client.post(
                '/1.0/user/reset_password_request',
                json={'email': 'no-existe@example.com'}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()['msg'], '_RESET_PASSWORD')
            send.assert_not_called()

    def test_reset_token_expires(self):
        user_id = self._create_user()
        with self.app.app_context():
            user = db.session.get(User, user_id)
            user.reset_password = hashlib.sha256(b'caducado').hexdigest()
            user.reset_password_expires = (
                datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                - datetime.timedelta(minutes=1)
            )
            db.session.commit()

        response = self.client.post(
            '/1.0/user/reset_password/caducado',
            json={'password': 'otraClave123', 'confirm': 'otraClave123'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['msg'], '_EXPIRED_TOKEN')

    # ------------------------------------------------------------------ upload

    def test_upload_requires_authentication(self):
        response = self.client.post('/1.0/datos/subir', data={})
        self.assertEqual(response.status_code, 401)

    def test_upload_accepts_csv(self):
        self._create_user()
        access = self._login()['access']

        response = self.client.post(
            '/1.0/datos/subir',
            data={'file': (io.BytesIO(b'nombre,valor\nuno,1\n'), 'datos.csv')},
            headers=self._auth(access),
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        uploaded = response.get_json()['file'][0]
        self.assertNotEqual(uploaded['disk'], 'error')
        self.assertTrue(os.path.exists(os.path.join(self.upload_dir, uploaded['disk'])))

    def test_upload_rejects_disallowed_extension(self):
        self._create_user()
        access = self._login()['access']

        response = self.client.post(
            '/1.0/datos/subir',
            data={'file': (io.BytesIO(b'MZ ejecutable'), 'virus.exe')},
            headers=self._auth(access),
            content_type='multipart/form-data'
        )
        self.assertEqual(response.get_json()['file'][0]['disk'], 'error')

    def test_upload_rejects_fake_xlsx(self):
        self._create_user()
        access = self._login()['access']

        response = self.client.post(
            '/1.0/datos/subir',
            data={'file': (io.BytesIO(b'esto no es un zip'), 'falso.xlsx')},
            headers=self._auth(access),
            content_type='multipart/form-data'
        )
        self.assertEqual(response.get_json()['file'][0]['disk'], 'error')

    def test_upload_rejects_binary_txt(self):
        self._create_user()
        access = self._login()['access']

        response = self.client.post(
            '/1.0/datos/subir',
            data={'file': (io.BytesIO(b'\x00\x01\x02binario'), 'binario.txt')},
            headers=self._auth(access),
            content_type='multipart/form-data'
        )
        self.assertEqual(response.get_json()['file'][0]['disk'], 'error')

    # --------------------------------------------------------------- blacklist

    def test_purge_expired_blacklist_tokens(self):
        with self.app.app_context():
            BlacklistToken.add(
                'viejo',
                'access',
                datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                - datetime.timedelta(minutes=5)
            )
            db.session.commit()
            deleted = BlacklistToken.purge_expired()
            db.session.commit()
            self.assertEqual(deleted, 1)
            self.assertFalse(BlacklistToken.is_blacklisted('viejo'))


class RateLimitTest(unittest.TestCase):

    def setUp(self):
        class RateLimitConfig(TestingConfig):
            RATELIMIT_ENABLED = True

        self.app = ExpApp(RateLimitConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            limiter.reset()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            limiter.reset()

    def test_login_is_rate_limited(self):
        bad_login = {'username': 'nadie', 'password': 'incorrecta'}

        for _ in range(10):
            response = self.client.post('/1.0/user/login', json=bad_login)
            self.assertEqual(response.status_code, 400)

        blocked = self.client.post('/1.0/user/login', json=bad_login)
        self.assertEqual(blocked.status_code, 429)
        self.assertEqual(blocked.get_json()['msg'], '_TOO_MANY_REQUESTS')


if __name__ == '__main__':
    unittest.main()
