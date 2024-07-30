from django.shortcuts import render
from predine.constants import request_handlers, status_code, status_message, functions
from Login.models import RoleDropdownMapping, Dropdown
from django.http import JsonResponse
import json

# Create your views here.


def parent_list(request):

    if request_handlers.request_type(request, 'GET'):
        print(request.session['role'])
        data = RoleDropdownMapping.objects.filter(role=request.session.get(
            'role'), dropdown_parent__child=None, dropdown_parent__can_edit=True).values('dropdown_parent__parent', 'dropdown_parent')
        print(data)

        transformed_data = [{'label': item['dropdown_parent__parent'],
                             'value': item['dropdown_parent']} for item in data]
        return JsonResponse({'data': transformed_data}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'data': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def add_child(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        parent = data.get('parent')
        child = data.get('child')
        validate_data = functions.validate(
            parent=parent, child=child, api_type="ADD CHILD")
        if validate_data is not None:
            if validate_data['status']:
                return JsonResponse({'msg': validate_data['msg']}, status=status_code.BAD_REQUEST)
        parent_exist = Dropdown.objects.filter(
            id=parent, child=None).first()
        if parent_exist is None:
            return JsonResponse({'msg': status_message.PARENT_NOT_FOUND}, status=status_code.BAD_REQUEST)
        if parent_exist.can_edit is False:
            return JsonResponse({'msg': status_message.PARENT_NOT_EDITED}, status=status_code.BAD_REQUEST)
        Dropdown.objects.create(
            parent=child, child=parent_exist, can_edit=False, added_by=request.user)
        return JsonResponse({'msg': status_message.CHILD_ADDED}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def get_child(request):
    if request_handlers.request_type(request, 'GET'):
        parent = request.GET.get('parent')
        if not parent:
            return JsonResponse({'msg': status_message.PARENT_NOT_FOUND}, status=status_code.BAD_REQUEST)
        parent_exist = Dropdown.objects.filter(
            id=parent, child=None).first()
        if parent_exist is None:
            return JsonResponse({'msg': status_message.PARENT_NOT_FOUND}, status=status_code.BAD_REQUEST)
        child_data = Dropdown.objects.filter(
            child=Dropdown.objects.filter(id=parent).first()).values('parent', 'id')
        transformed_data = [{'label': item['parent'],
                             'value': item['id']} for item in child_data]
        return JsonResponse({'data': transformed_data}, status=status_code.SUCCESS)
