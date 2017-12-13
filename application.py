# imports
import os
import json
import logging
import flask
from flask import request, Response
import boto3
import MySQLdb
import botocore
import matplotlib.image as mpimg
import matplotlib.pyplot as pplot
from scipy.misc import imresize
import numpy as np
from keras.models import load_model
from ruamel.yaml import YAML


'''
    Generate constants from config file
'''
configFile = open("./.config/config.yaml", mode='r')
yaml = YAML()
CONFIGS = yaml.load(configFile.read())
env = os.environ.get('RUN_ENV')
DB_HOST = CONFIGS['db'][env]['host']
DB_USER = CONFIGS['db'][env]['user']
DB_PASSWORD = CONFIGS['db'][env]['pass']
DB_NAME = CONFIGS['db'][env]['name']
MODEL_NAME = CONFIGS['dl']['model_name']
API_ENDPOINT = CONFIGS['api']['daemon']
BUCKET_NAME = CONFIGS['aws']['bucket_name']
IMAGE_NAME = CONFIGS['aws']['image_name']
IMAGE_KEY = CONFIGS['aws']['image_key']
USER_ID = CONFIGS['aws']['user_id']
IMAGE_X = CONFIGS['dl']['dim']['x']
IMAGE_Y = CONFIGS['dl']['dim']['y']
IMAGE_Z = CONFIGS['dl']['dim']['z']

model = load_model(MODEL_NAME)
s3 = boto3.resource('s3',use_ssl=False)

# # Create and config flask app
application = flask.Flask(__name__)
try:
    cnx = MySQLdb.connect(DB_HOST,DB_USER,DB_PASSWORD,DB_NAME)
except Exception as err:
    print(err)

# the endpoint that receives the messages
@application.route(API_ENDPOINT,methods=['POST'])
def process_image():
    response = None
    if request.json is None:
        response = Response("",status=415)
    else:
        message = dict()
        try:
            message = request.json
            try:
                s3.Bucket(BUCKET_NAME).download_file(message[IMAGE_KEY], IMAGE_NAME)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("The object does not exist.")
                else:
                    raise
            print(message[IMAGE_KEY])
            image = mpimg.imread(IMAGE_NAME)
            I = imresize(image,(IMAGE_X,IMAGE_Y,IMAGE_Z))
            I = np.reshape(I,(1,)+I.shape)
            x = model.predict(I,batch_size=1)
            print(x)
            ## write to db
            # print(x[0][0].item())
            sql = "UPDATE `cerback`.`image_statuses` SET `type1` = %f, `type2` = %f, `type3`=%f, `status` = 'PROCESSED' WHERE `image_key` = '%s';"%(x[0][0].item(),x[0][1].item(),x[0][2].item(),message[IMAGE_KEY])
            print(sql)
            cnx.cursor().execute(sql)
            cnx.commit()
            response = Response("Done",status=200)
        except Exception as ex:
            logging.exception('Error processing message: %s'% request.json)
            response = Response(ex.message, status=500)
    return response
if __name__ == '__main__':
    application.run(host='0.0.0.0')