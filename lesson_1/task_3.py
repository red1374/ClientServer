def is_byte_convertable(str):
    """
    Checks if string can be converted into a byte string
    :param str: input string
    :return:
    """
    try:
        bytes_string = eval(f'b"{str}"')
    except SyntaxError:
        return False

    return True


string_list = ('attribute', 'класс', 'функция', 'type')

for str in string_list:
    print(str, '- is', end='')
    if not is_byte_convertable(str):
        print(' not', end='')
    print(' convertable into bytes!')
