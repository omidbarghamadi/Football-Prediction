from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Team, Match, Prediction
from .serializers import TeamSerializer, MatchSerializer, PredictionSerializer
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from .middleware import update_user_scores, update_predictions, update_matches


class TeamListView(APIView):
    permission_classes = []

    def get(self, request):
        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)


class MatchListView(APIView):
    permission_classes = []

    def get(self, request):
        matches = Match.objects.filter(is_active=True)
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)


class PredictionViewSet(viewsets.ModelViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        is_active = self.request.query_params.get('is_active')

        if is_active:
            return Prediction.objects.filter(user=self.request.user, match__is_active=is_active)

        return Prediction.objects.filter(user=self.request.user)


class TableView(APIView):
    permission_classes = []

    def get(self, request):
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # حالت بدون رابط کاربری
        chrome_options.add_argument('--disable-gpu')  # غیرفعال کردن GPU
        chrome_options.add_argument('--no-sandbox')  # غیرفعال کردن sandbox در محیط‌های لینوکس

        # تنظیم WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            # باز کردن صفحه وب
            url = "https://www.varzesh3.com/"  # آدرس صفحه‌ای که جدول در آن قرار دارد
            driver.get(url)

            # انتظار برای بارگذاری محتوا
            time.sleep(2)

            # پیدا کردن جدول بر اساس کلاس آن
            table = driver.find_element(By.CLASS_NAME, "league-standing")

            # استخراج داده‌های جدول
            rows = table.find_elements(By.TAG_NAME, "tr")
            data = []

            # پیمایش ردیف‌ها و استخراج اطلاعات
            for row in rows[1:]:  # اولین ردیف شامل هدر است
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells:
                    rank = cells[0].text
                    team = cells[1].text
                    games = cells[2].text
                    points = cells[3].text
                    data.append({"رتبه": rank, "تیم": team, "بازی": games, "امتیاز": points})

        finally:
            # بستن مرورگر
            driver.quit()

        # برگرداندن داده‌ها در قالب JSON
        return Response(data)


class UpdateView(APIView):
    permission_classes = []

    def get(self, request):
        update_matches()
        update_predictions()
        update_user_scores()
        return Response("ok")
