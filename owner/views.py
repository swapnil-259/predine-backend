from django.shortcuts import render
from predine.constants import request_handlers, status_code, status_message, functions
from execution.models import OwnerDetails
from Login.models import Dropdown,UserRole,User,Roles
from django.http import JsonResponse
import json
from owner.models import ChefRestaurantMapping, Dish
import secret
from user.models import OrderDetails,OrderDishDetails,OrderLogs


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
            child_id__parent='DISH CATEGORY', deleted_status=False).values('id', 'parent'))
        return JsonResponse({'data': category_data}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def edit_res_image(request):
    if request_handlers.request_type(request,'POST'):
        image = request.FILES.get('image')
        owner_data=OwnerDetails.objects.filter(owner = request.user).first()
        if owner_data is not None:
            owner_data.restaurant_pic=image
            owner_data.save()
            return JsonResponse({'msg': 'Image Updated Successfully'}, status=status_code.SUCCESS)
        else:
            return JsonResponse({'msg':'Do not find any owner'},status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def add_bank_details(request):
    if request_handlers.request_type(request,'POST'):
        data = json.loads(request.body)
        acc_holder_name= data.get('acc_holder_name')
        acc_ifsc_code= data.get('ifsc_code')
        acc_number = data.get('acc_number')
        print(acc_holder_name,acc_ifsc_code,acc_number)
        owner_data=OwnerDetails.objects.filter(owner = request.user).first()
        if owner_data is not None:
            owner_data.acc_holder_name=acc_holder_name
            owner_data.acc_ifsc_code=acc_ifsc_code
            owner_data.acc_number=acc_number
            owner_data.account_status=True
            owner_data.save()
            return JsonResponse({'msg': 'Account Details Added Successfully'}, status=status_code.SUCCESS)
        else:
            return JsonResponse({'msg':'Do not find any owner'},status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def check_bank_status(request):
    if request_handlers.request_type(request,'GET'):
        owner_data=OwnerDetails.objects.filter(owner = request.user,deleted_status=False).first()
        if owner_data:
            return JsonResponse({"account_status":owner_data.account_status})
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)
 

def view_bank_details(request):
    if request_handlers.request_type(request,'GET'):
        bank_details = OwnerDetails.objects.filter(owner=request.user,deleted_status=False).values('acc_holder_name','acc_ifsc_code','acc_number')
        return JsonResponse({'data':list(bank_details)})
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)

def add_chef(request):
    if request_handlers.request_type(request,'POST'):
        data = json.loads(request.body)
        first_name=data.get('first_name')
        last_name=data.get('last_name')
        email = data.get('email')
        phone_number = data.get('phone_number')
        restaurant = OwnerDetails.objects.get(owner=request.user)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'msg': 'User with this email already exists.'}, status=status_code.BAD_REQUEST)

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            username = email,
            password = secret.CHEF_PASS
        )
        user_role=UserRole.objects.create(user = user,role = Roles.objects.get(role_name='CHEF'))
        ChefRestaurantMapping.objects.create(chef = user_role,restaurant=restaurant)
        return JsonResponse({'msg':'Chef Added Successfully'},status=status_code.SUCCESS)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


from django.db.models import Max

def get_orders(request):
    if request_handlers.request_type(request, 'GET'):
        restaurant = OwnerDetails.objects.filter(owner=request.user, deleted_status=False).first()
        
        order_data = OrderDetails.objects.filter(restaurant=restaurant, deleted_status=False)

        orders = []
        for order in order_data:
            # Fetch the latest log with level 1 (current order status)
            latest_order_log = (
                OrderLogs.objects.filter(order=order, level=1)
                .order_by('-created_time')
                .first()
            )

            # Fetch the receiver status from level 3
            receiver_status_log = (
                OrderLogs.objects.filter(order=order, level=3)
                .order_by('-created_time')
                .first()
            )

            if not latest_order_log:
                continue
            
            dish_details = OrderDishDetails.objects.filter(order=order)
            dishes = [
                {
                    'dish_id': dish_detail.dish.id,
                    'dish_name': dish_detail.dish.name,
                    'quantity': dish_detail.quantity,
                    'amount': dish_detail.amount,
                }
                for dish_detail in dish_details
            ]

            orders.append({
                'order_id': order.order_id,
                'order_status': latest_order_log.order_status.parent if latest_order_log.order_status else None,
                'payment_status': order.payment_status.parent if order.payment_status else None,
                'payment_id': order.payment_id if order.payment_status and order.payment_status.parent == 'Success' else None,
                'total_amount': order.total_amount,
                'order_time': order.created_time.isoformat() if order.created_time else None,
                'order_receiving_time': order.order_time.isoformat() if order.order_time else None,
                'dishes': dishes,
                'receiver_status': receiver_status_log.order_status.parent if receiver_status_log and receiver_status_log.order_status else None,  # Receiver status from level 3
            })

        return JsonResponse({'data': orders}, status=200)

    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLOWED)



def accept_order(request):
    if request_handlers.request_type(request,'POST'):
        data = json.loads(request.body)
        order_id = data.get('order_id')
        print(order_id)
        order = OrderDetails.objects.filter(order_id=order_id,deleted_status=False).first()
        if order is None:
            return JsonResponse({'msg':'No orderId Found'},status=status_code.BAD_REQUEST)


        level_1_log = OrderLogs.objects.get(order=order, level=1)
        level_1_log.order_status = Dropdown.objects.filter(parent='Accepted',child__parent='ORDER STATUS',deleted_status=False) .first()
        level_1_log.save()
        return JsonResponse({'msg': 'Order accepted successfully.'})

        
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)

def reject_order(request):
    
    if request_handlers.request_type(request,'POST'):

        data = json.loads(request.body)
        order_id = data.get('order_id')
        order = OrderDetails.objects.filter(order_id=order_id,deleted_status=False).first()
        if order is None:
            return JsonResponse({'msg':'No orderId Found'},status=status_code.BAD_REQUEST)

        level_1_log = OrderLogs.objects.get(order=order, level=1)
        level_1_log.order_status = Dropdown.objects.filter(parent='Rejected',child__parent='ORDER STATUS',deleted_status=False).first()
        level_1_log.save()
        return JsonResponse({'msg': 'Order rejected successfully.'})

    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)
