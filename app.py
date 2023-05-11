import os
import csv
import io
from typing import Any
import logging
import httpx
from flask import Flask, jsonify, make_response, render_template, request, send_file
from flask_cors import CORS
from flask_caching import Cache
from urllib.parse import urlparse

from family.custom_exceptions import FamilyNotFound, WrongIIN, WrongPassword
from family.family import get_family_data
from excel.excel import get_excel


flask_app = Flask(__name__)
CORS(flask_app)


@flask_app.route('/family', methods=['GET'])
def get_family():
    iin = request.args.get('iin')
    try:
        family_data = get_family_data(iin=iin)
        return jsonify(({'data': family_data, 'success': True}))
    except (FamilyNotFound, WrongIIN, WrongPassword) as e:
        return jsonify({'error_msg': e.error_msg ,'success': False})


def convert_to_csv(family: Any) -> str:
    csv_dict = dict()
    for key, val in family.items():
        if key == 'Члены семьи':
            for i, member in enumerate(val, start=1):
                csv_dict[f'Член семьи {i}'] = f'{member["ИИН"]} {member["ФИО"]}'
        elif type(val) is dict:
            for key2, val2 in val.items():
                csv_dict[key2] = val2
        elif type(val) is list:
            csv_key = 'Рекомендация' if key == 'Рекомендации' else 'Риск'
            for i, el in enumerate(val, start=1):
                csv_dict[f'{csv_key} {i}'] = el

    csv_data = io.StringIO()
    writer = csv.DictWriter(csv_data, fieldnames=csv_dict.keys(), delimiter=';')
    writer.writeheader()
    writer.writerow(csv_dict)
    return csv_data.getvalue()


@flask_app.route('/download_csv', methods=['GET'])
def download_csv():
    # family = cache.get('family')
    iin = request.args.get('iin')
    if not iin:
        raise WrongIIN()
    family = get_family_data(iin=iin)
    response = make_response(convert_to_csv(family=family))
    response.headers.set('Content-Disposition', 'attachment', filename='data.csv')
    response.headers.set('Content-Type', 'text/csv')
    return response


@flask_app.route('/download_xlsx', methods=['GET'])
def download_xlsx():
    # flask_app.logger.info(f'CACHE: {cache}, {type(cache)}')
    # family = cache.get('family')
    # flask_app.logger.info(f'{family}, {type(family)}')
    
    iin = request.args.get('iin')
    flask_app.logger.info(f'IIN: {iin}')
    if not iin:
        raise WrongIIN()
    family = get_family_data(iin=iin)
    return send_file(get_excel(family=family), as_attachment=True)


@flask_app.route('/', methods=['GET', 'POST'])
def index() -> str:
    iin = request.form.get('data', '')

    base_html = 'base.html'
    cache.set('family', None, timeout=43200)

    parse_res = urlparse(request.url)

    flask_app.logger.info(urlparse(request.url))

    if request.method != 'POST':
        return render_template(base_html, url_prefix=parse_res.path, data=iin, family=None, error=None)

    family = None
    error_msg = None

    if iin == '':
        return render_template('base.html', data=iin, family=family, error='Введите ИИН')

    try:
        family = get_family_data(iin)
        # with open('test.json', 'r') as f:
            # family = json.load(f)
        cache.set('family', family, timeout=43200)

    except (FamilyNotFound, WrongIIN, WrongPassword) as e:
        error_msg = e.error_msg
    except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError):
        error_msg = 'Нет подключения к VPN на сервере. Свяжитесь с администраторами'

    return render_template('base.html', url_prefix=parse_res.path, data=iin, family=family if family else None, error=error_msg)


if __name__ == '__main__':
    flask_app.run()
else:
    logging.basicConfig(filename='record.log', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s',
                        encoding='utf-8')
# logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)

    cache = Cache(flask_app, config={'CACHE_TYPE': 'simple'})
