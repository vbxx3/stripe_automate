import os

from recaptcha import Captcha

import uvloop
import asyncio

from aiohttp import ClientSession
from urllib import parse
from dotenv import load_dotenv

import click

load_dotenv()
uvloop.install()

# Environment vars
DATA_SITEKEY = '6LezRwYTAAAAAClbeZahYjeSYHsbwpzjEQ0hQ1jB'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
CAPTCHA_KEY = os.getenv('CAPTCHA_KEY')
PAYMENT_ID = os.getenv('PAYMENT_ID')

CHARGE = "ch_1I646ZL5RkOYbcxuPRIFM3BX"
CREATED = 1609809179


async def main(charge: str,
               created: int):
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
					session_cookie = str(response.headers).split('session=')[1].split('; domain')[0]
					response = await response.json()
			if "csrf_token" not in response:
				print(response)
				raise Exception('Unexpected response')
			csrf = response['csrf_token']
			api_key = response['session_api_key']
			print("================ Credentials ================")
			print(f'CSRF Token: {csrf}')
			print(f'Session API Key: {api_key}')
			print(f'Session cookie: {session_cookie}')
			print(f'for email {response["email"]}')
			print()
		print({"variables": {"time": created, "input": {"charge": f'"{charge}"'}}})
		payload = {"operationName": "RadarAllSignalsForChargeQuery",
		           "variables": {"time": created, "input": {"charge": f'"{charge}"'}},
		           "query": "query RadarAllSignalsForChargeQuery($time: Int!, $input: ApiRadarSignalsSignalsDataInput) "
		                    "{\n  currentMerchant {\n    id\n    created\n    radarSettingsAtTime(time: $time) {\n     "
		                    " highestRiskThreshold\n      elevatedRiskThreshold\n      __typename\n    }\n    "
		                    "__typename\n  }\n  radarSignalsData(input: $input) {\n    amountMeanForCard\n    "
		                    "amountStandardDeviationForCard\n    billingToIpDistanceInKm\n    "
		                    "shippingToBillingDistanceInKm\n    shippingToIpDistanceInKm\n    amountInUsd\n    "
		                    "issuingBank\n    email\n    cardName\n    deviceBrand\n    deviceModel\n    emailAge\n    "
		                    "internetServiceProvidor\n    cardholderIp\n    operatingSystem\n    browser\n    "
		                    "cardholderName\n    cardCountsForDeviceLastWeek {\n      counterValue\n      insightsData "
		                    "{\n        ...CounterFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "selectedBucket\n      __typename\n    }\n    cardCountsForDeviceSecondsSinceFirstSeen {\n "
		                    "     counterValue\n      insightsData {\n        ...CounterFeatureInsightsDataFragment\n  "
		                    "      __typename\n      }\n      selectedBucket\n      __typename\n    }\n    "
		                    "cardCountsForEmailDeclinesLastWeek {\n      counterValue\n      insightsData {\n        "
		                    "...CounterFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "selectedBucket\n      __typename\n    }\n    "
		                    "cardCountsForEmailDeclinesSecondsSinceFirstSeen {\n      counterValue\n      insightsData "
		                    "{\n        ...CounterFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "selectedBucket\n      __typename\n    }\n    cardCountsForIpLastWeek {\n      "
		                    "counterValue\n      insightsData {\n        ...CounterFeatureInsightsDataFragment\n       "
		                    " __typename\n      }\n      selectedBucket\n      __typename\n    }\n    "
		                    "chargesForIpAllTimeSuccessRate {\n      counterValue\n      insightsData {\n        "
		                    "...CounterFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "selectedBucket\n      __typename\n    }\n    ipCountsForCardAuthorizedLastWeek {\n      "
		                    "counterValue\n      insightsData {\n        ...CounterFeatureInsightsDataFragment\n       "
		                    " __typename\n      }\n      selectedBucket\n      __typename\n    }\n    "
		                    "ipCountsForCardAuthorizedSecondsSinceFirstSeen {\n      counterValue\n      insightsData "
		                    "{\n        ...CounterFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "selectedBucket\n      __typename\n    }\n    nameCountsForIpLastWeek {\n      "
		                    "counterValue\n      insightsData {\n        ...CounterFeatureInsightsDataFragment\n       "
		                    " __typename\n      }\n      selectedBucket\n      __typename\n    }\n    "
		                    "nameCountsForIpSecondsSinceFirstSeen {\n      counterValue\n      insightsData {\n        "
		                    "...CounterFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "selectedBucket\n      __typename\n    }\n    normalizedNameCountsForCardLastWeek {\n      "
		                    "counterValue\n      insightsData {\n        ...CounterFeatureInsightsDataFragment\n       "
		                    " __typename\n      }\n      selectedBucket\n      __typename\n    }\n    "
		                    "countryCountsForCardLastWeek {\n      counterValue\n      insightsData {\n        "
		                    "...CounterFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "selectedBucket\n      __typename\n    }\n    chargesForEmailAllTimeSuccessRate {\n      "
		                    "counterValue\n      insightsData {\n        ...CounterFeatureInsightsDataFragment\n       "
		                    " __typename\n      }\n      selectedBucket\n      __typename\n    }\n    isDebit {\n      "
		                    "value\n      insightsData {\n        ...CategoricalFeatureInsightsDataFragment\n        "
		                    "__typename\n      }\n      __typename\n    }\n    isPrepaid {\n      value\n      "
		                    "insightsData {\n        ...CategoricalFeatureInsightsDataFragment\n        __typename\n   "
		                    "   }\n      __typename\n    }\n    pastedCvc {\n      value\n      insightsData {\n       "
		                    " ...CategoricalFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "__typename\n    }\n    pastedEmail {\n      value\n      insightsData {\n        "
		                    "...CategoricalFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "__typename\n    }\n    pastedExpiration {\n      value\n      insightsData {\n        "
		                    "...CategoricalFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "__typename\n    }\n    pastedNumber {\n      value\n      insightsData {\n        "
		                    "...CategoricalFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "__typename\n    }\n    pastedZip {\n      value\n      insightsData {\n        "
		                    "...CategoricalFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "__typename\n    }\n    isNamePartInEmail {\n      value\n      insightsData {\n        "
		                    "...CategoricalFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "__typename\n    }\n    hasPriorDisputeOnCardholderIp {\n      value\n      insightsData {"
		                    "\n        ...CategoricalFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "__typename\n    }\n    hasPriorIfrOnCardholderIp {\n      value\n      insightsData {\n   "
		                    "     ...CategoricalFeatureInsightsDataFragment\n        __typename\n      }\n      "
		                    "__typename\n    }\n    __typename\n  }\n}\n\nfragment CounterFeatureInsightsDataFragment "
		                    "on ApiRadarSignalsCounterSignalBucket {\n  key\n  networkDistribution\n  "
		                    "normalizedFraudRate\n  __typename\n}\n\nfragment CategoricalFeatureInsightsDataFragment "
		                    "on ApiRadarSignalsCategoricalSignalBucket {\n  bucketValue\n  networkDistribution\n  "
		                    "normalizedFraudRate\n  __typename\n}\n"}
		async with session.post('https://dashboard.stripe.com/ajax/graphql',
		                        json=payload,
		                        headers={
			                        'x-stripe-csrf-token': csrf,
			                        'stripe-livemode': 'false',
			                        'Referer': 'https://dashboard.stripe.com/test/payments/pi_1I646ZL5RkOYbcxulqDwH6RR',
			                        'Origin': 'https://dashboard.stripe.com'
		                        },
		                        cookies={
			                        'session': session_cookie
		                        }
		                        ) as response:
			print(await response.json())


@click.command()
@click.option('--charge', default=CHARGE)
@click.option('--created', type=int, default=CREATED)
def click_main(charge: str,
               created: int):
	asyncio.get_event_loop().run_until_complete(main(charge, created))


if __name__ == "__main__":
	click_main()
