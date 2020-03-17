"""Data Science Assignment Submission"""
import json
from functools import partial
from numbers import Number
from statistics import mean

import flask
import pandas as pd
from jsonschema.exceptions import ValidationError
from flask import jsonify, request
from flask_cors import CORS

from json_validator import input_validator

df = pd.read_json("netaporter.json", lines=True)

app = flask.Flask(__name__)
CORS(app)

validator = input_validator()

def discount_percentage(price):
    offer_price = price['offer_price']['value']
    regular_price = price['regular_price']['value']
    return (regular_price - offer_price) / regular_price * 100


def filter_by_discount_op_n(operator, n, price):
    discount = discount_percentage(price)

    if operator == '>':
        return discount > n
    if operator == '==':
        return discount == n
    if operator == '<':
        return discount < n

def filter_by_discount(operator, percent):
    return partial(filter_by_discount_op_n, operator, percent)


def get_discounts(price):
    discount = discount_percentage(price)
    return discount


@app.route('/', methods=['POST'])
def main():
    try:
        data = json.loads(request.data)
        validator.validate(data)
    except ValidationError:
        return jsonify(error=True, msg="JSON data invalid")
    except:
        return jsonify(error=True, msg="Invalid POST data")

    query_types = list(data['query_type'].split('|'))
    returns = {}

    for _filter in data['filters']:
        if _filter['operand1'] == 'discount':
            if not isinstance(_filter['operand2'], Number):
                return jsonify(error=True, msg="Discount percentage is not a number")

            operator = _filter['operator']
            percent = _filter['operand2']

            filtered_data = df[df.price.apply(filter_by_discount(operator, percent))]

            if "discounted_products_list" in query_types:
                returns.update(
                    {'discounted_products_list': [x['$oid'] for x in filtered_data._id]})

            if "avg_discount" in query_types:
                discounts = filtered_data.price.apply(get_discounts)
                avg_discount = mean(discounts) if len(discounts) > 0 else 0
                returns.update({'avg_discount': avg_discount})

    return jsonify(returns)

if __name__ == "__main__":
    app.run(port=5000)
