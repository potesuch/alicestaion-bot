import re

URL_USER = 'https://iot.quasar.yandex.ru/m/user'
URL_V3_USER = 'https://iot.quasar.yandex.ru/m/v3/user'

def parse_scenario(data: dict) -> dict:
    result = {
        k: v
        for k, v in data.items()
        if k in ("name", "icon", "effective_time", "settings")
    }
    result["triggers"] = [parse_trigger(i) for i in data["triggers"]]
    result["steps"] = [parse_step(i) for i in data["steps"]]
    return result


def parse_trigger(data: dict) -> dict:
    result = {k: v for k, v in data.items() if k == "filters"}

    value = data["trigger"]["value"]
    if isinstance(value, dict):
        value = {
            k: v
            for k, v in value.items()
            if k in ("instance", "property_type", "condition")
        }
        value["device_id"] = data["trigger"]["value"]["device"]["id"]

    result["trigger"] = {"type": data["trigger"]["type"], "value": value}
    return result


def parse_step(data: dict) -> dict:
    params = data["parameters"]
    return {
        "type": data["type"],
        "parameters": {
            "requested_speaker_capabilities": params["requested_speaker_capabilities"],
            "launch_devices": [parse_device(i) for i in params["launch_devices"]],
        },
    }


def parse_device(data: dict) -> dict:
    return {
        "id": data["id"],
        "capabilities": [
            {"type": i["type"], "state": i["state"]} for i in data["capabilities"]
        ],
        "directives": data["directives"],
    }


class YandexQuasar:

    def __init__(self, session):
        self.session = session

    async def _update_csrf_token(self):
        r = await self.session.get('https://yandex.ru/quasar')
        data = await r.text()
        m = re.search('"csrfToken2":"(.+?)"', data)
        self.csrf_token = m[1]

    async def get(self):
        r = await self.session.get(f'{URL_V3_USER}/devices')
        try:
            data = await r.json()
        except:
            print(await r.text())
        assert data['status'] == 'ok', data
        self.devices = []
        for household in data['households']:
            if 'sharing_info' in household:
                continue
            self.devices += household['all']
        await self.get_scenarios()

    async def get_scenarios(self):
        r = await self.session.get(f'{URL_USER}/scenarios')
        data = await r.json()
        assert data['status'] == 'ok', data
        self.scenarios = data['scenarios']

    @property
    def speakers(self):
        return [
            d for d in self.devices if d.get('quasar_info') and d.get('capabilities')
        ]

    async def create_scenario(self, speaker_id):
        payload = {
            'name': f'bot_command_{speaker_id}',
            'icon': 'home',
            'triggers': [{
                'type': 'scenario.trigger.voice',
                'value': speaker_id
            }],
            'steps': [{
                'type': 'scenarios.steps.actions',
                'parameters': {
                    'requested_speaker_capabilities': [],
                    'launch_devices': [{
                        'id': speaker_id,
                        'capabilities': [{
                            'type': 'devices.capabilities.quasar.server_action',
                            'state': {
                                'instance': 'text_action',
                                'value': 'Привет',
                            }
                        }]
                    }]
                }
            }]
        }
        await self._update_csrf_token()
        r = await self.session.post(f'{URL_USER}/scenarios', json=payload,
                                    headers={'x-csrf-token': self.csrf_token})
        data = await r.json()
        assert data['status'] == 'ok', data

    async def update_scenario(self, scenario_id, command):
        r = await self.session.get(f'{URL_V3_USER}/scenarios/{scenario_id}/edit')
        data = await r.json()
        assert data['status'] == 'ok', data
        payload = parse_scenario(data['scenario'])
        payload['steps'][0]['parameters']['launch_devices'][0]['capabilities'][0]['state']['value'] = command
        await self._update_csrf_token()
        r = await self.session.put(f'{URL_V3_USER}/scenarios/{scenario_id}', json=payload,
                                   headers={'x-csrf-token': self.csrf_token})
        data = await r.json()
        assert data['status'] == 'ok', data

    async def exec_scenario(self, scenario_id):
        await self._update_csrf_token()
        r = await self.session.post(f'{URL_USER}/scenarios/{scenario_id}/actions',
                                    headers={'x-csrf-token': self.csrf_token})
        data = await r.json()
        assert data['status'] == 'ok', data
