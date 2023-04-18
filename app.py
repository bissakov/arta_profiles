import json
import httpx
from flask import Flask, request, render_template
from family_data.family import get_family_data
from family_data.entities import Family
from family_data.utils import FamilyNotFound, WrongPassword, FamilyNotInList


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home() -> str:
    iin = request.form.get('data', '')

    if request.method != 'POST':
        return render_template('index.html', data=iin, family=None, error=None)

    family = None
    error_msg = None

    try:
        family = get_family_data(iin)
    except FamilyNotFound:
        error_msg = 'Неправильный ИИН'
    except httpx.HTTPError:
        error_msg = 'Connection error'
    except WrongPassword:
        error_msg = 'Неправильный пароль. Свяжитесь с администраторами'
    except FamilyNotInList:
        error_msg = 'ИИН не найден в списке "Потенциальные получатели АСП с детьми"'

    return render_template('index.html', data=iin, family=family.to_dict() if family else None, error=error_msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
