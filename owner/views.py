from django.shortcuts import render
from predine.constants import request_handlers, status_code, status_message, functions
from execution.models import OwnerDetails
from Login.models import Dropdown
from django.http import JsonResponse
import json
from owner.models import Dish


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
        category_exist = Dropdown.objects.filter(
            id=category, child__parent='DISH CATEGORY', deleted_status=False).first()
        if category_exist is None:
            return JsonResponse({'msg': status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)

        dish_created = Dish.objects.create(
            name=name,
            restaurant=restaurant,
            description=description,
            preparation_time=preparation_time,
            price=price,
            category=category_exist,
            image=image
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
        return JsonResponse({'data': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)