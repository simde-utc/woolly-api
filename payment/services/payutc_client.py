from functools import partial
import requests
from typing import Any


ALLOWED_ACTIONS_MAP = {
    'get': 'get',
    'find': 'get',
    'create': 'post',
    'update': 'put',
    'delete': 'delete',
}

BASE_CONFIG = {
    'base_url': 'https://api.nemopay.net',
    'nemopay_version': '2018-07-03',
    'system_id': '80405',
    'fun_id': None,
    'async': False,

    # Login credentials
    'session_id': None,
    'app_key': None,
    'username': None,
    'login_method': None,
    'badge_id': None,
    'badge_pin': None,
    'mail': None,
    'password': None,
    'cas_ticket': None,
    'cas_service': None,
}


def filter_dict_by_keys(dico: dict, *keys: tuple) -> dict:
    return { key: dico[key] for key in keys }


class PayutcException(Exception):
    """
    Payutc Client Exception
    """
    def __init__(self,
                 message: str=None,
                 response: requests.Response=None,
                 config: dict=None,
                 data: dict=None):
        if response.text:
            message += f"\nResponse: {response.text}"
        super().__init__(message)
        self.response = response
        self.config = config
        self.data = data

    @classmethod
    def from_response(cls, response: dict) -> 'PayutcException':
        """
        Create an PayutcException from an API response
        """
        error = response.get('error')
        if not error:
            return cls("Erreur inconnue", 'unknown_payutc_error')

        message = error.get('message', "Une erreur inconnue est survenue avec PayUTC")
        code = error['error']
        details = [ f"{k}: {m}" for k, m in error.get('data', {}).items() ]

        return cls(message, code, details)


