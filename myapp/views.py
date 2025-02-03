from django.contrib.auth.hashers import check_password
# from django.contrib.auth.models import User
from .models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import DatabaseCredential
from .serializers import DatabaseCredentialSerializer, LoginSerializer, UserSignupSerializer
from .permissions import IsAuthenticatedAndAdmin
import mysql.connector

from celery import shared_task

@shared_task(bind=True)
def logger(text):
    print("-----------------------")
    print(f"am at {text}")

class PingView(APIView):
    def get(self, request):
        return Response({"message": "Hey your services are running: pong pong"}, status=status.HTTP_200_OK)

class SignupView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated users to sign up

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "User registered successfully",
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class LoginView(APIView):
#     permission_classes = [AllowAny]  # Allow anyone to attempt login

#     def post(self, request):
#         username = request.data.get("username")
#         password = request.data.get("password")
        
#         if not username or not password:
#             return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             user = User.objects.get(username=username)
#             if check_password(password, user.password):  # Validate hashed password
#                 refresh = RefreshToken.for_user(user)
#                 return Response({
#                     "message": "Login successful",
#                     "access": str(refresh.access_token),
#                     "refresh": str(refresh)
#                 }, status=status.HTTP_200_OK)
#             else:
#                 return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
#         except User.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
class LoginView(APIView):
    def post(self, request):
        # logger.delay("just started login")
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            try:
                # logger.delay("at line 73 getting username to check")
                user = User.objects.get(username=username)
                if check_password(password, user.password):  # Validate hashed password
                    # logger.delay("you are there")
                    refresh = RefreshToken.for_user(user)
                    # logger.delay("we are almost good to generated the data")
                    return Response({
                        "message": "Login successful",
                        "access": str(refresh.access_token),
                        "refresh": str(refresh)
                    }, status=status.HTTP_200_OK)
                else:
                    
                    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConnectView(APIView):
    # permission_classes = [IsAuthenticatedAndAdmin]

    def post(self, request):
        serializer = DatabaseCredentialSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                if data['db_type'] == 'mysql':
                    conn = mysql.connector.connect(
                        user=data['username'], password=data['password'],
                        host=data['host'], port=data['port'], database=data['db_name'], charset='utf8mb4'
                    )
                    conn.close()
                    serializer.save()
                    return Response({"message": "Connection to MySQL established successfully", "credentials_saved": True}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Only MySQL is supported at the moment."}, status=status.HTTP_400_BAD_REQUEST)
            except mysql.connector.Error as e:
                return Response({"message": f"Failed to connect to the database: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FetchDataView(APIView):
    # permission_classes = [IsAuthenticatedAndAdmin]

    def post(self, request):
        db_name = request.data.get("db_name")
        query = request.data.get("query")

        try:
            db_record = DatabaseCredential.objects.get(db_name=db_name)
            conn = mysql.connector.connect(
                user=db_record.username, password=db_record.password,
                host=db_record.host, port=db_record.port, database=db_record.db_name, charset='utf8mb4'
            )
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return Response({"data": result}, status=status.HTTP_200_OK)
        except DatabaseCredential.DoesNotExist:
            return Response({"message": f"Database {db_name} not found in records."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"Error fetching data: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
