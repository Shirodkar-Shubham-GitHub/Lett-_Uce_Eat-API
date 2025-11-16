from rest_framework.views import APIView
from django.db import transaction
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Q
from django.conf import settings
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMessage
import razorpay


class RegisterAPI(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        data = {
            "username": request.data.get("username"),
            "email": request.data.get("email"),
            "password": request.data.get("password"),
        }

        serializer = RegisterSerializer(data=data)

        if serializer.is_valid():
            try:
                # Save the user and create an instance
                serializer.save()
                new_user = serializer.instance

                # 1. Send email to the admin notifying about the new registration
                subject_admin = f'New User Registered: {new_user.username}'
                message_admin = f"""
                Dear Admin,

                A new user has registered on the Lett' uce Eat platform and their profile is awaiting completion.

                ------------------------------------------------------------
                User Name: {new_user.username}
                Email: {new_user.email}
                ------------------------------------------------------------

                Please review the user's profile and ensure they fill out all necessary details, especially their address, for easy tracking.

                ------------------------------------------------------------

                Best regards,  
                Lett' uce Eat System Notification
                """
                admin_email = settings.ADMIN_EMAIL
                recipient_list_admin = [admin_email]
                admin_email_message = EmailMessage(subject_admin, message_admin, settings.EMAIL_HOST_USER, recipient_list_admin)
                admin_email_message.send()

                # 2. Send email to the user informing them their registration is complete and to complete their profile
                subject_user = "Registration Complete - Please Complete Your Profile"
                message_user = f"""
                Dear {new_user.username},

                Congratulations! Your registration on the Lett' uce Eat platform is complete. To make it easier for us to track and serve you better, please make sure to fill out your profile, especially your address details.

                Please visit your profile page to complete your details:
                [Profile Update Link Here]

                Best regards,
                Lett' uce Eat Team
                """
                user_email_message = EmailMessage(subject_user, message_user, settings.EMAIL_HOST_USER, [new_user.email])
                user_email_message.send()

                return Response({
                    "success": True,
                    "message": "User created successfully. Please check your email to complete your profile (user) and notify admin (admin)."
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

class GoogleAuthView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Expects: { "token": "GOOGLE_ID_TOKEN" }
        """
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=400)

        # Verify Google token
        google_resp = requests.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        )
        if google_resp.status_code != 200:
            return Response({"error": "Invalid Google token"}, status=400)

        data = google_resp.json()
        email = data.get("email")
        name = data.get("name", "")

        if not email:
            return Response({"error": "Email not provided"}, status=400)

        first_name, last_name = (
            name.split(" ", 1) if " " in name else (name, "")
        )

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                "username": email.split("@")[0],
                "first_name": first_name,
                "last_name": last_name,
            },
        )

        # Send email to admin
        if created:
            # Only send the admin email if the user is newly created
            subject_admin = f'New User Logged In via Google: {user.username}'
            message_admin = f"""
            Dear Admin,

            A new user has logged in to the Lett' uce Eat platform via Google.

            ------------------------------------------------------------
            User Name: {user.username}
            Email: {user.email}
            ------------------------------------------------------------

            Please review the user's profile and ensure they fill out all necessary details, especially their address, for easy tracking.

            ------------------------------------------------------------

            Best regards,  
            Lett' uce Eat System Notification
            """
            admin_email = settings.ADMIN_EMAIL
            recipient_list_admin = [admin_email]
            admin_email_message = EmailMessage(subject_admin, message_admin, settings.EMAIL_HOST_USER, recipient_list_admin)
            admin_email_message.send()

        # Send email to user
        subject_user = "Login Successful - Complete Your Profile"
        message_user = f"""
        Dear {user.username},

        Congratulations! You have successfully logged in to the Lett' uce Eat platform using your Google account. To make it easier for us to track and serve you better, please make sure to fill out your profile, especially your address details.

        Please visit your profile page to complete your details:
        [Profile Update Link Here]

        Best regards,
        Lett' uce Eat Team
        """
        user_email_message = EmailMessage(subject_user, message_user, settings.EMAIL_HOST_USER, [user.email])
        user_email_message.send()

        # Generate and return JWT tokens for the authenticated user
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            }
        )

class HeroPageListAPI(APIView):

    @transaction.atomic
    def get(self, request):

        try:
            # Query Params
            search_query = request.query_params.get('search', '').strip()

            menu_items = MenuItem.objects.filter(is_deleted=False, is_available=True)

            if search_query:
                menu_items = menu_items.filter(
                    Q(name__icontains=search_query) |
                    Q(cuisine__icontains=search_query) |
                    Q(diet_type__icontains=search_query)
                    )

            menu_items = menu_items.order_by('-created_at')[:3]

            serializer = HeroPageSerializer(menu_items, many=True)

            cuisines = MenuItem.objects.values_list('cuisine', flat=True).distinct()

            response = []
            for code in cuisines:
                label = dict(Cuisines.choices).get(code, code)
                response.append({'code': code, 'label': label})

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
                'cuisines': response,
                'dish_details': serializer.data
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })

class MenuCardListAPI(APIView):

    @transaction.atomic
    def get(self, request):

        try:
            # Query Params
            search_query = request.query_params.get('search', '').strip()
            cuisines = request.query_params.getlist('cuisine', [])
            diet_type = request.query_params.getlist('diettype', [])
            goal_value = request.query_params.get('goal', None)
            sort_by = request.query_params.get('sort', '').strip().lower()

            menu_items = MenuItem.objects.filter(is_deleted=False, is_available=True)

            # Search (case-insensitive match)
            if search_query:
                menu_items = menu_items.filter(
                    Q(name__icontains=search_query) |
                    Q(cuisine__icontains=search_query) |
                    Q(diet_type__icontains=search_query)
                    )
                
            # Filter by Cuisines (case-insensitive match)
            if cuisines:
                cuisines = [cuisine.strip().lower() for cuisine in cuisines]
                menu_items = menu_items.filter(
                    cuisine__iregex=r'(' + '|'.join(cuisines) + ')'
                )

            # Filter by Diet Type (case-insensitive match)
            if diet_type:
                diet_type = [diettype.strip().lower() for diettype in diet_type]
                menu_items = menu_items.filter(
                    diet_type__iregex=r'(' + '|'.join(diet_type) + ')'
                )

            # Filter by Goal
            if goal_value is not None:
                try:
                    goal_value = float(goal_value)
                    if goal_value < 0 or goal_value > 100000:
                            return Response({"error": "Invalid goal value"}, status=status.HTTP_400_BAD_REQUEST)
                    menu_items = menu_items.filter(price__lte=goal_value)
                except ValueError:
                    return Response({"error": "Invalid goal value"}, status=status.HTTP_400_BAD_REQUEST)
                
            # Sort by Price
            if sort_by == 'price_asc':
                menu_items = menu_items.order_by('price')  # Lowest to highest
            elif sort_by == 'price_desc':
                menu_items = menu_items.order_by('-price')  # Highest to lowest

            # Sort By Badges Later after Order Creations

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
                'dish_details': serializer.data
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })

class DishDetailsCreateAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def post(self, request, slug):  # Accept 'slug' as a parameter from the URL

        try:
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'status': status.HTTP_401_UNAUTHORIZED,
                    'message': 'User is not authenticated'
                })

            # Fetch the MenuItem using the slug from the URL
            menu_item = MenuItem.objects.filter(slug=slug, is_deleted=False, is_available=True).first()

            if not menu_item:
                return Response({
                    'success': False,
                    'message': 'Menu item not found or unavailable',
                    'status': status.HTTP_404_NOT_FOUND,
                    'data': []
                })

            # Get the quantity from the request body (default to 1 if not provided)
            quantity = request.data.get('quantity', 1)

            # Validate that quantity is a positive integer
            if not isinstance(quantity, int) or quantity <= 0:
                return Response({
                    'success': False,
                    'message': 'Invalid quantity. Must be a positive integer.',
                    'status': status.HTTP_400_BAD_REQUEST
                })

            # Create a Cart item (or update if it already exists)
            cart_item, created = Cart.objects.get_or_create(
                is_deleted=False,
                user=request.user,
                menu_item=menu_item,
                defaults={'quantity': quantity}
            )

            # If the cart item already exists, we update the quantity
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            # Serialize the MenuItem associated with the Cart item (menu_item)
            cart_serializer = DishDetailsPageSerializer(cart_item)

            return Response({
                'success': True,
                'status': status.HTTP_201_CREATED if created else status.HTTP_200_OK,
                'message': 'Item added to cart' if created else 'Cart updated',
                'data': cart_serializer.data  # Return the serialized MenuItem data
            })

        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })

class CartListAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def get(self, request):

        try:

            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'status': status.HTTP_401_UNAUTHORIZED,
                    'message': 'User is not authenticated'
                })

            curr_user = request.user

            cart_items = Cart.objects.filter(user=curr_user, is_deleted=False)

            # paginator = LimitOffsetPagination()
            # paginated_queryset = paginator.paginate_queryset(menu_item, request)
            serializer = CartSerializer(cart_items, many=True)

            if not serializer.data:
                return Response({
                    'success': False,
                    'message': 'No records found',
                    'status': status.HTTP_404_NOT_FOUND,
                    'data': []
                })
            
            # paginated_response = paginator.get_paginated_response(serializer.data)
            # Calculate total cart price once
            total_cart_price = sum(item.quantity * item.menu_item.price for item in cart_items if item.menu_item)

            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'message': 'Cart items fetched successfully',
                'data': serializer.data,
                'total_cart_price': total_cart_price
            })

        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })

class CartItemDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def put(self, request, slug):
        try:
            # Ensure the user is authenticated
            user = request.user

            # Fetch the MenuItem using the slug
            menu_item = MenuItem.objects.filter(slug=slug, is_deleted=False).first()
            if not menu_item:
                return Response({
                    "success": False,
                    "message": "Menu item not found or is deleted.",
                    "status": status.HTTP_404_NOT_FOUND
                })

            # Fetch the user's cart item for this MenuItem
            cart_item = Cart.objects.filter(user=user, menu_item=menu_item, is_deleted=False).first()
            if not cart_item:
                return Response({
                    "success": False,
                    "message": "Cart item not found or already deleted.",
                    "status": status.HTTP_404_NOT_FOUND
                })

            # Soft delete the cart item (mark as deleted, don't remove from DB)
            cart_item.is_deleted = True
            cart_item.deleted_at = timezone.now()  # Optionally, you can store when the item was deleted
            cart_item.save()

            return Response({
                "success": True,
                "message": "Cart item has been marked as deleted.",
                "status": status.HTTP_200_OK
            })

        except Exception as e:
            return Response({
                "success": False,
                "message": str(e),
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR
            })

class CreateOrderAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            user = request.user
            cart_items = Cart.objects.filter(user=user, is_deleted=False)

            if not cart_items.exists():
                return Response({
                    'success': False,
                    'message': 'Your cart is empty.'
                }, status=status.HTTP_400_BAD_REQUEST)

            total_amount = sum([item.total_price() for item in cart_items])

            # Create Razorpay order
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            razorpay_order = client.order.create({
                "amount": int(total_amount * 100),
                "currency": "INR",
                "payment_capture": 1
            })
            razorpay_order_id = razorpay_order['id']

            # Create an Order entry for each cart item
            created_orders = []
            for item in cart_items:
                order = Order.objects.create(
                    user=user,
                    dish=item.menu_item,
                    quantity=item.quantity,
                    total_price=item.total_price(),
                    status=OrderStatus.PENDING,
                    razorpay_order_id=razorpay_order_id
                )
                created_orders.append({
                    "order_id": order.id,
                    "dish": order.dish.name,
                    "quantity": order.quantity,
                    "slug": order.slug,
                    "price": float(order.dish.price),
                    "total_price": float(order.total_price),
                    "ordered_date_time": order.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })

            return Response({
                'success': True,
                'message': 'Razorpay order created.',
                'razorpay_order_id': razorpay_order_id,
                'total_amount': float(total_amount),
                'orders': created_orders
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConfirmOrderPaymentAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            user = request.user
            payment_id = request.data.get("razorpay_payment_id")
            order_id = request.data.get("razorpay_order_id")
            signature = request.data.get("razorpay_signature")

            if not all([payment_id, order_id, signature]):
                return Response({
                    "success": False,
                    "message": "Missing payment details."
                }, status=status.HTTP_400_BAD_REQUEST)

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Verify signature
            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': signature
                })
            except razorpay.errors.SignatureVerificationError:
                return Response({
                    "success": False,
                    "message": "Signature verification failed."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Fetch payment details
            payment = client.payment.fetch(payment_id)

            if payment.get("status") != "captured":
                return Response({
                    "success": False,
                    "message": f"Payment not captured yet (status: {payment.get('status')})."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Update Orders
            orders = Order.objects.filter(user=user, razorpay_order_id=order_id)

            if not orders.exists():
                return Response({
                    "success": False,
                    "message": "No orders found for this Razorpay order ID."
                }, status=status.HTTP_404_NOT_FOUND)

            total_amount = 0
            order_details_text = ""

            for order in orders:
                order.status = OrderStatus.CONFIRMED
                order.razorpay_payment_id = payment_id
                order.razorpay_signature = signature
                order.save()

                total_amount += float(order.total_price)
                order_details_text += (
                    f"- {order.dish.name} (Qty: {order.quantity}) — ₹{float(order.total_price)}\n"
                )

            # Clear cart
            Cart.objects.filter(user=user, is_deleted=False).update(is_deleted=True)

            # -----------------------------------------------------------
            # 1️⃣ SEND EMAIL TO USER
            # -----------------------------------------------------------
            subject_user = "Your Order Has Been Successfully Placed!"
            message_user = f"""
            Dear {user.username},

            Thank you for your order on Lett' uce Eat!

            Your payment has been successfully received and your order is now confirmed.

            ------------------------------------------------------------
            ORDER DETAILS
            {order_details_text}
            ------------------------------------------------------------
            Total Amount Paid: ₹{total_amount}
            Payment ID: {payment_id}
            Order Reference: {order_id}
            ------------------------------------------------------------

            Our team will begin processing your order shortly.

            Thank you for choosing Lett' uce Eat!
            """

            EmailMessage(
                subject_user,
                message_user,
                settings.EMAIL_HOST_USER,
                [user.email]
            ).send()

            # -----------------------------------------------------------
            # 2️⃣ SEND EMAIL TO ADMIN
            # -----------------------------------------------------------
            admin_email = settings.ADMIN_EMAIL

            subject_admin = f"New Order Placed by {user.username}"
            message_admin = f"""
            Dear Admin,

            A new order has been successfully confirmed on Lett' uce Eat.

            ------------------------------------------------------------
            USER DETAILS
            Name: {user.username}
            Email: {user.email}
            ------------------------------------------------------------

            ORDER DETAILS
            {order_details_text}
            ------------------------------------------------------------
            Total Amount Paid: ₹{total_amount}
            Razorpay Order ID: {order_id}
            Razorpay Payment ID: {payment_id}
            ------------------------------------------------------------

            Please review the order and continue with the processing workflow.

            Regards,
            Lett' uce Eat System Notification
            """

            EmailMessage(
                subject_admin,
                message_admin,
                settings.EMAIL_HOST_USER,
                [admin_email]
            ).send()

            # -----------------------------------------------------------

            return Response({
                "success": True,
                "message": "Order payment confirmed successfully.",
                "orders": [
                    {
                        "order_id": o.id,
                        "dish": o.dish.name,
                        "quantity": o.quantity,
                        "total_price": float(o.total_price)
                    } for o in orders
                ]
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CartClearAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def post(self, request):
        user = request.user
        # Fetch the cart items
        cart_items = Cart.objects.filter(user=user, is_deleted=False)

        # Delete the cart items
        cart_items.update(is_deleted=True)

        return Response({
            'success': True,
            'message': 'Cart cleared successfully',
            'status': status.HTTP_200_OK
        })

class PastOrderListAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def get(self, request):

        try:
            order_items = Order.objects.filter(is_deleted=False, user=request.user, status=OrderStatus.DELIVERED).order_by('-created_at')


            serializer = PastOrderSerializer(order_items, many=True)

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
                'past_orders_list': serializer.data
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })

class MenuItemListAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def get(self, request):

        try:

            # if MenuItem.objects.filter(is_available=False):    #    Not in this API
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_204_NO_CONTENT,
            #         'message': 'No items available'
            #     })

            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            menu_item = MenuItem.objects.filter(is_deleted=False, is_available=True)

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
                'message': 'All Menu Items fetched successfuly',
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
                "image": request.data.get("image"),
                "name": request.data.get("name"),
                "price": request.data.get("price"),
                "is_available": request.data.get("is_available"),
                "cuisine": request.data.get("cuisine"),
                "diet_type": request.data.get("diet_type"),
                "badges": request.data.get("badges", [])
            }

            serializer = MenuItemSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": status.HTTP_201_CREATED,
                    "message": "Menu Item created successfully",
                    "data": serializer.data
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

# class MenuItemByIDAPI(APIView):

#     # permission_classes = [IsAuthenticated]
#     # authentication_classes = [JWTAuthentication]

#     def get(self, request, slug):
#         try:
#             # if not request.user.is_authenticated:
#             #     return Response({
#             #         'success': False,
#             #         'status': status.HTTP_401_UNAUTHORIZED,
#             #         'message': 'User is not authenticated'
#             #     })

#             try:
#                 menu = get_object_or_404(MenuItem, slug=slug)
#             except MenuItem.DoesNotExist:
#                 return Response({
#                     'success': False,
#                     'message': 'Menu Items record not found',
#                     'status': status.HTTP_404_NOT_FOUND,
#                     'data': []
#                 })
            
#             serializer = MenuItemSerializer(menu)

#             return Response({
#                     'success': True,
#                     'message': 'Menu Items details updated successfully',
#                     'status': status.HTTP_200_OK,
#                     'data': serializer.data
#                 })
#         except Exception as e:
#                 return Response({
#                     'success': False,
#                     'message': 'Something went wrong',
#                     'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     'data': serializer.errors
#                 })
        
class MenuItemUpdateAPI(APIView):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def put(self, request, slug):

        try:
            # if not request.user.is_authenticated:
            #     return Response({
            #         'success': False,
            #         'status': status.HTTP_401_UNAUTHORIZED,
            #         'message': 'User is not authenticated'
            #     })

            menu_item = MenuItem.objects.get(slug=slug)

        except MenuItem.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Menu Item record not found',
                'status': status.HTTP_404_NOT_FOUND,
                'data': []
            })
        
        data = {
                "image": request.data.get("image"),
                "name": request.data.get("name"),
                "price": request.data.get("price"),
                "is_available": request.data.get("is_available"),
                # "quantity": request.data.get("quantity"),
                "cuisine": request.data.get("cuisine"),
                "diet_type": request.data.get("diet_type"),
                "badges": request.data.get("badges"),
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
    def put(self, request, slug):

        try:

            try:
                # if not request.user.is_authenticated:
                #     return Response({
                #         'success': False,
                #         'status': status.HTTP_401_UNAUTHORIZED,
                #         'message': 'User is not authenticated'
                #     })

                menu_item = MenuItem.objects.get(slug=slug)
            
            except MenuItem.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Menu Item record not found',
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

class ActiveOrderListAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def get(self, request):

        try:

            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'status': status.HTTP_401_UNAUTHORIZED,
                    'message': 'User is not authenticated'
                })

            order = Order.objects.filter(is_deleted=False, user=request.user, status__in=[OrderStatus.CONFIRMED, OrderStatus.OUT_FOR_DELIVERY]).order_by('-created_at')

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
                'message': 'Order records fetched successfullly',
                'data': paginated_response.data
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
            })

class PastOrderListAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic
    def get(self, request):

        try:
            order_items = Order.objects.filter(is_deleted=False, user=request.user, status=OrderStatus.DELIVERED).order_by('-created_at')


            serializer = PastOrderSerializer(order_items, many=True)

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
                'past_orders_list': serializer.data
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e)
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
                'message': 'Contact record fetched successfully',
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

