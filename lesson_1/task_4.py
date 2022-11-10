def into_bytes_and_back(str):
    """
    Converting string into bytes and back
    :param str: string
    :return:
    """
    print("** Input string:", str)

    bytes_string = str.encode('utf-8')
    print('Encoded:')
    print(type(bytes_string), bytes_string)

    print('Decoded:')
    decoded_string = bytes_string.decode('utf-8')
    print(type(decoded_string), decoded_string, "\n\n")


string_list = ('разработка', 'администрирование', 'protocol', 'standard')

for str in string_list:
    into_bytes_and_back(str)
