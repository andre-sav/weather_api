from flask import Flask, jsonify, render_template
import openaq
import json
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)

class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return '<Value %r>' % (self.value)

api = openaq.OpenAQ()

def extraction(body):
    results = []
    for item in body:
        for data in body['results']:
            result_tuple = tuple([data['date']['utc'], data['value']])
            results.append(result_tuple)
    return results
            
@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # TODO Get data from OpenAQ, make Record objects with it, and add to db
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    for item in body:
        for data in body['results']:
            record = Record(datetime=str(data['date']['utc']), value=data['value'])
            DB.session.add(record)
            DB.session.commit()
    return 'Data refreshed!'

# @APP.route('/')
# def root():
#     status, body = api.measurements(city='Los Angeles', parameter='pm25')
#     results = extraction(body)
#     result = json.dumps(results)
#     return result

@APP.route('/')
def root():
    res = Record.query.filter(Record.value>=10).all()
    for temp in res:
        print(temp.datetime)
    return render_template('index.html', res=res)
