from flask import Flask, request, render_template
from family_data.family import get_family_data


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    iin = request.form['data']
    result = get_family_data(iin)
    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
