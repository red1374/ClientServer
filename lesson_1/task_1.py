def show_str_info(string_list):
    """
    Show list item type and data
    :param string_list: string items list
    :return:
    """
    for str in string_list:
        print(type(str))
        print(str)


string_list = ('разработка', 'сокет', 'декоратор')
unicode_string_list = (
    '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
    '\u0441\u043e\u043a\u0435\u0442',
    '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440',
)

print(8 * '*', ' Simple Strings ', 8 * '*')
show_str_info(string_list)

print("\n", 8 * '*', ' Strings at Unicode ', 8 * '*')
show_str_info(unicode_string_list)

