def process_data(items=[]):  # mutable-default
    pass

def read_file(path):
    f = open(path, 'r')  # unclosed-resource
    return f.read()

def loop_example(arr):
    for i in range(len(arr) + 1):  # loop-off-by-one
        print(arr[i])

def auth_check(user, role):
    if role == "admin" or "superuser":  # always-true
        return True
    return False

def calculate(cost):
    cost == 0  # noop-comparison
    return cost

def handle_error():
    try:
        1 / 0
    except:  # bare-except
        pass  # empty-except

def ship_order(order):
    if order.status == "shipped":
        return False
    if order.items:
        for item in order.items:
            if item.stock < 1:
                return False
            item.stock -= 1
    else:
        return False
    order.status = "shipped"
    try:
        db.save(order)
        send_email(order.customer)
    except Exception as e:
        logger.error(e)
        return False
    return True

def add(a, b):
    return a + b

def square(x):
    return x * x

def get_name(user):
    return user.name

def is_even(n):
    return n % 2 == 0
