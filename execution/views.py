from .models import OwnerDetails, User, Dropdown
from Login.models import UserRole, Roles
import json
from django.http import JsonResponse
from predine.constants import request_handlers, status_code, status_message, functions
import secret


def owner_registration(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone_number = data.get('phone_number')
        restaurant_name = data.get('restaurant_name')
        address = data.get('address')
        type = data.get('res')
        role = data.get('role')
        validate_data = functions.validate(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number,
                                           restaurant_name=restaurant_name, address=address, role=role, type=type, api_type="OWNER")
        if validate_data is not None:
            if validate_data['status'] == True and validate_data['other'] == False:
                return JsonResponse({'msg': validate_data['msg']+' '+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            elif validate_data['status'] == True and validate_data['other'] == True:
                return JsonResponse({'msg': validate_data['msg']}, status=status_code.BAD_REQUEST)

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=email,
            phone_number=phone_number,
            password=secret.OWNER_PASS
        )

        if user:
            print(role, type)
            role_exist = Roles.objects.filter(
                id=role, deleted_status=False).first()
            type_exist = Dropdown.objects.filter(
                id=type, deleted_status=False, child_id__parent="RESTAURANT TYPE").first()
            if role_exist is None:
                return JsonResponse({'msg': status_message.INVALID_DATA}, status=status_code.BAD_REQUEST)
            if type_exist is None:
                return JsonResponse({'msg': status_message.INVALID_DATA}, status=status_code.BAD_REQUEST)

            role = UserRole.objects.create(
                role=role_exist,
                user=user
            )
            owner = OwnerDetails.objects.create(
                owner=user,
                restaurant_name=restaurant_name,
                address=address,
                restaurant_type=type_exist
            )

        else:
            return JsonResponse({"msg": status_code.BAD_REQUEST}, status=status_message.BAD_REQUEST)
        if owner:
            return JsonResponse({"msg": status_message.SUCCESS})
        else:
            return JsonResponse({"msg": status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def get_role_type(request):
    if request_handlers.request_type(request, 'GET'):

        data = Dropdown.objects.filter(child=Dropdown.objects.filter(
            parent="ROLE TYPE").first()).values('parent', 'id')

        transformed_data = [{'label': item['parent'],
                             'value': item['id']} for item in data]
        return JsonResponse({'data': transformed_data}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'data': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def get_res_type(request):
    if request_handlers.request_type(request, 'GET'):
        data = Dropdown.objects.filter(
            child=Dropdown.objects.filter(parent="RESTAURANT TYPE").first()
        ).values('parent', 'id')

        transformed_data = [{'label': item['parent'],
                             'value': item['id']} for item in data]

        return JsonResponse({'data': transformed_data}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'data': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def view_owners(request):
    if request_handlers.request_type(request, 'GET'):
        restaurant_data = OwnerDetails.objects.filter(deleted_status=False).values(
            'id', 'restaurant_name', 'restaurant_type__parent', 'address', 'owner_id', 'owner__first_name', 'owner__last_name', 'owner__phone_number', 'owner__email')
        print(restaurant_data)
        return JsonResponse({'data': list(restaurant_data)}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'data': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)
