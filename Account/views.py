from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterSerializer, LoginSerializer, UpdateProfileSerializer, TopUsersSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from .models import CustomUser
# from CIS_control.models import CisControl


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "ثبت ‌نام با موفقیت انجام شد."},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileView(APIView):
    permission_classes = []

    def put(self, request, *args, **kwargs):
        user_id = request.data.get('id')
        if not user_id:
            return Response({"error": "شناسه کاربری الزامی است."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "کاربری با این شناسه یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateProfileSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "پروفایل با موفقیت به‌روزرسانی شد.",
                             "data": serializer.data},
                            status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # حذف توکن کاربر
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({"message": "با موفقیت خارج شدید."}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"error": "توکن پیدا نشد."}, status=status.HTTP_400_BAD_REQUEST)


class TopUsersView(APIView):

    def get(self, request):
        top_users = CustomUser.objects.order_by('-score')[:10]  # مرتب‌سازی نزولی و انتخاب 10 نفر برتر
        serializer = TopUsersSerializer(top_users, many=True)
        return Response(serializer.data)