class PayutcClient:
    """
    The Payutc Client for the Nemopay API
    """

    def __init__(self, config: dict={}, **kwargs):
        self.config = {
            **BASE_CONFIG,
            **config,
            **kwargs,
        }

    def request(self, method: str, uri: str, data: dict={}, api: str='resources', **kwargs) -> Any:
        """
        Generic request to the Payutc API
        Can request both 'resources' (new, by default) and 'services' (old) APIs

        Args:
            method: the HTTP method
            uri:    the endpont to request
            data:   the data to sent in the request (default: {})
            api:    the API to request (default: 'resources')
            return_response: If true, return the response no matter what the status (default: False)

        Returns:
            Response or data

        Raises:
            PayutcException: in case something goes wrong raise a PayutcException
        """
        # Build url
        assert api in {'services', 'resources'}
        url = f"{self.config['base_url']}/{api}/{uri}"
        if 'id' in kwargs:
            url += f"/{kwargs['id']}"

        request_config = {
            'params': filter_dict_by_keys(self.config, 'app_key', 'system_id'),
            'cookies': { 'sessionid': self.config.get('session_id') },
            'headers': {
                'Content-Type': 'application/json',
                'nemopay-version': self.config.get('nemopay_version'),
            },
        }

        if method == 'get':
            request_config['params'].update(data)
        else:
            request_config['json'] = data

        # Make the request
        response = requests.request(method, url, **request_config)

        if kwargs.get('return_response', False):
            return response

        if response.ok:
            return response.json()

        message = f"Error {response.status_code} on {method.upper()} {api}/{uri}"
        raise PayutcException(message, response, request_config, data)

    def list_routes(self):
        """
        List all available routes of the resources API
        """
        return self.request('get', '')

    def __getattr__(self, attr: str) -> Any:
        if attr in ALLOWED_ACTIONS_MAP:
            return partial(self.request, attr)

        # Dynamic resource methods
        # Example: payutc.create_item(...)
        split = attr.split('_')
        if len(split) == 2:
            action, resource = split
            if action in ALLOWED_ACTIONS_MAP:
                http_method = ALLOWED_ACTIONS_MAP[action]
                return partial(self.request, http_method, resource)

        raise AttributeError(f"'{attr}' is not a valid dynamic request")

    def __repr__(self) -> str:
        conf = {
            'fun_id': self.config['fun_id'],
            'authenticated': self.is_authenticated,
        }
        conf_str = ' '.join(k if v is True else f"{k}={v}" for k, v in conf.items() if v)
        return f"<PayutcClient {conf_str}>"

    # ------------------------------------------------------------
    #   Configuration
    # ------------------------------------------------------------

    def _get_data_or_config(self, data: dict, *keys) -> dict:
        return {
            key: data.get(key, self.config.get(key))
            for key in keys
            if key in data or key in self.config
        }

    def _set_or_get_config(self, key: str, value: Any=None) -> Any:
        """
        Set key in config if there is a value otherwise get it from the config
        """
        if value is not None:
            self.config[key] = value
            return value
        else:
            return self.config[key]

    # ------------------------------------------------------------
    #   Login
    # ------------------------------------------------------------

    def _login(self, response: dict) -> dict:
        if type(response) is not dict or not response.get('sessionid'):
            raise PayutcException('Login failed', response)
        self.config['session_id'] = response.get('sessionid')
        self.config['username'] = response.get('username')
        return response

    def login(self, method: str, **kwargs):
        method = self._set_or_get_config('method', method)
        login_function = getattr(self, f"login_{method}", None)
        if login_function and callable(login_function):
            return login_function(**kwargs)
        else:
            raise NotImplementedError(f"Login method '{method}' is not implemented")

    @property
    def is_authenticated(self) -> bool:
        return bool(self.config.get('session_id'))

    def get_user_details(self) -> dict:
        return self.request('post', 'MYACCOUNT/getUserDetails', api='services')

    def login_cas(self, ticket: str=None, service: str=None):
        data = {
            'ticket': self._set_or_get_config('cas_ticket', ticket),
            'service': self._set_or_get_config('cas_service', service),
        }
        response = self.request('post', 'POSS3/loginCas', data, api='services')
        return self._login(response)

    def login_app(self, app_key: str=None):
        data = { 'key': self._set_or_get_config('app_key', app_key) }
        response = self.request('post', 'POSS3/loginApp', data, api='services')
        return self._login(response)

    def login_user(self, login: str=None, password: str=None):
        data = {
            'login': self._set_or_get_config('mail', login),
            'password': self._set_or_get_config('password', password),
        }
        response = self.request('post', 'SELFPOS/login2', data, api='services')
        return self._login(response)

    def login_badge(self, badge_id: str=None, pin: int=None):
        data = {
            'badge_id': self._set_or_get_config('badge_id', badge_id),
            'pin': self._set_or_get_config('badge_pin', pin),
        }
        response = self.request('post', 'POSS3/loginBadge2', data, api='services')
        return self._login(response)

    # ------------------------------------------------------------
    #   Web transactions
    # ------------------------------------------------------------

    def create_transaction(self, data: dict) -> dict:
        keys = ('items', 'mail', 'return_url', 'fun_id', 'callback_url')
        data = self._get_data_or_config(data, *keys)
        data['fun_id'] = str(data['fun_id'])  # TODO str ??
        data['items'] = str(data['items'])
        resp = self.request('post', 'WEBSALE/createTransaction', data, api='services')
        if 'error' in resp:
            raise PayutcException.from_response(resp)
        return resp

    def get_transaction(self, data: dict) -> dict:
        data = self._get_data_or_config(data, 'tra_id', 'fun_id')
        return self.request('post', 'WEBSALE/getTransactionInfo', data, api='services')

    def get_payment_url(self, tra_id: int) -> str:
        return f"https://payutc.nemopay.net/validation?tra_id={tra_id}"

    def upsert_category(self, data: dict, id: int=None) -> int:
        if id is not None:
            data["obj_id"] = id
        return self.request("post", "GESARTICLE/setCategory", data, api="services")["success"]

    def upsert_product(self, data: dict, id: int=None) -> int:
        if id is not None:
            data["obj_id"] = id
        return self.request("post", "GESARTICLE/setProduct", data, api="services")["success"]
