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


class Register_custumer(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        custumers = Customer.objects.all()
        serializer = Register_custumerSerializer(custumers,many =True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

    def post(self, request):
        serializer = Register_custumerSerializer(data=request.data)
        print("the incoming data",request.data)
        if serializer.is_valid():
            serializer.save()
            print("the saved data is",serializer)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=500)
    
    # def post(self, request):
    #     serializer = Register_custumerSerializer(data=request.data)
    #     address = request.data.get('address')

    #     # Validate address format
    #     if address is None or not isinstance(address, list):
    #         return Response({'message': 'adress must be a list of dictionaries'}, status=status.HTTP_400_BAD_REQUEST)
        
    #     # Ensure each address is a dictionary
    #     if not all(isinstance(item, dict) for item in address):
    #         return Response({'message': 'Each address must be a dictionary'}, status=status.HTTP_400_BAD_REQUEST)

    #     if serializer.is_valid():
    #         username = serializer.validated_data.get('username')
    #         print("Username from request: ", username)

    #         # Check if username already exists
    #         if Customer.objects.filter(username=username).exists():
    #             return Response({'message': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

    #         # Save customer with address
    #         customer = serializer.save()
    #         customer.address = address  # Store address as a list of dictionaries
    #         customer.save()

    #         return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class Login_view(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        data = request.data
        if data:
            # print("the requested data",data)
            username = data.get('username')
            password = data.get('password')
            print("the requested data",username,password)

            check_items = Customer.objects.filter(username=username , password=password).first()
            if check_items:
                request.session["author"] = username
                print("the seesion data",request.session["author"])

                content = {
                    'message': 'login successfully',
                    "username": check_items.username,
                    "user_id": check_items.id
                    }
                return Response(content)
            elif Administrator.objects.filter(username=username, password=password).exists():
                admin_user = Administrator.objects.get(username=username, password=password)
                
                content = {
                    'message': 'Login successfully',
                    'username': admin_user.username,  
                    'user_id': admin_user.id    
                }
                
                return Response(content, status=200)

            else:
                content = {'message': 'user name is incorrect'}
                return Response(content)
        return Response(data.errors, status=400)

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
        customer = Customer.objects.get(id =id)
        if customer:
            serializer = Register_custumerSerializer(customer)
            return Response(serializer.data,status=200)
        else:
            return Response({"error": "Customer not found"},status=400)


    def patch(self, request, id):
            try:
                customer = Customer.objects.get(id=id)
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

            # Handle Address Update Separately (if provided)
            new_adress = request.data.get('adress')
            
            if new_adress:
                # Ensure `adress` is a list of dictionaries
                if not isinstance(new_adress, list) or not all(isinstance(item, dict) for item in new_adress):
                    return Response({'error': 'adress must be a list of dictionaries'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Merge new address data with existing address data
                existing_adress = customer.adress  # Get current address list
                
                for i, new_entry in enumerate(new_adress):
                    if i < len(existing_adress):  # Update existing addresses
                        existing_adress[i].update(new_entry)
                    else:  # Append new addresses if the index exceeds existing ones
                        existing_adress.append(new_entry)
                
                customer.adress = existing_adress  # Save updated address
                customer.save()

            # Proceed with updating other fields (if any)
            serializer = Register_custumerSerializer(customer, data=request.data, partial=True)
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
        user = request.data.get('user_id')
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
                invidual = Customer.objects.filter(username=user).first()
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
        if user_id is None or not isinstance(products, list):
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
        user = request.data.get('username')
        print("The username holder:", user)

        if user is not None:
            order_list = []
            customer = Customer.objects.filter(username=user).first()
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
                            "temp_address": products.get("temp_address"),
                            "permanent_address": customer.permanent_adress,
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
            

class Search_all(APIView):
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

        product_data = [{ 
            "id": p.id, "name": p.product_name, "category":p.product_category,"product_description":p.product_description,"product_images":p.product_images if p.product_images else None,"prize_range":p.prize_range,"product_discount":p.product_discount,
            } for p in products]
        return Response({"results": product_data}, status=200)


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

        product_data = [
            {
                "id": c.id,
                "name": c.username,
                "profile_image": request.build_absolute_uri(c.profile_image.url) if c.profile_image else None,
                "discount_individual": c.discount_individual,
                "permanent_adress":c.permanent_adress,
                "phone_number":c.phone_number,
                "status":c.status
            }
            for c in customers
        ]

        return Response({"results": product_data}, status=200)

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

