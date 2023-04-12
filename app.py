import json
from flask import Flask, request, render_template
from family_data.family import get_family_data
from family_data.entities import Family
from family_data.utils import FamilyNotFound


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home() -> str:
    family = None
    error_msg = None
    iin = request.form.get('data', '')
    if request.method == 'POST':
        try:
            family = get_family_data(iin)
        except FamilyNotFound:
            error_msg = 'Неправильный ИИН'
    return render_template('index.html', data=iin, family=family.to_dict() if family else None, error=error_msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
