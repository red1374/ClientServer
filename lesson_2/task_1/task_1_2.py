from chardet import detect
import locale
import re
import csv

default_encoding = locale.getpreferredencoding()
file_list = ('info_1.txt', 'info_2.txt', 'info_3.txt')
data_search_list = ('Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы')
main_data = []


def get_values(file_data, search_list):
    """
    Get values by searching string from a file data
    :param file_data: file data string
    :param search_list: searching string list
    :return: values of a searching strings
    """
    if file_data is None or data_search_list is None:
        return False

    result = []
    for search_item in search_list:
        match = re.search(eval(f'r"^{search_item}\:\s*[\S, ]+"'), file_data, flags=re.MULTILINE)
        if match[0] is None:
            result.append('--')
        else:
            result.append(match[0].replace(search_item + ':', '').replace("\t", '').strip())

    return result


def get_data(file_list, search_list):
    """
    Get searching data from files
    :param file_list: list of file names
    :param search_list: list for searching strings
    :return:
    """
    data = []
    if file_list is None or search_list is None:
        return False

    for file_name in file_list:
        with open(file_name, 'rb') as f:
            content = f.read()

            encoding = detect(content)['encoding']
            if default_encoding != encoding:
                str = content.decode(encoding=encoding)
                content = str.encode(default_encoding)

            data.append(get_values(content.decode(encoding=default_encoding), search_list))

    return data


def write_to_csv(file_name, data):
    """
    Write data to csv file
    :param file_name: new csv file name
    :param data: data to write
    :return:
    """
    if file_name is None or data is None:
        return False

    with open(file_name, 'w', encoding=default_encoding, newline='') as f_n:
        F_N_WRITER = csv.writer(f_n, quoting=csv.QUOTE_NONNUMERIC)
        F_N_WRITER.writerows(data)

    return True


# Get data from files
files_data = get_data(file_list, data_search_list)

# Add table headers
main_data.append(list(data_search_list))
for file_line in files_data:
    main_data.append(file_line)

# Write data to csv file
write_to_csv('summery.csv', main_data)
