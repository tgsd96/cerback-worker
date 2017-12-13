from ruamel.yaml import YAML
import MySQLdb

configFile = open("./.config/config.yaml", mode='r')
yaml = YAML()
CONFIGS = yaml.load(configFile.read())
env = 'dev'
DB_HOST = CONFIGS['db'][env]['host']
DB_USER = CONFIGS['db'][env]['user']
DB_PASSWORD = CONFIGS['db'][env]['pass']
DB_NAME = CONFIGS['db'][env]['name']
IMAGE_KEY ="0031a315-2985-4b65-8dcc-95a92d49750e.png"
x = [[0.91,0.11,0.22]] 

try:
    cnx = MySQLdb.connect(DB_HOST,DB_USER,DB_PASSWORD,DB_NAME)
except Exception as err:
    print(err)
print(type(x[0][0]))
sql = "UPDATE `cerback`.`image_statuses` SET `type1` = %f WHERE `image_key` = '%s';"%(x[0][0],IMAGE_KEY)
print(sql)
cnx.cursor().execute(sql)
cnx.commit()
# cnx.cursor().execute(sql,(0.99,IMAGE_KEY))
# cnx.commit()