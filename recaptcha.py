import time

import backoff as backoff
import requests


class Captcha:
    def __init__(self, api_key: str):
        self.api_key = api_key

    @backoff.on_exception(backoff.expo,
                          Exception,
                          max_tries=3)
    def solve(self, url: str, google_key: str, hcaptcha: bool = False, invisible: bool = False):
        method, key_type = ('hcaptcha', 'sitekey') if hcaptcha else ('userrecaptcha', 'googlekey')
        with requests.get(
                f'https://2captcha.com/in.php?key={self.api_key}&'
                f'method={method}&'
                f'{key_type}={google_key}&'
                f'invisible={1 if invisible else 0}&'
                f'pageurl={url}&'
                f'json=1') as response:
            response_json = response.json()
            print(response_json)
            if response_json['status'] != 1:
                raise Exception('Captcha ERROR')
            _id = response_json['request']
        for _ in range(15):
            time.sleep(10)
            response = requests.get(
                f'https://2captcha.com/res.php?key={self.api_key}&action=get&id={_id}&json=1').json()
            print(response)
            if response['status'] == 1:
                return response['request']
            elif response['request'] != 'CAPCHA_NOT_READY':
                raise Exception(f'Captcha error: {response["request"]}')
        raise Exception('Captcha was not ready in 150 seconds')


if __name__ == '__main__':
    captcha = Captcha('')
    g_response = captcha.solve('WEBSITE_URL', 'GOOGLE_SITE_KEY')
