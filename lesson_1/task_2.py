def get_bytes(string_list):
    """
    Get byte string from a string
    :param string_list: string list items
    :return:
    """
    for str in string_list:
        bytes_string = eval(f'b"{str}"')
        print(type(bytes_string))
        print(bytes_string)
        print("String length: ", len(bytes_string))


string_list = ('class', 'function', 'method')

get_bytes(string_list)
