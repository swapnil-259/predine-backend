def request_type(request, type):
    print(type)
    if request.method == type:
        return True

    else:
        return False
