from predine.constants import path, status_code, status_message
from django.http import JsonResponse


def authentication(get_response):
    def check_authentication(request):
        req_path = request.path
        if req_path in path.AUTHENTICATED_PATH:
            if request.user.is_authenticated:
                print(request.session['role'], request.session['user_role'])
                response = get_response(request)
                role_res = check_role(req_path, request.session['user_role'])
                if role_res:
                    return response
                return JsonResponse({status_message.FORBIDDEN}, status_code.FORBIDDEN)
            else:
                return JsonResponse({status_message.UNAUTHENTICATED}, status_code.UNAUTHENTICATED)
        else:
            response = get_response(request)
            return response
    return check_authentication


def check_role(req_path, role):
    match role:
        case "ADMIN":
            if req_path in path.ADMIN_ROLE:
                return True
            return False
        case "OWNER":
            if req_path in path.OWNER_ROLE:
                return True
            return False
        case "USER":
            if req_path in path.USER_ROLE:
                return True
            return False
        case "CHEF":
            if req_path in path.CHEF_ROLE:
                return True
        case "OWNER-CHEF":
            if req_path in path.CHEF_ROLE:
                return True
            return False
