from rest_framework.views import APIView
from django.db import transaction
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Sum, F
from django.forms import DecimalField


class RegisterAPI(APIView):

    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):

        data = {
            "username": request.data.get("username"),
            "email": request.data.get("email"),
            "password": request.data.get("password"),
            "phone": request.data.get("phone")
        }

        serializer = RegisterSerializer(data=data)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    "success": True,
                    "message": "User created successfully"
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "success": False,
                    "message": f"An error occurred: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "success": False,
                "message": "Invalid data",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

class ProfileListAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:

            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            profile = request.user

            serializer = ProfileSerializer(profile)
            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'Profile retrieved successfully',
                'data': serializer.data
            })
        except Profile.DoesNotExist:
            return Response({
                'success': False,
                'status': status.HTTP_404_NOT_FOUND,
                'message': 'Profile not found'
            })
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })

class ProfileCreateAPI(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def post(self, request):
        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            data = {
                "user": request.user.id,
                "auth_token": request.data.get("auth_token"),
                "is_verified": request.data.get("is_verified", False)
            }

            serializer = ProfileSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'status': status.HTTP_201_CREATED,
                    'message': 'Profile created successfully',
                    'data': serializer.data
                })
            else:
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': 'Invalid input',
                    'errors': serializer.errors
                })
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })

class ProfileUpdateAPI(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def put(self, request):
        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            profile = request.user

            data = {
                "auth_token": request.data.get("auth_token", profile.auth_token),
                "is_verified": request.data.get("is_verified", profile.is_verified)
            }

            serializer = ProfileSerializer(profile, data=data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'status': status.HTTP_200_OK,
                    'message': 'Profile updated successfully',
                    'data': serializer.data
                })
            else:
                return Response({
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': 'Invalid input',
                    'errors': serializer.errors
                })

        except Profile.DoesNotExist:
            return Response({
                'success': False,
                'status': status.HTTP_404_NOT_FOUND,
                'message': 'Profile not found'
            })
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })

class ProfileDeleteAPI(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def put(self, request):
        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            profile = request.user.profile

            profile.is_deleted = True  # Add this field to the model if not already
            profile.save()

            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'Profile deleted successfully (soft delete)'
            })

        except Profile.DoesNotExist:
            return Response({
                'success': False,
                'status': status.HTTP_404_NOT_FOUND,
                'message': 'Profile not found'
            })
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })

class HeroPageListAPI(APIView):

    @transaction.atomic
    def get(self, request):

        try:
            menu_items = MenuItem.objects.filter(is_deleted=False).order_by('-created_at')[:3]

            serializer = HeroPageSerializer(menu_items, many=True)

            if not serializer.data:
                return Response({
                    'success': False,
                    'message': 'No records found',
                    'status': status.HTTP_404_NOT_FOUND,
                    'data': []
                })

            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'Data fetched successfully',
                'data': serializer.data
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })
        

class ActiveOrdersListAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def get(self, request):
        try:
            order_items = OrderItem.objects.filter(
                is_deleted=False,
                order__customer=request.user,
                order__status=OrderStatus.PENDING
            ).select_related('order', 'menu_item')  # Optimize

            menu_items = MenuItem.objects.filter(
                order_items__in=order_items
            ).distinct()

            serializer = HeroPageSerializer(menu_items, many=True)

            total_quantity = order_items.aggregate(
                total_qty=Sum('quantity')
            )['total_qty'] or 0

            total_amount = order_items.aggregate(
                total_amt=Sum(
                    F('quantity') * F('price'),  # Make sure `price` exists on OrderItem
                    output_field=DecimalField()
                )
            )['total_amt'] or 0.00

            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'Cart data fetched successfully',
                'total_quantity': total_quantity,
                'total_amount': float(total_amount),
                'data': serializer.data
            })

        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })
        

class CartItemCreateAPI(APIView):
    def post(self, request):
        menu_item_id = request.data.get('menu_item_id')
        quantity = request.data.get('quantity', 1)

        try:
            menu_item = MenuItem.objects.get(id=menu_item_id)
        except MenuItem.DoesNotExist:
            return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get or create the active order (cart) for this user
        order, created = Order.objects.get_or_create(user=request.user, status='cart')

        # Add item to the cart
        order_item = OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)

        return Response({'message': 'Item added to cart'}, status=status.HTTP_201_CREATED)


