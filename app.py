"""Data Science Assignment Submission"""
import json
from functools import partial
from numbers import Number
from statistics import fmean

import flask
import pandas as pd
from jsonschema.exceptions import ValidationError
from flask import jsonify, request
from flask_cors import CORS

from json_validator import input_validator


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


def filter_by_brand_name(brand_name, brand):
    return brand['name'] == brand_name

def filter_by_brand(brand_name):
    return partial(filter_by_brand_name, brand_name)


def filter_by_expensive_product(product):
    basket_price = product['price']['basket_price']['value']
    for res in product.similar_products['website_results'].values():
        for item in res['knn_items']:
            if item['_source']['price']['basket_price']['value'] < basket_price:
                return True

    return False


df = pd.read_json("netaporter.json", lines=True)

app = flask.Flask(__name__)
CORS(app)

validator = input_validator()


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

    filtered_data = df
    for _filter in data.get('filters', []):
        if _filter['operand1'] == 'discount':
            if not isinstance(_filter['operand2'], Number):
                return jsonify(error=True, msg="Discount percentage is not a number")

            operator = _filter['operator']
            percent = _filter['operand2']

            filtered_data = filtered_data[
                filtered_data.price.apply(filter_by_discount(operator, percent))]

        elif _filter['operand1'] == 'brand.name':
            operator = _filter['operator']
            if operator != '==':
                return jsonify(error=True, msg="To filter by brand name, use operator '=='")

            brand_name = _filter['operand2']
            filtered_data = filtered_data[
                filtered_data.brand.apply(filter_by_brand(brand_name))]


    if "discounted_products_list" in query_types:
        returns.update(
            {'discounted_products_list': [x['$oid'] for x in filtered_data._id]})

    if "avg_discount" in query_types:
        discounts = filtered_data.price.apply(discount_percentage)
        avg_discount = fmean(discounts) if len(discounts) > 0 else 0.0
        returns.update({'avg_discount': avg_discount})

    if "expensive_list" in query_types:
        expensive_list = filtered_data[
            filtered_data.apply(filter_by_expensive_product, axis=1)]

        returns.update({'expensive_list': [x['$oid'] for x in expensive_list._id]})


    return jsonify(returns)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
