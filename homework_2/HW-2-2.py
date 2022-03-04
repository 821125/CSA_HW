import json

data_to_write = [
    ('Laptop Lenowo', 1, 25000, 'Petrova L.K.', '2021-12-05'),
    ('Laptop Acer', 2, 45000, 'Ivanov M.K.', '2021-12-05'),
    ('Printer Samsung', 1, 15000, 'Petrov V.D.', '2022-01-05'),
    ('Monitor Samsung', 2, 24000, 'Vasilyev L.K.', '2021-01-05'),
    ('PC Asus', 1, 55000, 'Maksimov V.K.', '2022-01-15')
]

filename = 'orders.json'

def write_order_to_json(item, quantity, price, buyer, date):   
    with open(filename, encoding="utf-8") as file_to_read:
        data = json.loads(file_to_read.read())
    data['orders'].append({
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date
    })
    with open(filename, "w", encoding="utf-8") as file_to_write:
        json.dump(data, file_to_write, indent=4, separators=(',', ': '), ensure_ascii=False)
    print(f'New data was write to {filename}')


for item in data_to_write:
    write_order_to_json(*item)

