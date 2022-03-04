import re

os_prod_list = []
os_name_list = []
os_code_list = []
os_type_list = []
main_data = [[
    'Изготовитель системы',
    'Название ОС',
    'Код продукта',
    'Тип системы'
]]

def get_data():
    data = []
    dirctory_items = list(filter(lambda x: '.txt' in x, os.listdir()))
    for filename in dirctory_items:
        with open(filename) as file:
            for line in file.readlines():
                data += re.findall(r'^(\w[^:]+).*:\s+([^:\n]+)\s*$', line)
    for item in data:
        os_prod_list.append(item[1]) if item[0] == main_data[0][0] else None
        os_name_list.append(item[1]) if item[0] == main_data[0][1] else None
        os_code_list.append(item[1]) if item[0] == main_data[0][2] else None
        os_type_list.append(item[1]) if item[0] == main_data[0][3] else None
    for i in range(len(os_prod_list)):
        main_data.append([os_prod_list[i], os_name_list[i], os_code_list[i], os_type_list[i]])
    return main_data

def write_to_csv(file_path):
    data = get_data()
    with open(file_path, 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        for line in data:
            writer.writerow(line)
    print(f'Data was write to {file_path}')

write_to_csv('data_report.csv')