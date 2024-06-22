import re


class YandexSession:
    """
    Класс для работы с сессиями Яндекса.

    Arguments:
        session: Сессия для выполнения HTTP-запросов.
        username (str, optional): Имя пользователя для авторизации.
        password (str, optional): Пароль для авторизации.
    """

    def __init__(self, session, username=None, password=None):
        self.session = session
        self.username = username
        self.password = password

    async def login(self):
        """
        Выполняет авторизацию пользователя.

        Возвращает:
            tuple: Кортеж с данными авторизации и состоянием авторизации.
        """
        r = await self.session.get(
                'https://passport.yandex.ru/auth'
        )
        data = await r.text()
        m = re.search(r'"csrf_token" value="([^"]+)"', data)
        auth_payload = {'csrf_token': m[1]}
        r = await self.session.post(
            'https://passport.yandex.ru/registration-validations/auth/multi_step/start',
            data={**auth_payload, 'login': self.username}
        )
        data = await r.json()
        if data.get('can_register') is True:
            state = 'wrong_login'
            return auth_payload, state
        auth_payload['track_id'] = data.get('track_id')
        r = await self.session.post(
            'https://passport.yandex.ru/registration-validations/auth/multi_step/commit_password',
            data={
                **auth_payload,
                'password': self.password,
                'retpath': 'https://passport.yandex.ru/am/finish?status=ok&from=Login'
            }
        )
        data = await r.json()
        if data['status'] != 'ok':
            state = 'wrong_password'
            return auth_payload, state
        state = data.get('state') or 'authenticated'
        if state == 'auth_challenge':
            r = await self.session.post(
                'https://passport.yandex.ru/registration-validations/auth/challenge/submit',
                data={
                    **auth_payload
                }
            )
            r = await self.session.post(
                'https://passport.yandex.ru/registration-validations/auth/challenge/send_push',
                data={
                    **auth_payload
                }
            )
        return auth_payload, state

    async def code_auth(self, auth_payload, code):
        """
        Подтверждает авторизацию с использованием кода.

        Аргументы:
            auth_payload (dict): Данные авторизации.
            code (str): Код для подтверждения.

        Возвращает:
            str: Статус авторизации.
        """
        r = await self.session.post(
            'https://passport.yandex.ru/registration-validations/auth/challenge/commit',
            data={
                **auth_payload,
                'challenge': 'push_2fa',
                'answer': code
            }
        )
        data = await r.json()
        status = data['status']
        if status != 'ok':
            print('Неверный код')
        return status
