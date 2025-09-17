import sys

def print_marketing_list(pattern):
    #мои клиенты
    clients = ['andrew@gmail.com', 'jessica@gmail.com', 'ted@mosby.com',
               'john@snow.is', 'bill_gates@live.com', 'mark@facebook.com',
               'elon@paypal.com', 'jessica@gmail.com']
    # последнее мероприятие
    participants = ['walter@heisenberg.com', 'vasily@mail.ru',
                    'pinkman@yo.org', 'jessica@gmail.com', 'elon@paypal.com',
                    'pinkman@yo.org', 'mr@robot.gov', 'eleven@yahoo.com']
    # список клиентов, кто видел последнюю рекламу
    recipients = ['andrew@gmail.com', 'jessica@gmail.com', 'john@snow.is']
    # PATTERNS
    patterns = ["call_center", "potential_clients", "loly_program"]

    pattern = pattern.lower()
    if pattern not in patterns:
        print("Неверный pattern")
        return

    set_clients = set(clients)
    set_participants = set(participants)
    set_recipients = set(recipients)

    if pattern == patterns[0]:
        return get_call_center(set_clients, set_participants, filter=set_recipients)

    elif pattern == patterns[1]:
        return get_call_center(set_participants, filter=set_clients)

    elif pattern == patterns[2]:
        return get_call_center(set_clients, filter=set_participants)

    #
    # get_call_center(set_clients, set_participants, filter=set_recipients)
    # get_call_center(set_participants, filter=set_clients)
    # get_call_center(set_clients, filter=set_participants)
    print(pattern)

    return
#*args позволяет передавать произвольное количество позиционных
# аргументов в виде кортежа, а **kwargs — произвольное количество
# именованных аргументов в виде словаря
def get_call_center(*args, **kwargs):
    merge_list = []
    for ls in args:
        merge_list.extend(ls)

    result_list = []

    for k,v in kwargs.items():
        for element in merge_list:
            if element not in v:
                result_list.append(element)

    print(result_list)
    return


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Нужно ввести pattern форматирования')
        sys.exit(0)

    print_marketing_list(sys.argv[1])