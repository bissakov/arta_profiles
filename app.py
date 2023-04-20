import httpx
from flask import Flask, request, render_template
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from family_selenium.family import get_family_data
from family_selenium.custom_exceptions import FamilyNotFound, WrongPassword, WrongIIN

app = Flask(__name__)

# options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


@app.route('/', methods=['GET', 'POST'])
def home() -> str:
    iin = request.form.get('data', '')

    if request.method != 'POST':
        return render_template('index.html', data=iin, family=None, error=None)

    family = None
    error_msg = None

    try:
        family = get_family_data(iin, driver)
        # with open('test.json', 'r', encoding='utf-8') as f:
        #     family = json.load(f)
    except FamilyNotFound:
        error_msg = 'Семья не найдена. Проверьте ИИН'
    except httpx.HTTPError or WebDriverException:
        error_msg = 'Connection error'
    except WrongPassword:
        error_msg = 'Неправильный пароль. Свяжитесь с администраторами'
    except WrongIIN:
        error_msg = 'Неверный ИИН. ИИН должен состоять из 12 цифр без букв и пробелов'

    import time
    time.sleep(5)

    return render_template('index.html', data=iin, family=family if family else None, error=error_msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
