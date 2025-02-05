import json

from django.db.models import Q
from django.http import JsonResponse

from owner.models import ChefRestaurantMapping, UserRole, OwnerDetails
from predine.constants import request_handlers, status_code, status_message
from user.models import Dropdown, OrderDetails, OrderLogs, OrderDishDetails


def chef_orders(request):
    order_approved_status = Dropdown.objects.filter(
        parent="Accepted", child__parent="ORDER STATUS"
    ).first()
    payment_success_status = Dropdown.objects.filter(
        parent="Success", child__parent="PAYMENT STATUS"
    ).first()

    chef_restaurants = ChefRestaurantMapping.objects.filter(
        chef__user_id=request.user
    ).values_list("restaurant", flat=True)

    approved_orders = (
        OrderLogs.objects.filter(
            level=1,
            order_status=order_approved_status,
            order__payment_status=payment_success_status,
            order__restaurant__in=chef_restaurants,
        )
        .select_related("order")
        .order_by("-order__created_time")
    )

    chef_orders = approved_orders.filter(order__orderlogs__level=2)

    orders_data = []

    for log in chef_orders:
        order_details = log.order

        level_2_status = OrderLogs.objects.filter(order=order_details, level=2).first()

        level_3_status = OrderLogs.objects.filter(order=order_details, level=3).first()

        orders_data.append(
            {
                "order_id": order_details.order_id,
                "total_amount": order_details.total_amount,
                "order_time": (
                    order_details.created_time.isoformat()
                    if order_details.created_time
                    else None
                ),
                "order_receiving_time": (
                    order_details.order_time.isoformat()
                    if order_details.order_time
                    else None
                ),
                "restaurant": (
                    {
                        "name": order_details.restaurant.restaurant_name,
                        "address": order_details.restaurant.address,
                    }
                    if order_details.restaurant
                    else None
                ),
                "order_status": (
                    level_2_status.order_status.parent
                    if level_2_status and level_2_status.order_status
                    else None
                ),
                "receiver_status": (
                    level_3_status.order_status.parent
                    if level_3_status and level_3_status.order_status
                    else None
                ),
                "dishes": [
                    {
                        "dish_id": dish_detail.dish.id,
                        "dish_name": dish_detail.dish.name,
                        "quantity": dish_detail.quantity,
                        "amount": dish_detail.amount,
                    }
                    for dish_detail in order_details.orderdishdetails_set.filter(
                        cancel=False
                    )
                ],
            }
        )

    return JsonResponse({"data": orders_data}, safe=False)


def complete_order(request):
    if request_handlers.request_type(request, "POST"):
        data = json.loads(request.body)
        order_id = data.get("orderId")
        order = OrderDetails.objects.filter(
            order_id=order_id, deleted_status=False
        ).first()
        if not order:
            return JsonResponse(
                {"msg": "Order not found"}, status=status_code.BAD_REQUEST
            )

        order_log = OrderLogs.objects.filter(order=order, level=2).first()
        if order_log:
            order_log.order_status = Dropdown.objects.filter(
                parent="Completed", child__parent="FOOD STATUS"
            ).first()
            order_log.save()
            OrderLogs.objects.create(
                order=order,
                level=3,
                order_status=Dropdown.objects.filter(
                    parent="Pending", child__parent="CUSTOMER STATUS"
                ).first(),
            )

            return JsonResponse({"msg": "Order completed successfully"}, status=200)
        else:
            return JsonResponse(
                {"msg": "Order log at level 2 not found"},
                status=status_code.BAD_REQUEST,
            )

    return JsonResponse(
        {"msg": "Invalid request method"}, status=status_code.METHOD_NOT_ALLWOED
    )


def receive_order(request):
    if request_handlers.request_type(request, "POST"):
        data = json.loads(request.body)

        order_id = data.get("orderId")

        order = OrderDetails.objects.filter(
            order_id=order_id, deleted_status=False
        ).first()
        if not order:
            return JsonResponse(
                {"msg": "Order not found"}, status=status_code.BAD_REQUEST
            )
        order_log = OrderLogs.objects.filter(order=order, level=3).first()
        if order_log:
            order_log.order_status = Dropdown.objects.filter(
                parent="Recieved", child__parent="CUSTOMER STATUS"
            ).first()
            order_log.save()
            return JsonResponse(
                {"msg": "Order status updated to received successfully"}, status=200
            )
        else:
            return JsonResponse(
                {"msg": "Order log not found"}, status=status_code.BAD_REQUEST
            )

    return JsonResponse(
        {"msg": "Invalid request method"}, status=status_code.METHOD_NOT_ALLWOED
    )


def manage_orders(request):
    if request_handlers.request_type(request, "GET"):
        restaurant = OwnerDetails.objects.filter(
            owner=request.user, deleted_status=False
        ).first()
        order_data = OrderDetails.objects.filter(
            restaurant=restaurant, deleted_status=False
        )

        orders = []
        for order in order_data:
            owner_order_log = (
                OrderLogs.objects.filter(order=order, level=1)
                .order_by("-created_time")
                .first()
            )

            chef_order_log = (
                OrderLogs.objects.filter(order=order, level=2)
                .order_by("-created_time")
                .first()
            )

            receiver_status_log = (
                OrderLogs.objects.filter(order=order, level=3)
                .order_by("-created_time")
                .first()
            )

            if not owner_order_log:
                continue

            dish_details = OrderDishDetails.objects.filter(order=order, cancel=False)
            dishes = [
                {
                    "dish_id": dish_detail.dish.id,
                    "dish_name": dish_detail.dish.name,
                    "quantity": dish_detail.quantity,
                    "amount": dish_detail.amount,
                    "id": dish_detail.id,
                }
                for dish_detail in dish_details
            ]

            orders.append(
                {
                    "order_id": order.order_id,
                    "order_status": (
                        owner_order_log.order_status.parent
                        if owner_order_log.order_status
                        else None
                    ),
                    "payment_status": (
                        order.payment_status.parent if order.payment_status else None
                    ),
                    "food_status": (
                        chef_order_log.order_status.parent
                        if chef_order_log and chef_order_log.order_status
                        else None
                    ),
                    "payment_id": (
                        order.payment_id
                        if order.payment_status
                        and order.payment_status.parent == "Success"
                        else None
                    ),
                    "total_amount": order.total_amount,
                    "order_time": (
                        order.created_time.isoformat() if order.created_time else None
                    ),
                    "order_receiving_time": (
                        order.order_time.isoformat() if order.order_time else None
                    ),
                    "dishes": dishes,
                    "receiver_status": (
                        receiver_status_log.order_status.parent
                        if receiver_status_log and receiver_status_log.order_status
                        else None
                    ),
                }
            )

        return JsonResponse({"data": orders}, status=200)

    else:
        return JsonResponse(
            {"msg": status_message.METHOD_NOT_ALLOWED},
            status=status_code.METHOD_NOT_ALLWOED,
        )
