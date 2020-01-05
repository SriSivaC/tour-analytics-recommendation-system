import os
import math
from utils import Util
from rbm import RBM

from google_images_download import google_images_download
from nltk.corpus import wordnet
import nltk
nltk.download('wordnet')

# define path
ROOT_DIR = os.path.abspath('/home/hduser/document/jupyter/FYP/')
ds_dir = ROOT_DIR + '/crawler/datasets/tripadvisor_dataset/attractions/'
spark_warehouse_dir = ROOT_DIR + '/crawler/datasets/tripadvisor_dataset/attractions/spark-warehouse/'
rbm_models_dir = ROOT_DIR + '/notebook/attraction/rbm_models/'


def f(row):
    avg_cat_rat = dict()
    for i in range(len(row['category'])):
        if row['category'][i] not in avg_cat_rat:
            avg_cat_rat[row['category'][i]] = [row['rating'][i]]
        else:
            avg_cat_rat[row['category'][i]].append(row['rating'][i])
    for key, value in avg_cat_rat.items():
        avg_cat_rat[key] = sum(value)/len(value)
    return avg_cat_rat


def sim_score(row):
    score = 0.0
    match = 0
    col1 = row['cat_rat']
    col2 = row['user_data']
    for key, value in col2.items():
        if key in col1:
            match += 1
            score += (value-col1[key])**2
    if match != 0:
        return ((math.sqrt(score)/match) + (len(col2) - match))
    else:
        return 100


def get_recc(spark, cat_rating, hyperparameter):

    util = Util()
    # reading
    attractions, ratings = util.read_data(spark, spark_warehouse_dir + 'etl/attractions'), util.read_data(spark, spark_warehouse_dir + 'etl/attraction_reviews')
    # processing
    ratings = util.clean_subset(ratings, hyperparameter['rows'])
    rbm_att, train = util.preprocess(ratings)
    # modeling
    num_vis = len(ratings)
    rbm = RBM(hyperparameter['alpha'], hyperparameter['H'], num_vis)
    # joining
    joined = ratings.set_index('activityId').join(
        attractions[["activityId", "category"]].set_index("activityId")).reset_index('activityId')
    joined['user_id'] = joined.index
    # grouping
    grouped = joined.groupby('user_id')
    category_df = grouped['category'].apply(list).reset_index()
    rating_df = grouped['rating'].apply(list).reset_index()
    # applying
    cat_rat_df = category_df.set_index('user_id').join(rating_df.set_index('user_id'))
    cat_rat_df['cat_rat'] = cat_rat_df.apply(f, axis=1)
    cat_rat_df = cat_rat_df.reset_index()[['user_id', 'cat_rat']]
    cat_rat_df['user_data'] = [cat_rating for i in range(len(cat_rat_df))]
    cat_rat_df['sim_score'] = cat_rat_df.apply(sim_score, axis=1)
    user = cat_rat_df.sort_values(['sim_score']).values[0][0]
    # showing
    print("Similar User: {u}".format(u=user))
    filename = "e"+str(hyperparameter['epochs'])+"_r"+str(hyperparameter['rows'])+"_lr" + \
        str(hyperparameter['alpha'])+"_hu"+str(hyperparameter['H'])+"_bs"+str(hyperparameter['batch_size'])
    # loading
    reco, weights, vb, hb = rbm.load_predict(filename, train, user)
    # calculating
    unseen, seen = rbm.calculate_scores(ratings, attractions, reco, user)
    # exporting
    rbm.export(unseen, seen, rbm_models_dir + filename, str(user))
    return filename, user, rbm_att


