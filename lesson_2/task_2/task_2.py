import json


def write_order_to_json(item, quantity, price, buyer, date):
    """
    Write order data to aa orders files
    :param item:
    :param quantity:
    :param price:
    :param buyer:
    :param date:
    :return:
    """
    order = {
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date
    }
    # Read data from file
    with open('orders.json', encoding='utf-8') as f:
        data = json.load(f)

        data['orders'].append(order)

    # Write data to file
    with open('orders.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


write_order_to_json('Товар 1', 2, 5200, 'Иванов Иван Иванович', '12.10.2022')
write_order_to_json('Товар 2', 5, 2700, 'Петров Петр Петрович', '22.10.2022')
write_order_to_json('Товар 1', 1, 2600, 'Сергеев Сергей Сергеевич', '29.11.2022')
write_order_to_json('Товар 3', 2, 5720, 'Григорьев Григорий Григориевич', '02.12.2022')
