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

from family.custom_exceptions import FamilyNotFound, WrongIIN, WrongPassword, IINNotInSections
from family.family import get_family_data
from excel.excel import get_excel


flask_app = Flask(__name__)
CORS(flask_app)


@flask_app.route('/download_xlsx', methods=['GET'])
def download_xlsx():
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

    flask_app.logger.info(urlparse(request.url))
    flask_app.logger.info(request.path)

    if request.method != 'POST':
        return render_template(base_html, data=iin, family=None, error=None)

    family = None
    error_msg = None

    if iin == '':
        return render_template('base.html', data=iin, family=family, error='Введите ИИН')

    try:
        family = get_family_data(iin)    
    except (FamilyNotFound, WrongIIN, WrongPassword, IINNotInSections) as e:
        error_msg = e.error_msg
    except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError):
        error_msg = 'Нет подключения к VPN на сервере. Свяжитесь с администраторами'

    return render_template('base.html', data=iin, family=family if family else None, error=error_msg)


if __name__ == '__main__':
    flask_app.run()
else:
    logging.basicConfig(filename='record.log', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s',
                        encoding='utf-8')
    logging.getLogger('httpcore').setLevel(logging.WARNING)

    cache = Cache(flask_app, config={'CACHE_TYPE': 'simple'})
