import pandas as pd

from repository import Repository


data = pd.read_csv('test.csv').drop(columns=['index'])

repo = Repository('repository.db')
records = data.to_dict(orient='records')
repo.add_prompts(records)
print('Done.')
