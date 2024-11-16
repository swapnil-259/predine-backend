import json
from urllib import request

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_datetime

from execution.models import OwnerDetails
from Login.models import Dropdown, User
from owner.models import Dish
from predine.algorithms.order_id import generate_unique_order_id
from predine.constants import request_handlers, status_code, status_message
from predine.constants.razorpay import razorpay_client
from user.models import OrderDetails, OrderDishDetails, OrderLogs


def get_all_restaurants(request):
    if request_handlers.request_type(request, "GET"):
        restaurant_data = OwnerDetails.objects.filter(deleted_status=False).values(
            "id",
            "restaurant_name",
            "address",
            "restaurant_type__parent",
            "restaurant_pic",
        )
        print(restaurant_data)
        return JsonResponse({"data": list(restaurant_data)}, safe=False)
    else:
        return JsonResponse(
            {"msg": status_message.METHOD_NOT_ALLOWED},
            status=status_code.METHOD_NOT_ALLWOED,
        )


def get_user_data(request):
    if request_handlers.request_type(request, "GET"):
        user_data = User.objects.filter(id=request.user.id).values(
            "first_name", "last_name", "email", "phone_number"
        )
        return JsonResponse({"data": list(user_data)}, safe=False)
    else:
        return JsonResponse(
            {"msg": status_message.METHOD_NOT_ALLOWED},
            status=status_code.METHOD_NOT_ALLWOED,
        )


def get_menu(request):
    if request_handlers.request_type(request, "GET"):
        print("kjhg", request.GET.get("data"))
        menu_data = Dish.objects.filter(
            restaurant=request.GET.get("data"), deleted_status=False
        ).values(
            "id",
            "name",
            "description",
            "price",
            "category__parent",
            "image",
            "preparation_time",
            "diet__parent",
            "recommended",
        )
        print(menu_data)
        return JsonResponse({"data": list(menu_data)}, safe=False)
    else:
        return JsonResponse(
            {"msg": status_message.METHOD_NOT_ALLOWED},
            status=status_code.METHOD_NOT_ALLWOED,
        )


def place_order(request):
    if request_handlers.request_type(request, "POST"):
        data = json.loads(request.body)
        cart_items = data.get("cartItems", [])
        selected_time = data.get("selectedTime")
        total_price = data.get("totalPrice")
        restaurant_id = data.get("restaurantId")

        order = OrderDetails.objects.create(
            user=request.user,
            order_id=generate_unique_order_id(),
            payment_status=Dropdown.objects.filter(
                child__parent="PAYMENT STATUS", parent="Pending", deleted_status=False
            ).first(),
            total_amount=total_price,
            order_time=parse_datetime(selected_time),
            restaurant_id=restaurant_id,
        )

        for item in cart_items:
            dish = Dish.objects.get(id=item["id"])
            OrderDishDetails.objects.create(
                order=order,
                dish=dish,
                quantity=item["quantity"],
                amount=item["price"] * item["quantity"],
            )
        OrderLogs.objects.create(
            order=order,
            level=1,
            order_status=Dropdown.objects.filter(
                child__parent="ORDER STATUS", parent="Pending", deleted_status=False
            ).first(),
        )

        return JsonResponse({"msg": "Order placed successfully"})
    else:

        return JsonResponse(
            {"msg": status_message.METHOD_NOT_ALLOWED},
            status=status_code.METHOD_NOT_ALLWOED,
        )


