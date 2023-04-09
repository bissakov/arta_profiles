from flask import Flask, request, render_template
from family_data.family import get_family_data


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    data = request.form.get('data', '')
    if request.method == 'POST':
        iin = request.form['data']
        # result = get_family_data(iin)
        result = iin
    return render_template('index.html', data=data, result=result)


if __name__ == '__main__':
    app.run(debug=True)
