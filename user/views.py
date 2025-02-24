import json

# from predine.constants.functions import order_cancelled_no_owner_response
import threading
import time
from urllib import request

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

import secret
from execution.models import OwnerDetails
from Login.models import Dropdown, User
from owner.models import Dish, OwnerStatistics
from predine.algorithms.order_id import generate_unique_order_id
from predine.constants import request_handlers, status_code, status_message
from predine.constants.razorpay import razorpay_client
from user.models import OrderDetails, OrderDishDetails, OrderLogs


def order_cancelled_no_owner_response(order_id):
    if order_id is None:
        return JsonResponse(
            {"msg": "Order Id is required"}, status=status_code.BAD_REQUEST
        )
    order_details = OrderDetails.objects.filter(id=order_id).first()
    if not order_details:
        return

    order_log = OrderLogs.objects.filter(order=order_details, level=1).first()
    if not order_log:
        return

    if (
        order_details.payment_status.parent == "Pending"
        and order_log.order_status.parent == "Pending"
    ):
        order_log.order_status = Dropdown.objects.filter(
            parent="No Response", child__parent="CANCELLED STATUS"
        ).first()
        order_log.save()


def get_all_restaurants(request):
    if request_handlers.request_type(request, "GET"):
        restaurant_data = OwnerDetails.objects.filter(deleted_status=False).values(
            "id",
            "restaurant_name",
            "address",
            "restaurant_type__parent",
            "restaurant_pic",
            "is_open",
        )
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
        menu_data = (
            Dish.objects.filter(
                restaurant=request.GET.get("data"), deleted_status=False
            )
            .values(
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
            .order_by("name")
        )
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
            order_time=selected_time,
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

        def monitor_order(order_id):
            time.sleep(120)
            order_cancelled_no_owner_response(order_id)

        thread = threading.Thread(target=monitor_order, args=(order.id,))
        thread.start()

        return JsonResponse({"msg": "Order placed successfully"})
    else:

        return JsonResponse(
            {"msg": status_message.METHOD_NOT_ALLOWED},
            status=status_code.METHOD_NOT_ALLWOED,
        )


def get_user_orders(request):
    if request_handlers.request_type(request, "GET"):
        orders = OrderDetails.objects.filter(user=request.user).order_by(
            "-created_time"
        )

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

            order_dishes = OrderDishDetails.objects.filter(order=order, cancel=False)
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
                        order.created_time if order.created_time else "Not Available"
                    ),
                    "payment_id": order.payment_id,
                    "order_receiving_time": order.order_time,
                    "order_status": order_status,
                    "level": (
                        last_order_log.level if last_order_log else "Not Available"
                    ),
                    "last_order_time": last_order_log.updated_time,
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
                "amount": order.total_amount * 100,
                "currency": "INR",
                "payment_capture": "1",
            }
        )

        order.razorpay_order_id = razorpay_order["id"]
        order.save()

        return JsonResponse(
            {
                "msg": "Order created successfully",
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

        result = razorpay_client.utility.verify_payment_signature(params_dict)

        if result:
            order = OrderDetails.objects.filter(
                razorpay_order_id=razorpay_order_id
            ).first()
            order.payment_status = Dropdown.objects.filter(
                parent="Success", child__parent="PAYMENT STATUS"
            ).first()
            order.payment_id = razorpay_payment_id
            order.payment_signature = razorpay_signature
            updated_time = order.updated_time
            current_time = timezone.now()
            time_difference = current_time - updated_time
            order_time = order.order_time
            updated_order_time = order_time + time_difference
            order.order_time = updated_order_time
            order.save()
            OrderLogs.objects.create(
                order=order,
                level=2,
                order_status=Dropdown.objects.filter(
                    parent="Preparing", child__parent="FOOD STATUS"
                ).first(),
            )

            owner = order.restaurant  # Assuming order has an owner field
            today_date = timezone.now().date()
            owner_statistics, created = OwnerStatistics.objects.get_or_create(
                owner=owner,
                date=today_date,
                defaults={"total_orders": 0, "total_revenue": 0},
            )

            if not created:
                owner_statistics.total_orders += 1
                owner_statistics.total_revenue += order.total_amount
                owner_statistics.save()
            return JsonResponse({"msg": "Payment successful"})
        else:
            return JsonResponse(
                {"msg": "Signature verification failed"},
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


def show_privacy_policy(request):
    return render(request, "privacy_policy.html")


def request_account_deletion(request):
    if request.method == "GET":
        # Logic to handle account deletion
        # You can save the request in a database, send an email, or immediately process the deletion
        return JsonResponse(
            {"message": "Your account deletion request has been submitted."}
        )


def razorpay_webhook(request):
    """Handles Razorpay webhook calls to update payment status."""
    body_unicode = request.body.decode("utf-8")  # Convert bytes to string
    data = json.loads(body_unicode)
    event = data.get("event")

    webhook_secret = secret.WEBHOOK_SECRET
    signature = request.headers.get("X-Razorpay-Signature")
    razorpay_client.utility.verify_webhook_signature(
        request.body.decode("utf-8"), signature, webhook_secret
    )

    if event == "payment.captured":
        payment_data = data["payload"]["payment"]["entity"]
        razorpay_order_id = payment_data["order_id"]
        razorpay_payment_id = payment_data["id"]
        razorpay_signature = signature

        order = OrderDetails.objects.filter(razorpay_order_id=razorpay_order_id).first()
        if order:
            order.payment_status = Dropdown.objects.filter(
                parent="Success", child__parent="PAYMENT STATUS"
            ).first()

            order.payment_id = razorpay_payment_id
            order.payment_signature = razorpay_signature
            updated_time = order.updated_time
            current_time = timezone.now()
            time_difference = current_time - updated_time
            order_time = order.order_time
            updated_order_time = order_time + time_difference
            order.order_time = updated_order_time
            order.save()

            OrderLogs.objects.create(
                order=order,
                level=2,
                order_status=Dropdown.objects.filter(
                    parent="Preparing", child__parent="FOOD STATUS"
                ).first(),
            )
            owner = order.restaurant  # Assuming order has an owner field
            today_date = timezone.now().date()
            owner_statistics, created = OwnerStatistics.objects.get_or_create(
                owner=owner,
                date=today_date,
                defaults={"total_orders": 0, "total_revenue": 0},
            )

            if not created:
                owner_statistics.total_orders += 1
                owner_statistics.total_revenue += order.total_amount
                owner_statistics.save()

            return JsonResponse({"msg": "Payment updated successfully"}, status=200)

    elif event == "payment.failed":
        payment_data = data["payload"]["payment"]["entity"]
        razorpay_order_id = payment_data["order_id"]

        order = OrderDetails.objects.filter(razorpay_order_id=razorpay_order_id).first()

        if order:
            order.payment_status = Dropdown.objects.filter(
                parent="Failed", child__parent="PAYMENT STATUS"
            ).first()
            order.save()
            return JsonResponse({"msg": "Payment failed updated"}, status=200)

    return JsonResponse({"msg": "Event ignored"}, status=400)