def get_user_orders(request):
    if request_handlers.request_type(request, "GET"):
        orders = OrderDetails.objects.filter(user=request.user)

        orders_summary = []
        for order in orders:
            last_order_log = (
                OrderLogs.objects.filter(order=order).order_by("-id").first()
            )

            if last_order_log and last_order_log.order_status:
                if last_order_log.level == 1:
                    if last_order_log.order_status.parent == "Cancel":
                        order_status = (
                            last_order_log.order_status.parent + " ( by User)"
                        )
                    else:

                        order_status = (
                            last_order_log.order_status.parent
                            + " (by Restaurant Owner)"
                        )
                elif last_order_log.level == 2:
                    order_status = last_order_log.order_status.parent
                else:
                    order_status = last_order_log.order_status.parent
            else:
                order_status = "Not Provided"

            order_dishes = OrderDishDetails.objects.filter(order=order)
            if last_order_log.order_status.parent == "Pending":
                print("heeloooooo")
            dishes_summary = [
                {
                    "dish_id": dish_detail.dish.id,
                    "dish_name": dish_detail.dish.name,
                    "quantity": dish_detail.quantity,
                    "amount_per_unit": dish_detail.amount,
                    "total_amount": dish_detail.quantity * dish_detail.amount,
                }
                for dish_detail in order_dishes
            ]

            orders_summary.append(
                {
                    "id": order.id,
                    "order_id": order.order_id,
                    "payment_status": (
                        order.payment_status.parent
                        if order.payment_status
                        else "Not Provided"
                    ),
                    "total_amount": order.total_amount,
                    "order_time": (
                        order.created_time.strftime("%Y-%m-%d %H:%M:%S")
                        if order.created_time
                        else "Not Available"
                    ),
                    "payment_id": order.payment_id,
                    "order_receiving_time": order.order_time,
                    "order_status": order_status,
                    "level": (
                        last_order_log.level if last_order_log else "Not Available"
                    ),  # Add level of last log entry
                    "dishes": dishes_summary,
                }
            )

        return JsonResponse({"data": orders_summary})
    else:
        return JsonResponse(
            {"msg": status_message.METHOD_NOT_ALLOWED},
            status=status_code.METHOD_NOT_ALLWOED,
        )


def create_order(request):
    if request_handlers.request_type(request, "POST"):
        data = json.loads(request.body)
        order_id = data.get("order_id")
        order = OrderDetails.objects.filter(
            order_id=order_id, deleted_status=False
        ).first()
        prefill = {"email": order.user.email, "contact": order.user.phone_number}
        razorpay_order = razorpay_client.order.create(
            {
                "amount": int(order.total_amount * 100),
                "currency": "INR",
                "payment_capture": "1",
            }
        )

        order.razorpay_order_id = razorpay_order["id"]
        order.save()

        return JsonResponse(
            {
                "razorpayOrderId": razorpay_order["id"],
                "amount": order.total_amount,
                "currency": "INR",
                "prefill": prefill,
            }
        )

    else:
        return JsonResponse(
            {"msg": status_message.METHOD_NOT_ALLOWED},
            status=status_code.METHOD_NOT_ALLWOED,
        )


def confirm_payment(request):
    if request_handlers.request_type(request, "POST"):
        data = json.loads(request.body)
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }
        print(params_dict)

        result = razorpay_client.utility.verify_payment_signature(params_dict)
        print(result)

        if result:
            order = OrderDetails.objects.get(razorpay_order_id=razorpay_order_id)
            order.payment_status = Dropdown.objects.filter(
                parent="Success", child__parent="PAYMENT STATUS"
            ).first()
            order.payment_id = razorpay_payment_id
            order.payment_signature = razorpay_signature
            order.save()
            OrderLogs.objects.create(
                order=order,
                level=2,
                order_status=Dropdown.objects.filter(
                    parent="Preparing", child__parent="FOOD STATUS"
                ).first(),
            )

            return JsonResponse({"message": "Payment successful"})
        else:
            return JsonResponse(
                {"error": "Signature verification failed"},
                status=status_code.BAD_REQUEST,
            )
    else:
        return JsonResponse(
            {"msg": status_message.METHOD_NOT_ALLOWED},
            status=status_code.METHOD_NOT_ALLWOED,
        )


def cancel_order(request):
    if request_handlers.request_type(request, "POST"):
        data = json.loads(request.body)
        print(data)
        order_id = data.get("order_id")
        if order_id is None:
            return JsonResponse(
                {"msg": "Order not Found"}, status=status_code.BAD_REQUEST
            )
        order_log_data = OrderLogs.objects.filter(order=order_id, level=1).first()
        order_log_data.order_status = Dropdown.objects.filter(
            parent="Cancel", child__parent="CUSTOMER STATUS"
        ).first()
        order_log_data.save()
        return JsonResponse(
            {"msg": "Order cancelled successfully"}, status=status_code.SUCCESS
        )
    else:
        return JsonResponse(
            {"msg": status_message.METHOD_NOT_ALLOWED},
            status=status_code.METHOD_NOT_ALLWOED,
        )
