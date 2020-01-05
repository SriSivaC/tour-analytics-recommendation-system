import os, sys
ROOT_DIR = '/home/hduser/document/jupyter/FYP/'
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

ATTRACTION_DIR = os.path.abspath('/home/hduser/document/jupyter/FYP/notebook/attraction/') 
if ATTRACTION_DIR not in sys.path:
    sys.path.insert(0, ATTRACTION_DIR)

import flask
from flask import request, jsonify
from pyspark.sql import SparkSession
from attraction_recc import get_recc, filter_df, get_recc_final
import re
from datetime import timedelta, date, datetime

# initiate spark session
spark = SparkSession.builder.appName('attraction').getOrCreate()

# define path
ds_dir = ROOT_DIR + '/crawler/datasets/tripadvisor_dataset/attractions/'
spark_warehouse_dir = ROOT_DIR + '/crawler/datasets/tripadvisor_dataset/attractions/spark-warehouse/'

hyperparameter = {
    'rows': 5000,
    'epochs': 20,
    'batch_size': 8,
    'alpha': 0.01,
    'H': 128
}

# read spark dataframe from parquet
final_attr_spark_df = spark.read.parquet(spark_warehouse_dir + 'etl/attractions')
final_attr_spark_df.createOrReplaceTempView('final_attr_spark_df')

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Travangel Flask API</h1><p>This site is a prototype API for Tour Analytics Final Year Project.</p>"


# A route to return all of the available entries in our database.
@app.route('/api/v1/data/attractions/category', methods=['GET'])
def api_category():
    attr_category_df = final_attr_spark_df.select(final_attr_spark_df.category).distinct().toPandas()

    attr_category_list = attr_category_df.category.tolist()
    attr_category = {'category':[re.sub('_', ' ', cat.capitalize()) for cat in attr_category_list]}

    return jsonify(attr_category)


# A route to return all of the available entries in our database.
@app.route('/api/v1/data/attractions/city', methods=['GET'])
def api_city():
    attr_city_df = final_attr_spark_df.select(final_attr_spark_df.city).distinct().toPandas()

    attr_city_list = attr_city_df.city.tolist()
    attr_city = {'city': attr_city_list}

    return jsonify(attr_city)


# A route to return all of the available entries in our database.
@app.route('/api/v1/data/attractions/price', methods=['GET'])
def api_price():
    attr_price_spark_df = spark.sql("SELECT MIN(price) as min_price, MAX(price) as max_price FROM final_attr_spark_df")

    attr_price_df = attr_price_spark_df.toPandas()
    attr_price = {'min_price': attr_price_df.min_price[0], 'max_price': attr_price_df.max_price[0]}

    return jsonify(attr_price)


# A route to return all of the available entries in our database.
@app.route('/api/v1/data/attractions/recommendation', methods=['GET'])
def api_attr_recc():

    if 'location' in request.args:
        location = str(request.args['location'])
        location = re.sub('_', ' ', location).title()
    else:
        return "Error: No location field provided. Please specify a location."

    if 'start_date' in request.args:
        start_date = str(request.args['start_date'])
    else:
        return "Error: No start_date field provided. Please specify a start_date."

    if 'end_date' in request.args:
        end_date = str(request.args['end_date'])
    else:
        return "Error: No end_date field provided. Please specify a end_date."

    attr_category_df = final_attr_spark_df.select(final_attr_spark_df.category).distinct().toPandas()
    attr_price_spark_df = spark.sql("SELECT MIN(price) as min_price, MAX(price) as max_price FROM final_attr_spark_df")

    attr_category_list = attr_category_df.category.tolist()
    attr_price_df = attr_price_spark_df.toPandas()
    budget_low = attr_price_df.min_price[0]
    budget_high = attr_price_df.max_price[0]

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    cat_rating = {key: float(5.0) for key in attr_category_list}

    filename, user, rbm_att = get_recc(spark, cat_rating, hyperparameter)
    with_url = filter_df(spark, filename, user, budget_low, budget_high, location, final_attr_spark_df.toPandas())
    final = get_recc_final(with_url, start_date, end_date)

    return jsonify(final)


# A route to return all of the available entries in our database.
@app.route('/api/v1/data/attractions/triplaner', methods=['GET'])
def api_triplanner():

    if 'location' in request.args:
        location = str(request.args['location'])
        location = re.sub('_', ' ', location).title()
    else:
        return "Error: No location field provided. Please specify a location."

    if 'start_date' in request.args:
        start_date = str(request.args['start_date'])
    else:
        return "Error: No start_date field provided. Please specify a start_date."

    if 'end_date' in request.args:
        end_date = str(request.args['end_date'])
    else:
        return "Error: No end_date field provided. Please specify a end_date."

    if 'budget_low' in request.args:
        budget_low = float(request.args['budget_low'])
    else:
        return "Error: No budget_low field provided. Please specify a budget_low."

    if 'budget_high' in request.args:
        budget_high = float(request.args['budget_high'])
    else:
        return "Error: No budget_high field provided. Please specify a budget_high."

    if 'category' in request.args:
        category = str(request.args['category'])
    else:
        return "Error: No cat_rating field provided. Please specify a cat_rating."

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    attr_category_list = category.split('+')
    cat_rating = {key: float(5.0) for key in attr_category_list}

    filename, user, rbm_att = get_recc(spark, cat_rating, hyperparameter)
    with_url = filter_df(spark, filename, user, budget_low, budget_high, location, final_attr_spark_df.toPandas())
    final = get_recc_final(with_url, start_date, end_date)

    return jsonify(final)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8121)
