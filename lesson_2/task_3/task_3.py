import yaml

data = {
    'list': [
        'item 1',
        'item 2',
        'item 3',
        'item 4'
    ],
    'integer': 5,
    'dict': {
        'k€y1': 'value',
        'k€y2': 5,
        'k€y3': 'value 1'
    }
}

with open('file.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

with open('file.yaml', encoding='utf-8') as f:
    data_from_file = yaml.load(f, Loader=yaml.FullLoader)

# Check that the data from file are equal to source object
if data_from_file == data:
    print('Data from file are equal to to source object!')
else:
    print('Something wrong')
