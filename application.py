
# imports

import json
import logging
import flask
from flask import request, Response
import boto3
import pymysql
import botocore
import os
import matplotlib.image as mpimg
import matplotlib.pyplot as pplot
from scipy.misc import imresize
import numpy as np
from keras.models import load_model
model = load_model('bottleneck_fc_model2.h5')

s3 = boto3.resource('s3',use_ssl=False)
BUCKET_NAME = "cerbackimageuploads"
KEY = "0031a315-2985-4b65-8dcc-95a92d49750e.png"

# # Create and config flask app
application = flask.Flask(__name__)
# try:
#     cnx = pymysql.connect(user="admin",password="H?!A4gkm",host="cerbackmain.cpkl1sz5etxf.us-west-2.rds.amazonaws.com",database="cerback")
# except Exception as err:
#     print(err)

# try:
#     with cnx.cursor() as cursor:
#         sql = "SELECT * FROM `image_statuses`"
#         cursor.execute(sql)
#         result = cursor.fetchone()
#         print(result)
# finally:
#     cnx.close()


# the endpoint that receives the messages
@application.route('/process-image',methods=['POST'])
def process_image():
    response = None
    if request.json is None:
        response = Response("",status=415)
    else:
        message = dict()
        try:
            message = request.json
            try:
                s3.Bucket(BUCKET_NAME).download_file(message["image_key"], 'my_local_image.jpg')
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("The object does not exist.")
                else:
                    raise
            print(message['image_key'])
            image = mpimg.imread('my_local_image.jpg')
            I = imresize(testIm,(240,320,3))
            I = np.reshape(I,(1,)+I.shape)
            model.predict(I,batch_size=1)
            response = Response("",status=200)
        except Exception as ex:
            logging.exception('Error processing message: %s'% request.json)
            response = Response(ex.message, status=500)
    return response
if __name__ == '__main__':
    application.run(host='0.0.0.0')