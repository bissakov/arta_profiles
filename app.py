import httpx
from flask import Flask, json, request, render_template, jsonify

from family.custom_exceptions import FamilyNotFound, WrongPassword, WrongIIN
from family.family import get_family_data


app = Flask(__name__)


@app.route('/family', methods=['GET'])
def get_family():
    iin = request.args.get('iin')
    try:
        family_data = get_family_data(iin=iin)
        return jsonify(({'data': family_data, 'success': True}))
    except (FamilyNotFound, WrongIIN, WrongPassword) as e:
        return jsonify({'error_msg': e.error_msg ,'success': False})



@app.route('/', methods=['GET', 'POST'])
def index() -> str:
    iin = request.form.get('data', '')

    base_html = 'base.html'

    if request.method != 'POST':
        return render_template(base_html, data=iin, family=None, error=None)

    family = None
    error_msg = None

    if iin == '':
        return render_template('base.html', data=iin, family=family, error='Введите ИИН')

    try:
        family = get_family_data(iin)
    except FamilyNotFound:
        error_msg = 'Семья не найдена. Проверьте ИИН'
    except httpx.ConnectTimeout:
        error_msg = 'Нет подключения к VPN на сервере. Свяжитесь с администраторами'
    except WrongPassword:
        error_msg = 'Неправильный пароль. Свяжитесь с администраторами'
    except WrongIIN:
        error_msg = 'Неверный ИИН. ИИН должен состоять из 12 цифр без букв и пробелов'

    return render_template('base.html', data=iin, family=family if family else None, error=error_msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

