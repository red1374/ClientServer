import random

from chardet import detect

input_list = ('сетевое программирование', 'сокет', 'декоратор')
encoding_list = ('cp1251', 'utf8', 'utf16')
files_list = ('test1.txt', 'test2.txt', 'test3.txt')


def create_file(file_name, input_list, encoding):
    """
    Create file with name file_name and data input_list in a given encoding
    :param file_name:
    :param input_list:
    :param encoding:
    :return:
    """
    f = open(file_name, 'w', encoding=encoding)
    for item in input_list:
        f.write(item + "\n")
    f.close()


def print_file_content(file_name):
    """
    Print out given file content
    :param file_name:
    :return:
    """
    with open(file_name, 'rb') as f:
        content = f.read()

    encoding = detect(content)['encoding']
    print(f'{file_name} ({encoding})')
    print('Content:')
    print(content.decode(encoding))


"""
Create files at random encoding
"""
for file_name in files_list:
    create_file(file_name, input_list, random.choice(encoding_list))

"""
Print out file encoding and its content
"""
for file_name in files_list:
    print_file_content(file_name)
