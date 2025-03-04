from django.shortcuts import render,redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage

from rest_framework import status
from .models import *
from .serializers import *
from django.db.models import Q
from django.core.files.uploadedfile import UploadedFile
import json
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
import datetime
from django.contrib.auth.hashers import check_password
import base64

SECRET_KEY = "django-insecure-+k#qrwj!@v*ls7(*xs%8!0wfip@6g^e!v!rn&d5y5d7tuj4vm(" 


class Register_custumer(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        custumers = Customer.objects.all()
        serializer = Register_custumerSerializer(custumers,many =True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if Customer.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)

        # Create new customer with hashed password
        customer = Customer(username=username, password=make_password(password))
        customer.save()

        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = None
        user_type = None

        # Try to get the user from Customer model
        try:
            user = Customer.objects.get(username=username)
            user_type = "customer"
        except Customer.DoesNotExist:
            pass  # If not found, continue checking in Administrator

        # If not found in Customer, try the Administrator model
        if user is None:
            try:
                user = Administrator.objects.get(username=username)
                user_type = "admin"
            except Administrator.DoesNotExist:
                return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

        # Check password
        if not check_password(password, user.password):
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens (Manually create tokens for non-AbstractUser models)

        profile_image_url = None
        if hasattr(user, "profile_image") and user.profile_image:
            profile_image_url = user.profile_image.url
        print(type(getattr(user, "profile_image", None)))

        refresh = RefreshToken()
        refresh.payload["user_id"] = user.id
        refresh.payload["username"] = user.username
        refresh.payload["user_type"] = user_type

        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username,
            "user_type": user_type,
            "profile_img": profile_image_url
        }, status=status.HTTP_200_OK)
        


class Logout_view(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        if "author" in request.session:
            print('the available seesion :',request.session["author"])
            request.session.pop('author')
            print("the session poped",request.session)
            content = {'message': 'logged out'}
            return Response(content)
        else:
            content = {'message': 'cant logged out'}
            return Response(content)


class ProductCategoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request,id=None):
        categories = Product_Category.objects.all()
        serializer = ProductCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductCategorySerializer(data=request.data)
        print("the incoming data",request.data)
        if serializer.is_valid():
            serializer.save()
            print("the saved data is",serializer)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class Product_categoryUpdate(APIView):
    permission_classes = [AllowAny]
    def patch(self,request,id):
        try:
            category = Product_Category.objects.get(id=id)
        except Product_Category.DoesNotExist:
            return Response({"message: no Product_Category found"})
        serializer = ProductCategorySerializer(category,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            print("the saved data is",serializer)
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)
        
    def delete(self,request,id):
        try:
            category_name = Product_Category.objects.get(id=id)
        except Product_Category.DoesNotExist:
            return Response({"message: no Product_Category found"})
        category_name.delete()
        return Response({"message": "Product deleted"}, status=200)





# class ProductListPost(APIView):
#     permission_classes = [AllowAny]
    
#     def get(self,request):
#         product = Product_list.objects.all()
#         serializer = ProductListSerializer(product, many = True)
#         return Response(serializer.data)
    

#     def post(self, request):
#         product_data = request.data  # Expecting a single dictionary

#         if not isinstance(product_data, dict):
#             return Response({"error": "Invalid format. Expected a dictionary."}, status=status.HTTP_400_BAD_REQUEST)

#         try:    
#             # Extract product details
#             prize_list = product_data.get('prize_range', [])
#             image_list = product_data.get('product_images', [])

#             # Validate prize_list
#             if not isinstance(prize_list, list) or any(not isinstance(prize, dict) for prize in prize_list):
#                 return Response({"error": "prize_range must be a list of dictionaries."}, status=status.HTTP_400_BAD_REQUEST)

#             # Validate image_list
#             if not isinstance(image_list, list) or any(not isinstance(img, UploadedFile) for img in image_list):
#                 return Response({"error": "product_images must be a list of UploadedFile (URLs or file paths)."},
#                                 status=status.HTTP_400_BAD_REQUEST)

