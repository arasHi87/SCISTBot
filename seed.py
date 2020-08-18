import json
import pymongo
from settings import *
from logger import logger

def seeder():
    s_list = json.load(open('data.json', 'r'))['school']
    client = pymongo.MongoClient("mongodb://{}:{}@{}:{}".format(
        DB_USER,
        DB_PASSWORD,
        DB_HOST,
        DB_PORT
    ))

    db = client[DB_NAME]
    s_col = db['school']

    logger.info('start insert school data')

    for data in s_list:
        if not s_col.count_documents({'e_name': data['e_name']}):
            logger.info('insert school {}'.format(data['e_name']))
            s_col.insert_one(data)
        else:
            logger.info('update school {}'.format(data['e_name']))
            s_col.update_one({'e_name': data['e_name']}, {'$set': data})

    logger.info('end insert school')

if __name__ == "__main__":
    seeder()