def filter_df(spark, filename, user, budget_low, budget_high, destination, att_df):
    df = spark.read.csv(rbm_models_dir + filename + '/user{u}_unseen.csv'.format(u=user), header=True, sep=",")
    recc_df = df.toPandas().set_index('_c0')
    del recc_df.index.name
    recc_df.columns = ['activityId', 'att_name', 'att_cat', 'att_price', 'score']

    recommendation = att_df[[
        'activityId', 'name', 'category', 'city', 'state', 'latitude',
        'longitude', 'price', 'rating'
    ]].set_index('activityId').join(recc_df[['activityId',
                                             'score']].set_index('activityId'),
                                    how="inner").reset_index().sort_values(
                                        "score", ascending=False)

    filtered = recommendation[(recommendation.city == destination)
                              & (recommendation.price >= budget_low) &
                              (recommendation.price <= budget_high)]

    # read spark dataframe from parquet
    attr_href_cat_spark_df = spark.read.parquet(ds_dir + 'tripadvisor_attr_href_cat')
    attr_href_cat_spark_df = attr_href_cat_spark_df.drop('_corrupt_record')
    attr_href_cat_spark_df = attr_href_cat_spark_df.dropna()
    attr_href_cat_df = attr_href_cat_spark_df.toPandas()
    # add activityId columns to dataframe
    attr_href_cat_df['activityId'] = attr_href_cat_df['href'].str.extract(r'd(\d+)', expand=True)

    with_url = filtered.set_index('activityId').join(attr_href_cat_df[['activityId', 'href']].set_index('activityId'), how="inner")
    return with_url


def get_place_photo_url(place, width=500):
    response = google_images_download.googleimagesdownload()  # class instantiation
    arguments = {
        "keywords": place.encode("ascii", errors="ignore").decode(),
        "limit": 1,
        "print_urls": True,
        "no_download": True
    }  # creating list of arguments
    paths = response.download(arguments)  # passing the arguments to the function
    try:
        return list(paths[0].values())[0][0]
    except:
        get_place_photo_url(place)


def top_recc(with_url, final):
    for i in range(len(with_url)):
        first_recc = with_url.iloc[[i]]

        if (first_recc['name'].values.T[0] not in final['name']):
            final['name'].append(first_recc['name'].values.T[0])
            final['location'].append(first_recc[['latitude', 'longitude'
                                                 ]].values.tolist()[0])
            final['price'].append(first_recc['price'].values.T[0])
            final['rating'].append(first_recc['rating'].values.T[0])
            final['category'].append(first_recc['category'].values.T[0])
            final['image'].append(get_place_photo_url(first_recc['name'].values.T[0]))
            return final
    return final


def find_closest(with_url, loc, tod, final):
    syns1 = wordnet.synsets("evening")
    syns2 = wordnet.synsets("night")

    evening = [word.lemmas()[0].name() for word in syns1
               ] + [word.lemmas()[0].name() for word in syns2]

    distance = list()
    for i in with_url[['latitude', 'longitude']].values.tolist():
        loc[0] = float(loc[0])
        loc[1] = float(loc[1])
        i[0] = float(i[0])
        i[1] = float(loc[1])
        distance.append(math.sqrt((loc[0] - i[0])**2 + (loc[1] - i[1])**2))

    with_dist = with_url
    with_dist["distance"] = distance
    sorted_d = with_dist.sort_values(['distance', 'price'],
                                     ascending=['True', 'False'])
    if tod == "Evening":
        mask = sorted_d.name.apply(lambda x: any(j in x for j in evening))
    else:
        mask = sorted_d.name.apply(lambda x: all(j not in x for j in evening))
    final = top_recc(sorted_d[mask], final)
    return final


def get_recc_final(with_url, start_date, end_date):
    final = dict()
    final['timeofday'] = []
    final['name'] = []
    final['location'] = []
    final['price'] = []
    final['rating'] = []
    final['category'] = []
    final['image'] = []

    # 4 recommeded attraction per day, two for morning and two for evening
    for i in range((end_date - start_date).days + 1):
        for j in range(2):
            final['timeofday'].append('Morning')
        for j in range(2):
            final['timeofday'].append('Evening')

    for i in range(len(final['timeofday'])):  # 16
        if i % 4 == 0:
            final = top_recc(with_url, final)
        else:
            if i == len(final['name']):
                final = top_recc(with_url, final)
            else:
                final = find_closest(with_url, final['location'][-1],
                                     final['timeofday'][i], final)

    return final
