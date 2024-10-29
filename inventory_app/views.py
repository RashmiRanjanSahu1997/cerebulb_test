from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Sum, F
from .models import Product, Category, Supplier, StockLog
from .serializers import ProductSerializer, StockLogSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.core.exceptions import ObjectDoesNotExist, ValidationError

class SignupAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username is already taken."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            "message": "User created successfully.",
            "token": token.key
        }, status=status.HTTP_201_CREATED)


# User Login View
class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key,"msg": "Loggedin Successfully."}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
# Product List and Create View (from the previous code)
class ProductListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            products = Product.objects.all()
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            # General error handling for unexpected errors
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Not authorized to add products."}, status=status.HTTP_403_FORBIDDEN)

        try:
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            # Handles validation errors
            return Response({"error": "Validation error", "details": e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            # Handles cases where a related object (like a foreign key) does not exist
            return Response({"error": "Related object does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # General error handling for unexpected errors
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            product = self.get_object(pk)
            if product is None:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        if not request.user.is_staff:
            return Response({"detail": "Not authorized to add products.Only Admins can Change"}, status=status.HTTP_403_FORBIDDEN)
        try:
            product = self.get_object(pk)
            if product is None:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": "Validation error", "details": e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({"detail": "Not authorized to remove products."}, status=status.HTTP_403_FORBIDDEN)
        try:
            product = self.get_object(pk)
            if product is None:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
            product.delete()
            return Response({"detail": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# Manage Stock (Add/Remove Stock) View
class ManageStockAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, product_id):
        """
        Adjust stock for a product by adding or removing quantity based on action.
        """
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        quantity = request.data.get("quantity")
        action = request.data.get("action")
        reason = request.data.get("reason", "No reason provided")

        # Validate input
        if quantity is None or quantity <= 0:
            return Response({"error": "A positive quantity is required."}, status=status.HTTP_400_BAD_REQUEST)
        if action not in dict(StockLog.ACTION_CHOICES):
            return Response({"error": "Invalid action. Must be 'add' or 'remove'."}, status=status.HTTP_400_BAD_REQUEST)

        # Adjust stock based on action
        if action == 'add':
            product.quantity += quantity
        elif action == 'remove':
            if product.quantity < quantity:
                return Response({"error": "Not enough stock to remove the specified quantity."}, status=status.HTTP_400_BAD_REQUEST)
            product.quantity -= quantity

        product.save()

        # Create stock log entry
        stock_log = StockLog.objects.create(
            product=product,
            quantity=quantity,
            action=action,
            reason=reason
        )

        # Serialize response data
        product_serializer = ProductSerializer(product)

        return Response({
            "product": product_serializer.data,
            "stock_log": {
                "product": stock_log.product.id,
                "quantity": stock_log.quantity,
                "action": stock_log.get_action_display(),
                "date": stock_log.date,
                "reason": stock_log.reason
            }
        }, status=status.HTTP_200_OK)
# View Stock Alerts for Low Quantity
class StockAlertAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        threshold = 5  # Set the low stock threshold here
        low_stock_products = Product.objects.filter(quantity__lt=threshold)
        serializer = ProductSerializer(low_stock_products, many=True)
        return Response(serializer.data)

# Reporting View for Inventory Summary
class InventoryReportAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """
        Returns reporting data:
            - Total inventory value
            - Sorted list of products by stock level
            - Filtered products by category, supplier, or stock level
        """
        # Calculate total inventory value (quantity * price for each product)
        total_inventory_value = Product.objects.aggregate(
            total_value=Sum(F('quantity') * F('price'))
        )['total_value'] or 0

        # Sorting parameter (ascending by default)
        sort_order = request.GET.get('sort', 'asc')
        sort_field = 'quantity' if sort_order == 'asc' else '-quantity'

        # Apply filters
        category = request.GET.get('category')
        supplier = request.GET.get('supplier')
        stock_level = request.GET.get('stock_level')

        products = Product.objects.all()

        # Filter by category if provided
        if category:
            products = products.filter(category__id=category)

        # Filter by supplier if provided
        if supplier:
            products = products.filter(supplier__id=supplier)

        # Filter by stock level (e.g., low stock if specified)
        if stock_level == 'low':
            products = products.filter(quantity__lt=5)

        # Order products by stock level
        products = products.order_by(sort_field)

        # Serialize products data
        serialized_products = ProductSerializer(products, many=True).data

        return Response({
            "total_inventory_value": total_inventory_value,
            "products": serialized_products,
            "sort_order": sort_order
        })