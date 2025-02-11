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


class Register_custumer(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        custumers = Customer.objects.all()
        serializer = Register_custumerSerializer(custumers,many =True)
        return Response(serializer.data,status.status.HTTP_200_Ok)
    
    def post(self,request):
        serializer = Register_custumerSerializer(data = request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            print("username from request: ",username)
            check = Customer.objects.filter(username=username)
            if check:
                content = {'message': 'username already taken'}
                return Response(content)
            else:
                serializer.save()
                return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
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
            else:
                content = {'message': 'cant login now'}
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
        return Response({"error": "Product deleted"}, status=400)





class ProductListPost(APIView):
    permission_classes = [AllowAny]
    
    def get(self,request):
        product = Product_list.objects.all()
        serializer = ProductListSerializer(product, many = True)
        return Response(serializer.data)
    

    def post(self, request):
        product_data = request.data  # Expecting a single dictionary

        if not isinstance(product_data, dict):
            return Response({"error": "Invalid format. Expected a dictionary."}, status=status.HTTP_400_BAD_REQUEST)

        try:    
            # Extract product details
            prize_list = product_data.get('prize_range', [])
            image_list = product_data.get('product_images', [])

            # Validate prize_list
            if not isinstance(prize_list, list) or any(not isinstance(prize, dict) for prize in prize_list):
                return Response({"error": "prize_range must be a list of dictionaries."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate image_list
            if not isinstance(image_list, list) or any(not isinstance(img, str) for img in image_list):
                return Response({"error": "product_images must be a list of strings (URLs or file paths)."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Create product instance
            product = Product_list.objects.create(
                product_name=product_data.get('product_name', 'Default Name'),
                product_images=[],  # Start empty
                product_description=product_data.get('product_description', 'Default Description'),
                product_discount=product_data.get('product_discount', '0%'),
                product_offer=product_data.get('product_offer', 'No Offer'),
                product_category=product_data.get('product_category', 'Miscellaneous'),
                prize_range=[],  # Start empty
                product_stock=product_data.get('product_stock', '0')
            )

            # Store up to 3 prize ranges
            for prize in prize_list[:3]:  
                product.add_prize_range(prize)

            # Store up to 5 images
            for image in image_list[:5]:  
                product.add_image(image)

            serializer = ProductListSerializer(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# class ProduclistView(APIView):
#     permission_classes = [AllowAny]

#     def get(self,request):
#         if "author" in request.session:
#             user = request.session.get('author')
#             print('author name is:',user)
#             username = Customer.objects.get(username=user)
#             print('username name is:',username)
#             response_data = []
#             try:
#                 individual_discount = int(username.discount_individual)
#                 print('individual_discount  is:',individual_discount)
#             except ValueError:
#                  individual_discount = 0
#             products = Product_list.objects.all()
#             for product in products:
#                 product_prize = product.prize_range
#                 print("product_prize is",product_prize)
#                 discounted_prices = []
#                 for prize in product_prize:
#                     if 'price' in prize:
#                         try:
#                             actual_prize = int(prize['price'])
#                             print("actual_prize is",actual_prize)

#                             final_discount = actual_prize - (actual_prize * individual_discount / 100)
#                             print("Final Price after Discount:", final_discount)

#                             discounted_prices.append({
#                                     "actual_price": actual_prize,
#                                     "final_discount": final_discount
#                                 })
#                             print("the output array is",discounted_prices)
                            
#                         except ValueError:
#                             continue 
                        
#                 serializer = ProductListSerializer(product)
#                 product_data = serializer.data
#                 product_data['discounted_prices'] = discounted_prices  

#                 response_data.append(product_data)

#         return Response(response_data, status=status.HTTP_200_OK)


 
class Product_updateanddelete(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, id):
        try:
            item = Product_list.objects.get(id=id)
        except Product_list.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        data = request.data.copy()  # Copy request data

        # Handle updating a specific index in prize_range
        index = data.pop("index", None)  # Get index if provided
        new_value = data.pop("new_value", None)  # Get new value if provided


        if index is not None and new_value is not None:
            if not isinstance(item.prize_range, list):
                return Response({"error": "prize_range is not a list"}, status=400)

            if index < 0 or index >= len(item.prize_range):
                return Response({"error": "Index out of range"}, status=400)

            # Update specific index in prize_range
            item.prize_range[index] = new_value
            data["prize_range"] = item.prize_range  # Ensure this field gets updated
        
        item_no = data.pop("item_no", None)  # Get index if provided
        new_image = data.pop("new_image", None)  # Get new value if provided

        if item_no is not None and new_image is not None:
            if not isinstance(item.product_images, list):
                return Response({"error": "product_images is not a list"}, status=400)

            if item_no < 0 or item_no >= len(item.product_images):
                return Response({"error": "item_no out of range"}, status=400)
            
                # Update specific index in prize_range
            item.product_images[item_no] = new_image
            data["product_images"] = item.product_images  # Ensure this field gets updated


        # Serialize with partial=True to update only provided fields
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

    def get(self,request,id=None):
        customer = Customer.objects.all()
        serializer = Register_custumerSerializer(customer,many=True)
        return Response(serializer.data)

    def patch(self, request, id):
        try:
            customer = Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)

        serializer = Register_custumerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

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
        if "author" in request.session:
            user = request.session['author']
            print("The available user is:", user)

            user_id = request.data.get('user_id')
            products = request.data.get('products')

            print("Received user_id:", user_id)
            print("Received products:", products)

            # Validate data
            if user_id is None or not isinstance(products, list):
                return Response({"error": "Invalid data format (user_id missing or products is not a list)"}, status=400)

            # Check if cart already exists for the user
            cart = Cart_items.objects.filter(user_id=user_id).first()

            if cart:
                # Update existing cart
                cart.cart_add(products)
                serializer = CartSerializer(cart)
            else:
                # Create new cart entry
                cart = Cart_items.objects.create(user_id=user_id, products=products)
                serializer = CartSerializer(cart)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response({"error": "No session found"}, status=400)
                

    def get(self, request):
        if "author" in request.session:

            a="40"
            print(type(a))

            user = request.session['author']
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
                                discount_to_apply = individual_discount if individual_discount else product_discount
                                discounted_price = price * (1 - discount_to_apply)
                                total_amount = product_count * discounted_price
                                print("Total Amount for Product:", total_amount)
                                break  

                    # Append product details to cart_data
                    if product_obj:
                        cart_data.append({
                            "user_id": item.user_id,
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
                    print("the sum_total",sum_total)

            if not cart_data:
                return Response({"error": "No products found in cart"}, status=404)

            return Response(cart_data)  

        return Response({"error": "No session found"}, status=403)


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
            if "author" in request.session:
                user = request.session["author"]
                print("The session holder:", user)

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
                                    "temp_address": products.get("total_amount"),
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

            else:
                return Response({"error": "No Session found"})

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



# class Cancel_order(APIView):
#     def delete(self,request):

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
                product_list = Product_list.objects.filter(id=product_id).first()
                if not product_list:
                    print(f"Skipping product with ID {product_id} (Not Found)")
                    continue  
                order_products.append(
                    {
                        'user_id':user_id,
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
            







# {"product_id": 24,
#   "total_count": 20,
#     "product_name": "mobile", "product_images": ["media/shoes1.jpg", "https://example.com/images/laptop3.jpg", "https://example.com/images/laptop3785.jpg", "https://example.com/images/laptop378787.jpg", "https://example.com/images/laptop3757858752.jpg"],
#       "product_description": "sangu's product",
#         "product_discount": "10",
#           "individual_discount": 0.0, 
#           "product_offer": "20",
#             "product_category": "Electronics", "product_stock": "100", 
#             "order_id": 3,
#             "total_amount": 6300.0,
#               "order_status": "Rejected"}