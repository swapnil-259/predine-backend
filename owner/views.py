from predine.constants import request_handlers, status_code, status_message
from execution.models import OwnerDetails
from Login.models import Dropdown
from django.http import JsonResponse
import json
from owner.models import Dish, ChefRestaurantMapping
from django.contrib.auth.hashers import check_password
from Login.models import User


def owner_data(request):
    if request_handlers.request_type(request, 'GET'):
        id = request.user.id
        owner_data = OwnerDetails.objects.filter(owner__id=id, deleted_status=False).values(
            'restaurant_name',
            'address',
            'restaurant_type__parent',
            'owner_role__role_name',
            'restaurant_pic',
            'owner__first_name',
            'owner__last_name',
            'owner__email',
            'owner__phone_number'
        ).first()
        formatted_data = [

            {'label': 'Restaurant Name',
                'value': owner_data['restaurant_name']},
            {'label': 'Restaurant Type',
                'value': owner_data['restaurant_type__parent']},
            {'label': 'Address',
                'value': owner_data['address']},
            {'label': 'First Name',
                'value': owner_data['owner__first_name']},
            {'label': 'Last Name',
                'value': owner_data['owner__last_name']},
            {'label': 'Email',
                'value': owner_data['owner__email']},
            {'label': 'Phone Number',
                'value': str(owner_data['owner__phone_number'])},
            {'label': 'Owner Role',
                'value': str(owner_data['owner_role__role_name'])},
            {'label': 'Restaurant Image',
                'value': owner_data['restaurant_pic']},
        ]
        return JsonResponse({'data': formatted_data}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def add_dish(request):
    if request_handlers.request_type(request, 'POST'):
        print('image', request.FILES.get('image'))
        print('Received FILES:', request.FILES)
        restaurant = OwnerDetails.objects.get(owner=request.user)
        print(restaurant)
        name = request.POST.get('name')
        description = request.POST.get('description')
        preparation_time = request.POST.get('preparation_time')
        price = request.POST.get('price')
        category = request.POST.get('category')
        image = request.FILES.get('image')
        diet = request.POST.get('diet')
        recommended = request.POST.get('recommended')
        category_exist = Dropdown.objects.filter(
            id=category, child__parent='DISH CATEGORY', deleted_status=False).first()
        if category_exist is None:
            return JsonResponse({'msg': status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)
        diet_exist = Dropdown.objects.filter(
            id=diet, child__parent='DIET PREFERENCE', deleted_status=False).first()
        if diet_exist is None:
            return JsonResponse({'msg': status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)

        dish_created = Dish.objects.create(
            name=name,
            restaurant=restaurant,
            description=description,
            preparation_time=preparation_time,
            price=price,
            category=category_exist,
            image=image,
            diet=diet_exist,
            recommended=recommended
        )
        if dish_created is not None:
            return JsonResponse({'msg': status_message.DISH_ADDED}, status=status_code.CREATED)
        else:
            return JsonResponse({'msg': status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def get_dish_type(request):
    if request_handlers.request_type(request, 'GET'):
        data = Dropdown.objects.filter(
            child=Dropdown.objects.filter(parent="DISH CATEGORY").first()
        ).values('parent', 'id')
        transformed_data = [{'label': item['parent'],
                             'value': item['id']} for item in data]

        return JsonResponse({'data': transformed_data}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def get_diet_pref(request):
    if request_handlers.request_type(request, 'GET'):
        data = Dropdown.objects.filter(
            child=Dropdown.objects.filter(parent="DIET PREFERENCE").first()
        ).values('parent', 'id')
        transformed_data = [{'label': item['parent'],
                             'value': item['id']} for item in data]

        return JsonResponse({'data': transformed_data}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def get_all_dishes(request):
    if request_handlers.request_type(request, 'GET'):
        data = Dish.objects.filter(restaurant=OwnerDetails.objects.get(owner=request.user), deleted_status=False).values(
            'name', 'description', 'price', 'preparation_time', 'category_id__parent', 'image', 'diet__parent', 'recommended')
        return JsonResponse({'data': list(data)}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def get_all_categories(request):
    if request_handlers.request_type(request, 'GET'):
        category_data = list(Dropdown.objects.filter(
            child_id__parent='DISH CATEGORY', added_by=request.user, deleted_status=False).values('id', 'parent'))
        return JsonResponse({'data': category_data}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def change_restaurant_pic(request):
    if request_handlers.request_type(request, 'POST'):
        image = request.FILES.get('image')
        data = OwnerDetails.objects.filter(
            owner_id=request.user, deleted_status=False).first()
        if data is not None:
            data.restaurant_pic = image
            data.save()
            return JsonResponse({'msg': 'Successfully Change Image'}, status=status_code.SUCCESS)
        else:
            return JsonResponse({'msg': 'No Restaurant Found'}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def change_password(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        owner_details = OwnerDetails.objects.filter(
            owner_id=request.user, deleted_status=False).first()

        if owner_details:
            if check_password(old_password, owner_details.owner.password):
                owner_details.owner.set_password(new_password)
                owner_details.owner.save()
                return JsonResponse({'msg': 'Successfully Change Image'}, status=status_code.SUCCESS)
            else:
                return JsonResponse({'msg': 'Old Password does not match'}, status=status_code.BAD_REQUEST)
        else:
            return JsonResponse({'msg': 'User not found'}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def check_owner_login_status(request):
    if request_handlers.request_type(request, 'GET'):
        user = User.objects.filter(
            user=request.user, deleted_status=False).first()
        if user.last_login is None:
            return JsonResponse({'data': {'Change_Password': True}}, status=status_code.SUCCESS)
        else:
            return JsonResponse({'data': {'Change_Password': False}}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def add_chef(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone_number = data.get('phone_number')
        password = data.get('password')
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=email,
            phone_number=phone_number,
            password=password
        )
        chef_mapping = ChefRestaurantMapping.objects.create(chef=user, restaurant=OwnerDetails.objects.filter(
            deleted_status=False, owner=request.user).first())
        if chef_mapping:
            return JsonResponse({'msg': 'Chef Added Successfully!!'}, status=status_code.SUCCESS)
        else:
            return JsonResponse({'msg': status_message.BAD_REQUEST}, status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def add_bank_details(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        acc_holder_name = data.get('acc_holder_name')
        ifsc_code = data.get('ifsc_code')
        acc_number = data.get('acc_number')
        owner_data = OwnerDetails.objects.filter(
            owner=request.user, deleted_status=False).first()
        if owner_data is None:
            return JsonResponse({'msg': 'Onwer not Found'}, status=status_code.BAD_REQUEST)
        owner_data.acc_holder_name = acc_holder_name
        owner_data.ifsc_code = ifsc_code
        owner_data.acc_number = acc_number
        owner_data.save()
        return JsonResponse({'msg': 'Successfully updated Bank Details'}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def get_all_chef(request):
    if request_handlers.request_type(request, 'GET'):
        restaurant = OwnerDetails.objects.filter(
            owner=request.user, deleted_status=False).first()
        data = ChefRestaurantMapping.objects.filter(restaurant=restaurant).values(
            'chef__first_name', 'chef__last_name', 'chef__email', 'chef__phone_number', 'chef_id')
        return JsonResponse({'data': list(data)}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)
