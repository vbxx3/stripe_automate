import os

from payloads import risk_graphql
from recaptcha import Captcha
from utils import split

import uvloop
import asyncio

from aiohttp import ClientSession
from urllib import parse
from dotenv import load_dotenv

load_dotenv()
uvloop.install()

# Environment vars
DATA_SITEKEY = '6LezRwYTAAAAAClbeZahYjeSYHsbwpzjEQ0hQ1jB'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
CAPTCHA_KEY = os.getenv('CAPTCHA_KEY')

# Values for test purposes
CHARGE = "ch_1I646ZL5RkOYbcxuPRIFM3BX"
CREATED = 1609809179


class InsightLoader:
    def __init__(self,
                 email: str,
                 password: str,
                 captcha_key: str,
                 data_sitekey: str):
        self.email = email
        self.password = password
        self.captcha_solver = Captcha(captcha_key)
        self.captcha_key = data_sitekey

        self.__is_logged_in = False
        self.__session = None
        self.__csrf = None
        self.__session_cookie = None

    async def sign_in(self):
        session = ClientSession(headers={
            'User-Agent': USER_AGENT
        })
        async with session.get('https://dashboard.stripe.com/login',
                               ) as response:
            await response.read()
            unesc_csrf = str(response.headers).split('stripe.csrf=')[1].split('; domain=stripe.com')[0]
            csrf = parse.unquote(unesc_csrf)
        # Defining login payload
        payload = {
            "email": EMAIL,
            "password": PASSWORD,
            "io_blackbox": "",
            "remember": True,
            "merchant": "",
            "invite_code": "",
            "account_invite": "",
            "invite": "",
            "redirect": "/",
            "source": "main_login",
            "has_platform_authenticator": False
        }
        # Defining headers
        headers = {
            'origin': 'https://dashboard.stripe.com',
            'referer': 'https://dashboard.stripe.com/login',
            'x-stripe-csrf-token': csrf,
            'x-requested-with': 'XMLHttpRequest'
        }
        async with session.post('https://dashboard.stripe.com/ajax/sessions',
                                headers=headers,
                                data=payload) as response:
            response = await response.json()
            if response.get('error_type', '') == 'need_captcha':
                # Solve captcha if it raised
                captcha = Captcha(self.captcha_key)
                g_response = captcha.solve('https://dashboard.stripe.com/login',
                                           DATA_SITEKEY)
                payload['g-recaptcha-response'] = g_response
                async with session.post('https://dashboard.stripe.com/ajax/sessions',
                                        headers=headers,
                                        data=payload) as response:
                    self.__session_cookie = str(response.headers).split('session=')[1].split('; domain')[0]
                    response = await response.json()
            if "csrf_token" not in response:
                print(response)
                raise Exception('Unexpected response')
            self.__session = session
            self.__csrf = response['csrf_token']
            self.__is_logged_in = True

    async def load_one(self,
                       charge: str,
                       created: int):
        if not self.__is_logged_in:
            raise Exception('Stripe was never logged in')
        payload = risk_graphql(created, charge)
        async with self.__session.post('https://dashboard.stripe.com/ajax/graphql',
                                       json=payload,
                                       headers={
                                           'x-stripe-csrf-token': self.__csrf,
                                           'stripe-livemode': 'false',
                                           'Referer': 'https://dashboard.stripe.com/test/payments/'
                                                      'pi_1I646ZL5RkOYbcxulqDwH6RR',
                                           'Origin': 'https://dashboard.stripe.com'
                                       },
                                       cookies={
                                           'session': self.__session_cookie
                                       }
                                       ) as response:
            return await response.json()

    async def load_many(self,
                        payments: list,
                        parallel: int = 3):
        chunk_list = split(payments, parallel)
        result = list()
        for chunk in chunk_list:
            result += await asyncio.gather(*[self.load_one(*element) for element in chunk])
        return result

    async def close(self):
        await self.__session.close()


async def test():
    loader = InsightLoader(EMAIL, PASSWORD, CAPTCHA_KEY, DATA_SITEKEY)
    await loader.sign_in()
    # for one - await loader.load_one(charge, created)
    result = await loader.load_many([
        [CHARGE, CREATED],
        [CHARGE, CREATED],
        [CHARGE, CREATED]
    ])
    print(result)
    await loader.close()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test())
