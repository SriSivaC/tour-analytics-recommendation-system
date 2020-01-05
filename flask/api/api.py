import flask
from flask import request, jsonify
from pyspark.sql import SparkSession
# from attraction_recc import *
import sys

# initiate spark session
spark = SparkSession.builder.appName('attraction').getOrCreate()

ROOT_DIR = '/home/hduser/document/jupyter/FYP/'
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

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

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Travangel Flask API</h1><p>This site is a prototype API for Tour Analytics Final Year Project.</p>"

# A route to return all of the available entries in our catalog.
@app.route('/api/v1/data/attractions/category', methods=['GET'])
def api_category():
    # read spark dataframe from parquet
    final_attr_spark_df = spark.read.parquet(spark_warehouse_dir + 'etl/attractions')
    attr_category_df = final_attr_spark_df.select(final_attr_spark_df.category).distinct().toPandas()
    attr_category_list = attr_category_df.category.tolist()
    return jsonify(attr_category_list)


@app.route('/api/v1/resources/books', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."

    # Create an empty list for our results
    results = []

    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    for book in books:
        if book['id'] == id:
            results.append(book)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0')
