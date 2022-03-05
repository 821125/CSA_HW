import yaml


filename = 'file.yaml'

data = {
    'items': ['laptop', 'monitor', 'pc', 'printer'],
    'items_quantity': 4,
    'items_price': {
        'laptop': '400€',
        'monitor': '300€',
        'pc': '400€',
        'printer': '500€'
    }
}

with open(filename, 'w', encoding='utf-8') as file_to_open:
    yaml.dump(data, file_to_open, default_flow_style=False, allow_unicode=True)

with open(filename, 'r', encoding='utf-8') as file_to_read:
    data_file = file_to_read.read()

print(data_file)
