from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import json
import os 
import pandas as pd
import pickle

from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

app = Flask(__name__)

df = pd.read_csv('cannabis.csv')

# creates the flask app and configures it. 
def create_app():
    """ Create and configure flask app"""
    app = Flask(__name__)
    CORS(app)

    # configure the database:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cannabis.sqlite3'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # suppress warning messages
    DB = SQLAlchemy(app)

    return app


@app.route('/')
def root():
    return "We have the best app"

# Load the model from file 

tfidf = pickle.load(open("pickled_files/vect_01.pkl", "rb"))
nn_model = pickle.load(open("pickled_files/knn_02.pkl", "rb"))

# GOING TO NEED TO CREATE A FUNCTION TO PARSE
# THE JSON DICTIONARY SENT TO US TO MATCH THE BELOW 
# PYTHON DICTIONARY.

def get_user_inputs(data):
        user_desc = ''
        for index in data:
            for values in data[index]:
                user_desc += '\n' + values
        return tfidf.transform([user_desc])


def output_user_reccomendations(query, dframe):
    _, similar_topic_indices = nn_model.kneighbors(query.todense())
    indices = list(similar_topic_indices[0])
    recc_values = []
    
    def get_index_values(index):
        output_values = {
        'ID':[],
        'Strain':[], 
        'Type':[], 
        'Rating':[], 
        'Flavor':[], 
        'Effects':[], 
        'Description':[]}
        output_values['Strain'].append(dframe['Strain'][index])

        return output_values['Strain'][0]
    for key in range(0, len(indices)):
        recc_values.append(get_index_values(indices[key]))
    return recc_values


def predict(user_inputs):
    """
    Takes a users perferences/symptoms are uses a prediction model to 
    return the best cannabis strains for that user. 
    """
    strain_query = get_user_inputs(user_inputs)
    reccomondations = output_user_reccomendations(strain_query, df)
    return reccomondations


@app.route('/recommendations/<effects>/<flavors>/<ailments>', methods=['GET', 'POST'])
def recommends(effects,flavors,ailments):
    
    user_inputs = {
        'effects': list(effects.split()),
        'flavors': list(flavors.split()),
        'ailments': list(ailments.split())
    }
    content = request.json
    print(content)
    # return jsonify(content)
    prediction = predict(user_inputs)
    return jsonify(prediction)


# optional route to display all strains if we want to 
# @app.route("/strains")
# def strains():
#     """
#     Function: returns a list of all the cannbais strains.
#     Returns: list of strains as a JSON array
#     """
#     try:
#         all_strains = df.to_json(orient="records")
#     except Exception as e:
#         raise e

#     return(all_strains)
