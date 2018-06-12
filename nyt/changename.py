import os
import json
from datetime import datetime


for filename in os.listdir('nyt/archive'):
    with open('nyt/archive/' + filename) as infile:
        date_obj = datetime.strptime(filename.split('.')[0], '%Y%m%d')
        new_filename = date_obj.strftime('%Y-%m-%d.json')
        os.rename('nyt/archive/' + filename, 'nyt/archive/' + new_filename)
