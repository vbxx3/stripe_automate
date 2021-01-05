import os

from recaptcha import Captcha

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
PAYMENT_ID = os.getenv('PAYMENT_ID')


async def main():
	async with ClientSession(headers={
		'User-Agent': USER_AGENT
	}) as session:
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
				captcha = Captcha(CAPTCHA_KEY)
				g_response = captcha.solve('https://dashboard.stripe.com/login',
				                           DATA_SITEKEY)
				payload['g-recaptcha-response'] = g_response
				async with session.post('https://dashboard.stripe.com/ajax/sessions',
				                        headers=headers,
				                        data=payload) as response:
					response = await response.json()
					csrf = response['csrf_token']
					api_key = response['session_api_key']
					print("\n================ Credentials ================")
					print(f'CSRF Token: {csrf}')
					print(f'Session API Key: {api_key}')
					print(f'for email {response["email"]}')
					print()
		# Next steps to get Risk Insights
		# stripe-account header will be flexible later
		async with session.get(f'https://dashboard.stripe.com/v1/events?related_object={PAYMENT_ID}',  # Will be modfied later
		                       headers={
			                       'Authorization': f'Bearer {api_key}',
			                       'stripe-livemode': 'false',
			                       'stripe-account': 'acct_1I1Tb5L5RkOYbcxu',
			                       'Referer': 'https://dashboard.stripe.com/test/payments'
		                       }
		                       ) as response:
			print(await response.text())


if __name__ == "__main__":
	asyncio.get_event_loop().run_until_complete(main())
