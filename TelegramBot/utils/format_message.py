
# Форматирование сообщения в таблицу
def format_str(add_str:str, k_args, max_len = 35):
    cell_len = int(max_len/k_args)
    str_len = len(add_str) 

    result_str = add_str

    if cell_len - str_len <= 0:
        return (result_str + f" ")
    
    for i in range(cell_len - str_len):
        result_str += " "

    return result_str