class OrderPostDetailsListAPI(APIView):
    def post(self, request):
        try:
            order = Order.objects.get(user=request.user, status='cart')
        except Order.DoesNotExist:
            return Response({'error': 'No active cart found'}, status=status.HTTP_404_NOT_FOUND)

        # Finalize the order
        order.status = 'ordered'
        order.ordered_at = timezone.now()
        order.save()

        return Response({'message': 'Order placed successfully'}, status=status.HTTP_200_OK)


class OrderDetailsListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # ========= ACTIVE ORDERS =========
            active_orders = Order.objects.filter(
                is_deleted=False,
                customer=request.user,
                status=OrderStatus.PENDING
            ).prefetch_related('items__menu_item')

            active_data = []
            total_active_amount = 0.00

            for order in active_orders:
                for item in order.items.all():
                    item_total = item.quantity * item.price
                    total_active_amount += float(item_total)

                    active_data.append({
                        "ordered_date_time": order.created_at,
                        "menu_name": item.menu_item.name,
                        "price": float(item.price),
                        "quantity": item.quantity,
                        "item_total": float(item_total),
                        "order_status": order.status
                    })

            # ========= PAST ORDERS (DELIVERED) =========
            delivered_orders = Order.objects.filter(
                is_deleted=False,
                customer=request.user,
                status=OrderStatus.DELIVERED
            ).prefetch_related('items__menu_item')

            past_data = []

            for order in delivered_orders:
                for item in order.items.all():
                    past_data.append({
                        "ordered_date_time": order.created_at,
                        "menu_name": item.menu_item.name,
                        "price": float(item.price),
                        "order_status": order.status,
                        "delivery_date_time": order.updated_at
                    })

            return Response({
                "success": True,
                "status": status.HTTP_200_OK,
                "message": "Order data fetched successfully.",
                "active_orders": {
                    "total_amount": total_active_amount,
                    "number_of_orders": active_orders.count(),
                    "orders": active_data
                },
                "past_orders": {
                    "number_of_orders": delivered_orders.count(),
                    "orders": past_data
                }
            })

        except Exception as e:
            return Response({
                "success": False,
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e)
            })

class OrderListAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def get(self, request):

        try:

            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            order = Order.objects.filter(is_deleted=False)

            paginator = LimitOffsetPagination()
            paginated_queryset = paginator.paginate_queryset(order, request)
            serializer = OrderSerializer(paginated_queryset, many=True)

            if not serializer.data:
                return Response({
                    'success': False,
                    'message': 'No records found',
                    'status': status.HTTP_404_NOT_FOUND,
                    'data': []
                })
            
            paginated_response = paginator.get_paginated_response(serializer.data)

            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'All verified account details',
                'data': paginated_response.data
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })

class OrderCreateAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]
    
    @transaction.atomic
    def post(self, request):

        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            data = {
                "customer": request.data.get("customer"),
                "status": request.data.get("status")
            }

            serializer = OrderSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": status.HTTP_201_CREATED,
                    "message": "Order created successfully"
                })

            else:
                return Response({
                    "success": False,
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Please input valid data.",
                    "errors": serializer.errors
                })

        except Exception as e:
           
            return Response({
            "success": False,
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": str(e)
            })

class OrderUpdateAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def put(self, request, pk):

        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            order = Order.objects.get(pk=pk)

        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found',
                'status': status.HTTP_404_NOT_FOUND,
                'data': []
            })
        
        data = {
                "customer": request.data.get("customer"),
                "status": request.data.get("status")
            }

        serializer = OrderSerializer(order, data=data)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Order updated successfully',
                    'status': status.HTTP_200_OK,
                    'data': serializer.data
                })
            except Exception as e:
                return Response({
                    'success': False,
                    'message': 'Something went wrong',
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'data': serializer.errors
                })
        else:
            return Response({
                'success': False,
                'message': 'Please enter valid input',
                'status': status.HTTP_400_BAD_REQUEST,
                'data': serializer.errors
            })

class OrderDeleteAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def put(self, request, pk):

        try:

            try:
                # if not request.user.is_authenticated:
                #     return Response({
                #         'success': False,
                #         'status': status.HTTP_401_UNAUTHORIZED,
                #         'message': 'User is not authenticated'
                #     })

                order = Order.objects.get(pk=pk)
            
            except Order.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Order not found',
                    'status': status.HTTP_404_NOT_FOUND,
                    'data': []
                })
            
            order.is_deleted = True
            order.save()

            return Response({
                    'success': True,
                    'message': 'Order deleted successfully',
                    'status': status.HTTP_200_OK
                })

        except Exception as e:
            return Response({
                'success': False,
                'message': 'Something went wrong. Please try again later',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'data': str(e)
            })

class MenuItemListAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def get(self, request):

        try:

            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            menu_item = MenuItem.objects.filter(is_deleted=False)

            paginator = LimitOffsetPagination()
            paginated_queryset = paginator.paginate_queryset(menu_item, request)
            serializer = MenuItemSerializer(paginated_queryset, many=True)

            if not serializer.data:
                return Response({
                    'success': False,
                    'message': 'No records found',
                    'status': status.HTTP_404_NOT_FOUND,
                    'data': []
                })
            
            paginated_response = paginator.get_paginated_response(serializer.data)

            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'All verified account details',
                'data': paginated_response.data
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })
        
class MenuItemCreateAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]
    
    @transaction.atomic
    def post(self, request):

        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            data = {
                "name": request.data.get("name"),
                "description": request.data.get("description"),
                "price": request.data.get("price"),
                "is_available": request.data.get("is_available"),
                "image": request.data.get("image")
            }

            serializer = MenuItemSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": status.HTTP_201_CREATED,
                    "message": "Menu Item created successfully"
                })

            else:
                return Response({
                    "success": False,
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Please input valid data.",
                    "errors": serializer.errors
                })

        except Exception as e:
           
            return Response({
            "success": False,
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": str(e)
            })


class MenuItemByIDAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    def get(self, request, pk):
        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            try:
                fund = get_object_or_404(Fund, pk=pk)
                print(fund, "   fund fund fund fund fund fund fund fund fund   ")
                donates_count = Donate.objects.filter(donate_fund=fund).count()
                print(donates_count, "   donates_count donates_count donates_count donates_count donates_count donates_count   ")
            except Fund.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Fund record not found',
                    'status': status.HTTP_404_NOT_FOUND,
                    'data': []
                })
           
            serializer = FundSerializer(fund)

            print(serializer, "   serializer serializer serializer serializer serializer serializer serializer   ")

            return Response({
                    'success': True,
                    'message': 'Fund details updated successfully',
                    'status': status.HTTP_200_OK,
                    'data': serializer.data
                })
        except Exception as e:
                return Response({
                    'success': False,
                    'message': 'Something went wrong',
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'data': serializer.errors
                })
        
class MenuItemUpdateAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def put(self, request, pk):

        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            menu_item = MenuItem.objects.get(pk=pk)

        except MenuItem.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Menu Item not found',
                'status': status.HTTP_404_NOT_FOUND,
                'data': []
            })
        
        data = {
                "name": request.data.get("name"),
                "description": request.data.get("description"),
                "price": request.data.get("price"),
                "is_available": request.data.get("is_available"),
                "image": request.data.get("image")
            }
        
        serializer = MenuItemSerializer(menu_item, data=data)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Menu item updated successfully',
                    'status': status.HTTP_200_OK,
                    'data': serializer.data
                })
            except Exception as e:
                return Response({
                    'success': False,
                    'message': 'Something went wrong',
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'data': serializer.errors
                })
        else:
            return Response({
                'success': False,
                'message': 'Please enter valid input',
                'status': status.HTTP_400_BAD_REQUEST,
                'data': serializer.errors
            })

class MenuItemDeleteAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def put(self, request, pk):

        try:

            try:
                # if not request.user.is_authenticated:
                #     return Response({
                #         'success': False,
                #         'status': status.HTTP_401_UNAUTHORIZED,
                #         'message': 'User is not authenticated'
                #     })

                menu_item = MenuItem.objects.get(pk=pk)
            
            except MenuItem.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Menu Item not found',
                    'status': status.HTTP_404_NOT_FOUND,
                    'data': []
                })
            
            menu_item.is_deleted = True
            menu_item.save()

            return Response({
                    'success': True,
                    'message': 'Menu Item deleted successfully',
                    'status': status.HTTP_200_OK
                })

        except Exception as e:
            return Response({
                'success': False,
                'message': 'Something went wrong. Please try again later',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'data': str(e)
            })

class OrderItemListAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def get(self, request):

        try:

            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            order_items = OrderItem.objects.filter(is_deleted=False)

            paginator = LimitOffsetPagination()
            paginated_queryset = paginator.paginate_queryset(order_items, request)
            serializer = OrderItemSerializer(paginated_queryset, many=True)

            if not serializer.data:
                return Response({
                    'success': False,
                    'message': 'No records found',
                    'status': status.HTTP_404_NOT_FOUND,
                    'data': []
                })
            
            paginated_response = paginator.get_paginated_response(serializer.data)

            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'All verified account details',
                'data': paginated_response.data
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })

class OrderItemCreateAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]
    
    @transaction.atomic
    def post(self, request):

        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            data = {
                "order": request.data.get("order"),
                "menu_item": request.data.get("menu_item"),
                "quantity": request.data.get("quantity"),
                "price": request.data.get("price")
            }

            serializer = OrderItemSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": status.HTTP_201_CREATED,
                    "message": "Order Item created successfully"
                })

            else:
                return Response({
                    "success": False,
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Please input valid data.",
                    "errors": serializer.errors
                })

        except Exception as e:
           
            return Response({
            "success": False,
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": str(e)
            })

class OrderItemUpdateAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def put(self, request, pk):

        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            menu_items = OrderItem.objects.get(pk=pk)

        except OrderItem.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order Item not found',
                'status': status.HTTP_404_NOT_FOUND,
                'data': []
            })
        
        data = {
                "order": request.data.get("order"),
                "menu_item": request.data.get("menu_item"),
                "quantity": request.data.get("quantity"),
                "price": request.data.get("price")
            }
        
        serializer = OrderItemSerializer(menu_items, data=data)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Order item updated successfully',
                    'status': status.HTTP_200_OK,
                    'data': serializer.data
                })
            except Exception as e:
                return Response({
                    'success': False,
                    'message': 'Something went wrong',
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'data': serializer.errors
                })
        else:
            return Response({
                'success': False,
                'message': 'Please enter valid input',
                'status': status.HTTP_400_BAD_REQUEST,
                'data': serializer.errors
            })

class OrderItemDeleteAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def put(self, request, pk):

        try:

            try:
                # if not request.user.is_authenticated:
                #     return Response({
                #         'success': False,
                #         'status': status.HTTP_401_UNAUTHORIZED,
                #         'message': 'User is not authenticated'
                #     })

                order_items = OrderItem.objects.get(pk=pk)
            
            except OrderItem.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Order Item not found',
                    'status': status.HTTP_404_NOT_FOUND,
                    'data': []
                })
            
            order_items.is_deleted = True
            order_items.save()

            return Response({
                    'success': True,
                    'message': 'Order Item deleted successfully',
                    'status': status.HTTP_200_OK
                })

        except Exception as e:
            return Response({
                'success': False,
                'message': 'Something went wrong. Please try again later',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'data': str(e)
            })

class DeliveryAddressListAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def get(self, request):

        try:

            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            address = DeliveryAddress.objects.filter(is_deleted=False)

            paginator = LimitOffsetPagination()
            paginated_queryset = paginator.paginate_queryset(address, request)
            serializer = DeliveryAddressSerializer(paginated_queryset, many=True)

            if not serializer.data:
                return Response({
                    'success': False,
                    'message': 'No records found',
                    'status': status.HTTP_404_NOT_FOUND,
                    'data': []
                })
            
            paginated_response = paginator.get_paginated_response(serializer.data)

            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'All verified account details',
                'data': paginated_response.data
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })

class DeliveryAddressCreateAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]
    
    @transaction.atomic
    def post(self, request):

        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            data = {
                "address": request.data.get("address"),
                "city": request.data.get("city"),
                "postal_code": request.data.get("postal_code"),
                "contact_phone": request.data.get("contact_phone")
            }

            serializer = DeliveryAddressSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": status.HTTP_201_CREATED,
                    "message": "Delivery address created successfully"
                })

            else:
                return Response({
                    "success": False,
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Please input valid data.",
                    "errors": serializer.errors
                })

        except Exception as e:
           
            return Response({
            "success": False,
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": str(e)
            })

class DeliveryAddressUpdateAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def put(self, request, pk):

        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            address = DeliveryAddress.objects.get(pk=pk)

        except DeliveryAddress.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Delivery address does not found',
                'status': status.HTTP_404_NOT_FOUND,
                'data': []
            })

        data = {
                "address": request.data.get("address"),
                "city": request.data.get("city"),
                "postal_code": request.data.get("postal_code"),
                "contact_phone": request.data.get("contact_phone")
            }

        serializer = DeliveryAddressSerializer(address, data=data)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Delivery address updated successfully',
                    'status': status.HTTP_200_OK,
                    'data': serializer.data
                })
            except Exception as e:
                return Response({
                    'success': False,
                    'message': 'Something went wrong',
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'data': serializer.errors
                })
        else:
            return Response({
                'success': False,
                'message': 'Please enter valid input',
                'status': status.HTTP_400_BAD_REQUEST,
                'data': serializer.errors
            })

class DeliveryAddressDeleteAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def put(self, request, pk):

        try:

            try:
                # if not request.user.is_authenticated:
                #     return Response({
                #         'success': False,
                #         'status': status.HTTP_401_UNAUTHORIZED,
                #         'message': 'User is not authenticated'
                #     })

                address = DeliveryAddress.objects.get(pk=pk)
            
            except DeliveryAddress.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Delivery address does not found',
                    'status': status.HTTP_404_NOT_FOUND,
                    'data': []
                })
            
            address.is_deleted = True
            address.save()

            return Response({
                    'success': True,
                    'message': 'Delivery address deleted successfully',
                    'status': status.HTTP_200_OK
                })

        except Exception as e:
            return Response({
                'success': False,
                'message': 'Something went wrong. Please try again later',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'data': str(e)
            })

class ContactListAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def get(self, request):

        try:

            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            contact = Contact.objects.filter(is_deleted=False)

            paginator = LimitOffsetPagination()
            paginated_queryset = paginator.paginate_queryset(contact, request)
            serializer = ContactSerializer(paginated_queryset, many=True)

            if not serializer.data:
                return Response({
                    'success': False,
                    'message': 'No records found',
                    'status': status.HTTP_404_NOT_FOUND,
                    'data': []
                })
            
            paginated_response = paginator.get_paginated_response(serializer.data)

            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'All verified account details',
                'data': paginated_response.data
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })

class ContactCreateAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]
    
    @transaction.atomic
    def post(self, request):

        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            data = {
                "name": request.data.get("name"),
                "email": request.data.get("email"),
                "phone": request.data.get("phone"),
                "message": request.data.get("message")
            }

            serializer = ContactSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": status.HTTP_201_CREATED,
                    "message": "Contact created successfully"
                })

            else:
                return Response({
                    "success": False,
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Please input valid data.",
                    "errors": serializer.errors
                })

        except Exception as e:
           
            return Response({
            "success": False,
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": str(e)
            })

class ContactUpdateAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def put(self, request, pk):

        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            contact = Contact.objects.get(pk=pk)

        except Contact.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Contact not found',
                'status': status.HTTP_404_NOT_FOUND,
                'data': []
            })

        data = {
                "name": request.data.get("name"),
                "email": request.data.get("email"),
                "phone": request.data.get("phone"),
                "message": request.data.get("message")
            }

        serializer = ContactSerializer(contact, data=data)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Contact updated successfully',
                    'status': status.HTTP_200_OK,
                    'data': serializer.data
                })
            except Exception as e:
                return Response({
                    'success': False,
                    'message': 'Something went wrong',
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'data': serializer.errors
                })
        else:
            return Response({
                'success': False,
                'message': 'Please enter valid input',
                'status': status.HTTP_400_BAD_REQUEST,
                'data': serializer.errors
            })
        
class ContactDeleteAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def put(self, request, pk):

        try:

            try:
                # if not request.user.is_authenticated:
                #     return Response({
                #         'success': False,
                #         'status': status.HTTP_401_UNAUTHORIZED,
                #         'message': 'User is not authenticated'
                #     })

                contact = Contact.objects.get(pk=pk)
            
            except Contact.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Contact not found',
                    'status': status.HTTP_404_NOT_FOUND,
                    'data': []
                })
            
            contact.is_deleted = True
            contact.save()

            return Response({
                    'success': True,
                    'message': 'Contact deleted successfully',
                    'status': status.HTTP_200_OK
                })

        except Exception as e:
            return Response({
                'success': False,
                'message': 'Something went wrong. Please try again later',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'data': str(e)
            })
        

