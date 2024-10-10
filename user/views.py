from django.shortcuts import render
from execution.models import OwnerDetails
from Login.models import User
from predine.constants import request_handlers,status_code,status_message
from django.http import JsonResponse
from owner.models import Dish

def get_all_restaurants(request):
    if request_handlers.request_type(request,'GET'):
            restaurant_data=OwnerDetails.objects.filter(deleted_status=False).values('id','restaurant_name','address','restaurant_type__parent','restaurant_pic')
            print(restaurant_data)
            return JsonResponse({'data':list(restaurant_data)},safe=False)
    else:
          return JsonResponse({'msg':status_message.METHOD_NOT_ALLOWED},status=status_code.METHOD_NOT_ALLWOED)

def get_user_data(request):
      if request_handlers.request_type(request,'GET'):
            user_data = User.objects.filter(id = request.user.id).values('first_name','last_name','email','phone_number')
            return JsonResponse({'data':list(user_data)},safe=False)
      else:
          return JsonResponse({'msg':status_message.METHOD_NOT_ALLOWED},status=status_code.METHOD_NOT_ALLWOED)

def get_menu(request):
      if request_handlers.request_type(request,'GET'):
            print("kjhg",request.GET.get('data'))
            menu_data = Dish.objects.filter(restaurant=request.GET.get('data'),deleted_status=False).values('name',
            'description','price','category__parent','image','preparation_time','diet__parent','recommended')
            print(menu_data)
            return JsonResponse({'data':list(menu_data)},safe=False)
      else:
          return JsonResponse({'msg':status_message.METHOD_NOT_ALLOWED},status=status_code.METHOD_NOT_ALLWOED)
