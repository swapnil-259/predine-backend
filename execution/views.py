from .models import OwnerDetails, User, Dropdown
from Login.models import UserRole, Roles
import json
from django.http import JsonResponse
from predine.constants import request_handlers, status_code, status_message, functions
import secret
from django.utils import timezone


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

        # Check if a user with the same email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({'msg': 'A user with this email already exists.'}, status=status_code.BAD_REQUEST)

        # validate_data = functions.validate(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number,
                                        #    restaurant_name=restaurant_name, address=address, role=role, type=type, api_type="OWNER")
        # if validate_data is not None:
        #     if validate_data['status'] == True and validate_data['other'] == False:
        #         return JsonResponse({'msg': validate_data['msg']+' '+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
        #     elif validate_data['status'] == True and validate_data['other'] == True:
        #         return JsonResponse({'msg': validate_data['msg']}, status=status_code.BAD_REQUEST)

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
            dd_exist = Dropdown.objects.filter(
                id=role, deleted_status=False, child__parent='ROLE TYPE ').first()
            print(dd_exist)
            role_exist = Roles.objects.filter(
                role_name=dd_exist.parent, deleted_status=False).first()
            print(role_exist)
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
                restaurant_type=type_exist,
                owner_role=role_exist
            )

        else:
            return JsonResponse({"msg": status_message.BAD_REQUEST}, status=status_message.BAD_REQUEST)
        if owner:
            return JsonResponse({"msg": status_message.SUCCESS})
        else:
            return JsonResponse({"msg": status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)

    elif request_handlers.request_type(request, "PUT"):
        data = json.loads(request.body).get('data')
        update_data = {}

        for i in data:
            if i['can_edit'] == True:
                update_data[i['key']] = i['value']
        owner_id = update_data.get('owner_id')
        first_name = update_data.get('first_name')
        last_name = update_data.get('last_name')
        phone_number = update_data.get('phone_number')
        restaurant_name = update_data.get('restaurant_name')
        address = update_data.get('address')

        validate_data = functions.validate(first_name=first_name, last_name=last_name,  phone_number=phone_number,
                                           restaurant_name=restaurant_name, address=address, api_type="OWNER")
        if validate_data is not None:
            if validate_data['status']:
                return JsonResponse({'msg': validate_data['msg']}, status=status_code.BAD_REQUEST)

        try:
            owner = OwnerDetails.objects.get(id=owner_id)
            owner.restaurant_name = restaurant_name
            owner.address = address
            owner.save()
            user = owner.owner
            user.first_name = first_name
            user.last_name = last_name
            user.phone_number = phone_number
            user.save()
            return JsonResponse({"msg": status_message.SUCCESS})

        except User.DoesNotExist:
            return JsonResponse({"msg": status_message.USER_NOT_FOUND}, status=status_code.BAD_REQUEST)

    elif request_handlers.request_type(request, 'DELETE'):
        print(request.body)
        data = json.loads(request.body)
        print(data)
        owner = data.get('id')
        owner_details = OwnerDetails.objects.filter(id=owner).first()
        print(owner_details)

        if owner_details is None:
            return JsonResponse({'msg': status_message.USER_NOT_FOUND}, status=status_code.BAD_REQUEST)
        else:
            OwnerDetails.objects.filter(id=owner).update(
                deleted_status=True, deleted_time=timezone.now())
            user = owner_details.owner.id
            User.objects.filter(id=user).update(
                deleted_status=True, deleted_time=timezone.now(), is_active=False, last_login=None)
            UserRole.objects.filter(user=user).update(
                deleted_status=True, deleted_time=timezone.now())
            return JsonResponse({"msg": status_message.SUCCESS})

    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def get_role_type(request):
    if request_handlers.request_type(request, 'GET'):
        print(Dropdown.objects.filter(
            parent="ROLE TYPE").first())

        data = Dropdown.objects.filter(child=Dropdown.objects.filter(
            parent="ROLE TYPE").first()).values('parent', 'id')
        print("roles",data)
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
        print("res",data)
        transformed_data = [{'label': item['parent'],
                             'value': item['id']} for item in data]

        return JsonResponse({'data': transformed_data}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'data': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def owner_list(request):
    if request_handlers.request_type(request, 'GET'):
        restaurant_data = OwnerDetails.objects.filter(deleted_status=False).values(
            'id', 'restaurant_name', 'restaurant_type__parent')
        print(restaurant_data)
        return JsonResponse({'data': list(restaurant_data)}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'data': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def view_owners(request):
    print(request.GET.get('id'))
    if request_handlers.request_type(request, 'GET'):
        owner_id = request.GET.get('id')
        if not owner_id:
            return JsonResponse({'data': 'ID parameter is missing'}, status=status_code.BAD_REQUEST)

        restaurant_data = OwnerDetails.objects.filter(deleted_status=False, id=owner_id).values(
            'id', 'restaurant_name', 'restaurant_type__parent', 'address',
            'owner__first_name', 'owner__last_name', 'owner__email', 'owner__phone_number', 'owner_role__role_name', 'restaurant_pic'
        ).first()

        if not restaurant_data:
            return JsonResponse({'data': 'No data found'}, status=status_code.NOT_FOUND)

        formatted_data = [
            {'label': 'id',
                'value': restaurant_data['id'], 'can_edit': True, 'key': 'owner_id'},
            {'label': 'Restaurant Name',
                'value': restaurant_data['restaurant_name'], 'can_edit': True, 'key': 'restaurant_name'},
            {'label': 'Restaurant Type',
                'value': restaurant_data['restaurant_type__parent'], 'can_edit': False, 'key': 'res'},
            {'label': 'Address',
                'value': restaurant_data['address'], 'can_edit': True, 'key': 'address'},
            {'label': 'First Name',
                'value': restaurant_data['owner__first_name'], 'can_edit': True, 'key': 'first_name'},
            {'label': 'Last Name',
                'value': restaurant_data['owner__last_name'], 'can_edit': True, 'key': 'last_name'},
            {'label': 'Email',
                'value': restaurant_data['owner__email'], 'can_edit': False, 'key': 'email'},
            {'label': 'Phone Number',
                'value': str(restaurant_data['owner__phone_number']), 'can_edit': True, 'key': 'phone_number'},
            {'label': 'Owner Role',
                'value': str(restaurant_data['owner_role__role_name']), 'can_edit': False, 'key': 'role'},
            {'label': 'Restaurant Image',
                'value': str(restaurant_data['restaurant_pic']), 'can_edit': True, 'key': 'img'},
        ]

        return JsonResponse({'data': formatted_data}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'data': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)
    
# def DashboardMappingView(request):
#     if request_handlers.request_type(request,'POST'):
#         category = request.GET.get('category')
#         image = request.FILES.get('image')
#         if category and image is None:
#             return JsonResponse({'msg':'category and Image both are required fields'},status=status_code.BAD_REQUEST)
#         category_data = Dropdown.obec