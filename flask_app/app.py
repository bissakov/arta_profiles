import json
from flask import Flask, request, render_template
from family_data.family import get_family_data


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home() -> str:
    family = None
    data = request.form.get('data', '')
    if request.method == 'POST':
        # result = get_family_data(iin)
        with open(r'D:\Work\python_rpa\arta_profiles\family_data\data.json', 'r', encoding='utf-8') as f:
            family = json.load(f)
    return render_template('index.html', data=data, family=family)


if __name__ == '__main__':
    app.run(debug=True)
