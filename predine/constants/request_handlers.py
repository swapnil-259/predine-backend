def request_type(request, type):
    if request.method == type:
        return True

    else:
        return False