#             # Create product instance
#             product = Product_list.objects.create(
#                 product_name=product_data.get('product_name', 'Default Name'),
#                 product_images=[],  # Start empty
#                 product_description=product_data.get('product_description', 'Default Description'),
#                 product_discount=product_data.get('product_discount', '0%'),
#                 product_offer=product_data.get('product_offer', 'No Offer'),
#                 product_category=product_data.get('product_category', 'Miscellaneous'),
#                 prize_range=[],  # Start empty
#                 product_stock=product_data.get('product_stock', '0')
#             )

#             # Store up to 3 prize ranges
#             for prize in prize_list[:3]:  
#                 product.add_prize_range(prize)

#             # Store up to 5 images
#             for image in image_list[:5]:  
#                 product.add_image(image)

#             serializer = ProductListSerializer(product)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         except ValidationError as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProductListPost(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product_list.objects.all()
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_data = request.data  

        if not isinstance(product_data, dict):
            return Response({"error": "Invalid format. Expected a dictionary."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Extract product details
            prize_list = product_data.get('prize_range', [])
            image_list = request.FILES.getlist('product_images')  # Fix image handling

            # Validate prize_list
            if not isinstance(prize_list, list) or any(not isinstance(prize, dict) for prize in prize_list):
                return Response({"error": "prize_range must be a list of dictionaries."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate image_list
            if not isinstance(image_list, list) or any(not hasattr(img, 'read') for img in image_list):
                return Response({"error": "product_images must be a list of image files."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Create product instance
            product = Product_list.objects.create(
                product_name=product_data.get('product_name', 'Default Name'),
                product_images=[],  # Empty initially
                product_description=product_data.get('product_description', 'Default Description'),
                product_discount=product_data.get('product_discount', '0%'),
                product_offer=product_data.get('product_offer', 'No Offer'),
                product_category=product_data.get('product_category', 'Miscellaneous'),
                prize_range=[],
                product_stock=product_data.get('product_stock', '0')
            )

            # Store up to 3 prize ranges
            for prize in prize_list[:3]:
                product.add_prize_range(prize)

            # Store up to 5 images
            image_urls = []
            for image in image_list[:5]:
                file_path = default_storage.save(f"product_images/{image.name}", ContentFile(image.read()))
                image_urls.append(f"{settings.MEDIA_URL}{file_path}")

            # Save images in JSONField
            product.product_images = image_urls
            product.save()

            serializer = ProductListSerializer(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




class ProduclistView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
            response_data = []
            products = Product_list.objects.all()

            for product in products:
                product_prize = product.prize_range
                print("product_prize is", product_prize)

                try:
                    discount = int(product.product_discount)
                    print('product_discount is:', discount)
                except (ValueError, TypeError):
                    discount = 0  # Default discount is 0 if not valid

                discounted_prices = []
                for prize in product_prize:
                    if 'price' in prize:
                        try:
                            actual_prize = int(prize['price'])
                            print("actual_prize is", actual_prize)

                            final_discount = actual_prize - (actual_prize * discount / 100)
                            print("Final Price after Discount:", final_discount)

                            discounted_prices.append({
                                "actual_price": actual_prize,
                                "final_discount": final_discount
                            })
                            print("The output array is", discounted_prices)
                            
                        except (ValueError, TypeError):
                            continue  # Skip invalid prices

                # Serialize the product data
                serializer = ProductListSerializer(product)
                product_data = serializer.data
                product_data['discounted_prices'] = discounted_prices  # Add discount data

                response_data.append(product_data)

            # Ensure a valid Response is always returned
            return Response(response_data, status=status.HTTP_200_OK)


class Product_updateanddelete(APIView):
    permission_classes = [AllowAny]

    def get(self,request,id):
        product = Product_list.objects.get(id = id)
        serializer = ProductListSerializer(product)
        return Response(serializer.data,status=200)

    def patch(self, request, id):
        try:
            item = Product_list.objects.get(id=id)
        except Product_list.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        data = request.data.copy()  # Copy request data

        # 🛠️ Handle updating a specific index in prize_range
        index = data.pop("index", None)
        new_value = data.pop("new_value", None)

        if index is not None and new_value is not None:
            try:
                index = int(index)  # Convert index to integer
            except (ValueError, TypeError):
                return Response({"error": "index must be an integer"}, status=400)

            if not isinstance(item.prize_range, list):
                return Response({"error": "prize_range is not a list"}, status=400)

            if index < 0 or index >= len(item.prize_range):
                return Response({"error": "Index out of range"}, status=400)

            item.prize_range[index] = new_value
            data["prize_range"] = item.prize_range

        
        item_no = data.pop("item_no", None)
        new_image = request.FILES.get("new_image")  
        print("the item no:",item_no,new_image)


        # Ensure item_no is properly extracted
        if isinstance(item_no, list) and item_no:
            item_no = item_no[0]  # Extract first value

        try:
            item_no = int(item_no)  # Convert to integer
        except (ValueError, TypeError):
            return Response({"error": "item_no must be an integer"}, status=400)

        if item_no is not None and new_image is not None:
            try:
                item_no = int(item_no)  # Convert index to integer
            except (ValueError, TypeError):
                return Response({"error": "item_no must be an integer"}, status=400)
            
            if not isinstance(item.product_images, list):
                return Response({"error": "product_images is not a list"}, status=400)

            if item_no < 0 or item_no >= len(item.product_images):
                return Response({"error": "item_no out of range"}, status=400)

            #  Save new image to media storage

            # Get the full server URL dynamically
            # Get the full server URL dynamically
            domain = settings.SITE_URL if hasattr(settings, "SITE_URL") else f"http://{request.get_host()}"
            file_path = default_storage.save(f"{new_image.name}", ContentFile(new_image.read()))
            # Construct the full URL
            full_url = f"{domain}{settings.MEDIA_URL}{file_path}"

            # Construct the full URL
            
            # file_path = default_storage.save(f"product_images/{new_image.name}", ContentFile(new_image.read()))
            # full_url = f"{domain}{settings.MEDIA_URL}{file_path}"

            #  Replace image at index
            item.product_images[item_no] = full_url
            data["product_images"] = json.dumps(item.product_images)
        serializer = ProductListSerializer(item, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product updated successfully", "data": serializer.data}, status=200)

        return Response(serializer.errors, status=400)


    def delete(self,requestk,id):
        try:
            item = Product_list.objects.get(id=id)
        except Product_list.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)
        item.delete()
        return Response({"message": "Product deleted successfully"}, status=200)
    
    def post(self,request,id):
        try:
            item = Product_list.objects.get(id=id)
        except Product_list.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)
        add_img = request.data.get('product_images')
        print("the extra image",add_img)

        item.add_extra_img(add_img)
        serializer = ProductListSerializer(item)
        print("the append data is",item)
        return Response(serializer.data, status=status.HTTP_200_OK)
       


# storing the search history

class Search_history(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Check if the user is logged in
        user_name = request.session.get("author")  # Assuming "author" stores the logged-in user's ID
        print('user is',user_name)
        if user_name:
            try:
                # Fetch the user from the database
                user = Customer.objects.get(username=user_name)
            except Customer.DoesNotExist:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Get the search history from the request
            term = request.data.get('term')
            print("the term is",term)

            if not term:
                return Response({"error": "Search term is required"}, status=status.HTTP_400_BAD_REQUEST)

         
            user.add_search_term(term)
            serializer = Register_custumerSerializer(user)
            print("the append data is",user)
     


            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No active session found'}, status=status.HTTP_401_UNAUTHORIZED)
        
    
    def get(self, request):
        user_name = request.session.get("author")  # Assuming "author" stores the logged-in user's username
        print('get user is', user_name)
        
        if user_name:
            try:
                # Fetch the user from the database
                user = Customer.objects.get(username=user_name)
                search_data = user.search_history   
                print('the user search history:', search_data)

                if not search_data:
                    return Response({'message': 'Search history is empty'}, status=status.HTTP_204_NO_CONTENT)

                # Collect all matching products for the search terms
                matched_products = Product_list.objects.filter(product_category__in=search_data).distinct()

                if matched_products.exists():
                    serializer = ProductListSerializer(matched_products, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'No matching products found'}, status=status.HTTP_204_NO_CONTENT)

            except Customer.DoesNotExist:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'No session found'}, status=status.HTTP_204_NO_CONTENT)




# view for new arrivals
class Newly_arrived(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Fetch the 5 most recently added products
        products = Product_list.objects.order_by('-created_at')[:5]  # Ensure 'created_at' field exists in your model

        # Serialize the products
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class Home(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)



# profile update
class Profile_update_custumer(APIView):
    permission_classes = [AllowAny]

    def get(self,request,id):
        try:
            customer = Customer.objects.get(id=id)
            serializer = Register_custumerSerializer(customer)
            return Response(serializer.data,status=200)
        except:
            return Response({"error": "Customer not found"},status=400)


    def patch(self, request, id):
        try:
            customer = Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the request data
        request_data = request.data.copy()

        # Handle Address Update Separately (if provided)
        new_address = request_data.pop('address', None)

        if new_address:
            if not isinstance(new_address, dict):
                return Response({'error': 'Address must be a dictionary'}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve existing address data (ensure it's a dictionary)
            existing_address = customer.address if isinstance(customer.address, dict) else {}

            # Merge new data into existing address
            existing_address.update(new_address)

            # Save the updated address
            customer.address = existing_address
            customer.save()

        # Proceed with updating other fields if needed
        serializer = Register_custumerSerializer(customer, data=request_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,id):
        customer = Customer.objects.get(id=id)
        if customer:
            customer.delete()
            return Response({"message": "Customer deleted"}, status=200)
        else:
            return Response({"error": "Customer not found"}, status=400)


# category filtering homescreen
class Category_filter(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
            category = request.data.get('category_name')
            print('Category received:', category)

            check = Product_list.objects.filter(product_category=category)

            if check.exists():  # Check if queryset is not empty
                print('Matching categories:', check)
                serializer = ProductListSerializer(check, many=True)  # Add many=True
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

class Adding_cart(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        products = request.data.get('products')

        print("Received user_id:", user_id)
        print("Received products:", products)

        # Validate data
        if user_id is None:
            return Response({"error": "Invalid data format (user_id missing or products is not a list)"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the user's cart
        cart = Cart_items.objects.filter(user_id=user_id).first()

        if cart:
            # Update the existing cart
            existing_products = {item["id"]: item for item in cart.products}  # Create a dictionary for quick lookup

            for new_product in products:
                product_id = new_product.get("id")
                new_count = int(new_product.get("count", 1))  # Ensure new count is an integer

                if product_id in existing_products:
                    # Convert existing count to integer before addition
                    existing_products[product_id]["count"] = int(existing_products[product_id].get("count", 1)) + new_count
                else:
                    # Ensure count is stored as an integer
                    new_product["count"] = new_count
                    existing_products[product_id] = new_product

            # Update cart products
            cart.products = list(existing_products.values())
            cart.save()
        else:
            # If no cart exists, create a new one and ensure count is stored as an integer
            for product in products:
                product["count"] = int(product.get("count", 1))
            cart = Cart_items.objects.create(user_id=user_id, products=products)

        # Serialize and return response
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
                

    def get(self, request):
        user = request.query_params.get('userid')
        print('Current author is:', user)

        user_cart_items = Cart_items.objects.filter(user_id=user)
        print('User cart items:', user_cart_items)

        if not user_cart_items.exists():
            return Response({"error": "No matching cart items found"}, status=404)

        cart_data = []

        for item in user_cart_items:
            print("Processing Cart Item:", item)
            print("Item Products Data:", item.products)

            for product in item.products:  
                p_id = product.get("id")
                product_count = int(product.get('count', 0))  
                print("Extracted Product ID:", p_id, "Product Count:", product_count)

                if not p_id:
                    continue  

                # Fetch product details
                product_obj = Product_list.objects.filter(id=p_id).first()
                print("Fetched Product Object:", product_obj)

                # Get customer details and individual discount
                invidual = Customer.objects.filter(id=user).first()
                individual_discount = float(invidual.discount_individual) / 100 if invidual and invidual.discount_individual else 0

                print("Individual Discount:", individual_discount)

                # Get product discount
                product_discount = float(product_obj.product_discount) / 100 if product_obj and product_obj.product_discount else 0
                print("Product Discount:", product_discount)

                # Calculate total amount
                total_amount = 0
                if product_obj and product_obj.prize_range:
                    for prize in product_obj.prize_range:
                        start = int(prize.get('from', 0) or 0)
                        end = int(prize.get('to', 0) or 0)
                        price = float(prize.get('price', 0) or 0)

                        print(f"Checking range: from {start} to {end}, price: {price}")

                        if start <= product_count <= end:
                            discount_to_apply = product_discount if product_discount else 0
                            discounted_price = price * (1 - discount_to_apply)
                            total_amount = product_count * discounted_price
                            print("Total Amount for Product:", total_amount)
                            break  

                # Append product details to cart_data
                if product_obj:
                    cart_data.append({
                        "user_id": item.user_id,
                        "username":invidual.username,
                        "product_id":p_id,
                        "total_count": product_count,
                        "product_name": product_obj.product_name,
                        "product_images": product_obj.product_images if product_obj.product_images else None,
                        "product_description": product_obj.product_description,
                        "product_discount": product_obj.product_discount,
                        "individual_discount": individual_discount,
                        "product_offer": product_obj.product_offer,
                        "product_category": product_obj.product_category,
                        "prize_range": product_obj.prize_range,
                        "product_stock": product_obj.product_stock,
                        "total_amount": total_amount,
                    })

                    sum_total = sum(item['total_amount'] for item in cart_data)
                    print("Total before discount:", sum_total)

                    discount_to_user = individual_discount if individual_discount else 0
                    discount_amount = sum_total * discount_to_user  # Calculate discount amount
                    final_price = sum_total - discount_amount  # Subtract discount from total

                    response_data = {
                        "cart_data": cart_data,
                        "sum_total": sum_total,  # Total before discount
                        "discount_amount": discount_amount,  # Discount applied
                        "final_price": final_price  # Total after discount
                    }

                    print("Discount applied:", discount_amount)
                    print("Final total after discount:", final_price)
                

        if not cart_data:
            return Response({"error": "No products found in cart"}, status=400)

        return Response(response_data) 


class Count_order_update(APIView):
    permission_classes = [AllowAny]

    def patch(self, request):
        count = request.data.get('count')
        product_id = request.data.get('product_id')
        user_id = request.data.get("user_id")

        print("Received request data:", count, product_id, user_id)

        # Validate request data
        if None in (count, product_id, user_id):
            return Response({"error": "Missing count, product_id, or user_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the cart for the given user
        cart = Cart_items.objects.filter(user_id=user_id).first()

        if not cart:
            return Response({"error": "Cart not found for the user"}, status=status.HTTP_404_NOT_FOUND)

        print("Cart Items before update:", cart.products)

        # Update the count of the product in the cart
        updated = False
        for item in cart.products:
            if str(item.get('id')) == str(product_id):  # Ensure ID comparison works
                item['count'] = int(count)  # Update the count
                updated = True
                break

        if not updated:
            return Response({"error": "Product not found in cart"}, status=status.HTTP_404_NOT_FOUND)

        # Save updated cart
        cart.save()

        print("Cart Items after update:", cart.products)

        # Serialize and return updated cart
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)




class Delete_all_cart(APIView):
    def post(self,request):
        user = request.data.get('username')
        cart_items = Cart_items.objects.filter(user_id = user)
        if cart_items is not None:
            cart_items.delete()
            return Response({"message": "Cart items deleted succesfully"}, status=200)
        else:
            return Response({"error": "No items found in cart"}, status=400)
    


class order_products(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        user_id = request.data.get('user_id')
        products = request.data.get('products')

        print("Received user_id:", user_id)
        print("Received products:", products)


        # Validate data
        if user_id is None or not isinstance(products, list) :
            return Response({"error": "Invalid data format (user_id missing or products is not a list)"}, status=400)

        # Check if cart already exists for the user
        order_products= Order_products.objects.filter(user_id=user_id).first()

        if order_products:
            # Update existing cart
            order_products.order_add(products)
            serializer = OrderSerializer(order_products)
        else:
            # Create new cart entry
            order_products = Order_products.objects.create(user_id=user_id, product_items=products)
            serializer = OrderSerializer(order_products)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        user = request.data.get('userid')
        print("The userid", user)

        if user is not None:
            order_list = []
            customer = Customer.objects.filter(id=user).first()

            check_order = Order_products.objects.filter(user_id=user).first()
            print("The order item with user:", check_order)

            if check_order:
                for products in check_order.product_items:
                    product_id = products.get("product_id")
                    print("The product ID is:", product_id)

                    # Fetch product from Product_list
                    product_list = Product_list.objects.filter(id=product_id).first()
                    if not product_list:
                        print(f"Skipping product with ID {product_id} (Not Found)")
                        continue  

                    order_list.append(
                        {
                            "user_id": user,
                            "username":customer.username,
                            "product_name": product_list.product_name,
                            "product_images": product_list.product_images
                            if product_list.product_images
                            else None,
                            "product_category": product_list.product_category,
                            "product_stock": product_list.product_stock,
                            "order_status": products.get("order_status"),
                            "total_quantity": products.get("total_count"),
                            "total_amount": products.get("total_amount"),
                        }
                    )

                if not order_list:
                    return Response(
                        {"error": "No products found in order_list"}, status=404
                    )

                return Response(order_list)

            else:
                return Response({"error": "No product found for this username"})

        else:
            return Response({"error": "No User found"})




class UpdateOrderStatus(APIView):
    permission_classes = [AllowAny]
    def patch(self, request):
        order_reject = request.data.get("rejected_product", [])  # List of rejected product IDs
        user_id = request.data.get("user_id")
        order_id = request.data.get("order_id")

        print("The request data list:", order_reject, user_id, order_id)

        # Fetch the order related to the user and order_id
        order = Order_products.objects.filter(user_id=user_id).first()
        print("The order data:", order)

        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Extracting product items (assuming JSONField or dictionary structure)
        product_items_list = order.product_items  
        print("The product_items_list data:", product_items_list)

        updated = False  # Flag to check if any update happens

        for item in product_items_list:
            if item["order_id"] == order_id:
                if item["product_id"] in order_reject:
                    item["order_status"] = "rejected"
                else:
                    item["order_status"] = "accepted"
                updated = True

        # Save changes if any updates were made
        if updated:
            order.product_items = product_items_list
            order.save(update_fields=["product_items"])  # Save only the modified field
            print(f"Order {order.id} updated successfully")
            return Response({"message": "Order updated successfully", "updated_items": product_items_list}, status=status.HTTP_200_OK)

        return Response({"message": "No updates were made"}, status=status.HTTP_400_BAD_REQUEST)

class CancelOrder(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        order_id = request.data.get('order_id')

        # Ensure order_id is a string for consistent comparison
        order_id = str(order_id).strip()

        # Fetch user's order
        order_list = Order_products.objects.filter(user_id=username).first()

        if not order_list:
            return Response({"message": "Order not found"}, status=404)

        if not order_list.product_items:
            return Response({"message": "No products in order"}, status=404)

        print("Product Items before cancellation:", order_list.product_items)

        # Check for a matching order
        updated_items = []
        order_removed = False  # Flag to check if any order was removed

        for item in order_list.product_items:
            print("Checking:", item)  # Debugging

            # Convert order_id to string to ensure comparison works
            item_order_id = str(item.get("order_id")).strip()
            item_status = str(item.get("order_status")).strip().lower()

            if item_order_id == order_id and item_status == "null":
                print("Cancelling Order:", item)
                order_removed = True
                continue  # Skip adding this item (remove it)

            updated_items.append(item)

        if not order_removed:
            return Response({"message": "Order cannot be cancelled or not found"}, status=400)

        # Update the database
        order_list.product_items = updated_items
        order_list.save()

        return Response({"message": "Order cancelled successfully"}, status=200)




class Stock_auto_update(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        order_list = Order_products.objects.all()
        products = Product_list.objects.all()
        updated_products = []  # Store updated products

        for product in products:
            product_id = product.id
            stock = int(product.product_stock)
            print("Product ID & Stock:", product_id, stock)

            for orders in order_list:
                for items in orders.product_items:
                    id_product = items.get('product_id')
                    order_status = items.get('order_status')

                    if str(id_product) == str(product_id) and order_status == "accepted":
                        count = int(items.get('total_count'))
                        print("Order ID:", id_product, "Count:", count, "Order Status:", order_status)

                        # Reduce stock and save
                        product.product_stock = max(stock - count, 0)  # Prevent negative stock
                        product.save()
                        updated_products.append(product)

        # Serialize all updated products
        serializer = ProductListSerializer(updated_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class Total_counts_dashboard(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        active_customer_count = Customer.objects.filter(status=True).count()
        print("Active customers:", active_customer_count)

        order_count = sum(len(order.product_items) for order in Order_products.objects.all() if isinstance(order.product_items, list))
        print("Total product count in all orders:", order_count)

        response_data = {
            "total_products" : Product_list.objects.count(),
            "total_category" : Product_Category.objects.count(),
            "active_customer_count":active_customer_count,
            "order_count":order_count
            }
        return Response(response_data)


class Update_customer_status(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, id):
        # Extract status from request data
        status = request.data.get("status", None)

        # Ensure status is a boolean
        if not isinstance(status, bool):
            return Response({"error": "The request must contain a boolean 'status' field."}, status=400)

        # Get the customer object or return 404
        customer = get_object_or_404(Customer, id=id)

        # Convert boolean to a string to match CharField
        customer.status = status  
        customer.save()

        # Serialize and return updated customer data
        serializer = Register_custumerSerializer(customer)
        return Response(serializer.data, status=200)
        


class Total_orders_list(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        
        order_list = Order_products.objects.all()
        if not order_list:
            return Response({"error": "No order_list found"})
        order_products = []
        for orders in order_list:
            user_id = orders.user_id
            for products in orders.product_items:
                product_id = products.get('product_id')
                order_id = products.get('order_id')
                product_list = Product_list.objects.filter(id=product_id).first()
                if not product_list:
                    print(f"Skipping product with ID {product_id} (Not Found)")
                    continue  
                order_products.append(
                    {
                        'user_id':user_id,
                        'order_id':order_id,
                        # "temp_address": products.get("total_amount"),
                        "permanent_address": products.get('permanent_address'),
                        "product_name": product_list.product_name,
                        "product_images": product_list.product_images
                        if product_list.product_images
                        else None,
                        "product_category": product_list.product_category,
                        "product_stock": product_list.product_stock,
                        "order_status": products.get("order_status"),
                        "total_count": products.get("total_count"),
                        "total_amount": products.get("total_amount"),

                    }
                )

        return Response(order_products,status=200)
            

class Search_all_products(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        search_term = request.data.get("search_term", "").strip()

        if not search_term:
            return Response({"error": "Search term is required"}, status=400)

        def search_products(search_term):
            query = Q()
            for field in Product_list._meta.get_fields():
                if hasattr(field, "attname"):  # Ensures it's a valid field
                    field_name = field.attname
                    field_type = field.get_internal_type()

                    # Apply filtering only to text-based fields
                    if field_type in ["CharField", "TextField"]:
                        query |= Q(**{f"{field_name}__icontains": search_term})  # Case-insensitive search

            return Product_list.objects.filter(query)

        products = search_products(search_term)

        if not products.exists():
            return Response({"message": "No matching products found"}, status=404)
        

        serializer = ProductListSerializer(products, many=True)
        return Response({"products": serializer.data}, status=200)

        # product_data = [{ 
        #     "id": p.id, "name": p.product_name, "category":p.product_category,"product_description":p.product_description,"product_stock":p.product_stock,"product_images":p.product_images if p.product_images else None,"prize_range":p.prize_range,"product_discount":p.product_discount,
        #     } for p in products]
        # return Response({"results": product_data}, status=200)


class SearchAllCustomer(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        search_term = request.data.get("search_term", "").strip()

        if not search_term:
            return Response({"error": "Search term is required"}, status=400)

        def search_customers(search_term):
            query = Q()
            for field in Customer._meta.get_fields():
                if hasattr(field, "attname"):  # Ensures it's a valid field
                    field_name = field.attname
                    field_type = field.get_internal_type()

                    if field_type in ["CharField", "TextField"]:
                        query |= Q(**{f"{field_name}__icontains": search_term})  # Case-insensitive search

            return Customer.objects.filter(query)

        customers = search_customers(search_term)

        if not customers.exists():
            return Response({"message": "No matching customers found"}, status=404)
        
        serializer = Register_custumerSerializer(customers, many=True)
        return Response({"products": serializer.data}, status=200)

        # product_data = [
        #     {
        #         "id": c.id,
        #         "name": c.username,
        #         "profile_image": request.build_absolute_uri(c.profile_image.url) if c.profile_image else None,
        #         "discount_individual": c.discount_individual,
        #         "permanent_adress":c.address,
        #         "phone_number":c.phone_number,
        #         "status":c.status
        #     }
        #     for c in customers
        # ]

        # return Response({"results": product_data}, status=200)




class SearchOrders(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        search_term = request.data.get("search_term", "").strip().lower()

        if not search_term:
            return Response({"error": "Search term is required"}, status=400)

        filtered_orders = []

        # **Step 1: Search in user_id with icontains**
        order_list = Order_products.objects.filter(
            Q(user_id__icontains=search_term)  # Partial match for user_id
        )

        # **Step 2: Search in product_items**
        if not order_list.exists():
            all_orders = Order_products.objects.all()

            for order in all_orders:
                try:
                    product_items = json.loads(order.product_items) if isinstance(order.product_items, str) else order.product_items
                except json.JSONDecodeError:
                    continue  # Skip if JSON is invalid

                matching_products = [
                    product for product in product_items
                    if search_term in str(product.get("order_status", "")).lower()
                    or search_term in str(product.get("order_id", "")).lower()
                    or search_term in str(product.get("order_date", "")).lower()
                    or search_term in str(product.get("product_name", "")).lower()
                    or search_term in str(product.get("product_category", "")).lower()
                ]

                if matching_products:
                    filtered_orders.append({
                        "id": order.id,
                        "user_id": order.user_id,
                        "product_items": matching_products
                    })

        else:
            # Directly add matching orders
            filtered_orders = [
                {"id": order.id, "user_id": order.user_id, "product_items": order.product_items}
                for order in order_list
            ]

        if not filtered_orders:
            return Response({"message": "No matching orders found"}, status=404)

        return Response({"orders": filtered_orders}, status=200)

    

class Enquiry_send(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = EnquirySerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        else:
            return Response({"message":"the enquiry form is not valid check field names or method"},status=200)
        
    def get(self,request):
        enquiry = Enquiry.objects.all()
        enquiry_list=[]
        if enquiry:
            for items in enquiry:
                product_id = items.product_id
                print("the product id is:",product_id) 
                product_list = Product_list.objects.filter(id=product_id).first()
                print('the product list:',product_list)
                enquiry_list.append({
                    "username":items.user_id,
                    "product_name":product_list.product_name,
                    "product_image":product_list.product_images if product_list.product_images else None, 
                    "product_description":product_list.product_description,
                    "message":items.message
                }
                )
            return Response(enquiry_list,status=200)
        else:
            return Response({"error": "Enquiry not found"},status=400)


class Top_products(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        orders_list = Order_products.objects.all()
        response_data = []  # Move response_data outside of the loop
        seen_products = set()

        for orders in orders_list:
            for product in orders.product_items:
                if product.get('order_status') == 'accepted':  # Use .get() to avoid KeyError
                    product_id = product.get('product_id')
                    print('The product id with status accepted:', product_id)
                    if product_id in seen_products:  # Skip if already added
                        continue
                    try:
                        product_list = Product_list.objects.get(id=product_id)
                    except Product_list.DoesNotExist:
                        continue  # Skip if product not found
                    seen_products.add(product_id)
                    
                    response_data.append({
                        'product_id': product_id,
                        'product_name':product_list.product_name,
                        'product_images':product_list.product_images if product_list.product_images else None,
                        'product_description':product_list.product_description,
                        'product_discount':product_list.product_discount if product_list.product_discount else None,
                        'product_category':product_list.product_category,
                        'prize_range':product_list.prize_range,
                        'product_stock':product_list.product_stock,
                        'order_status': product.get('order_status')
                    })
        
        return Response(response_data)
                
