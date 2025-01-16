from django.utils.timezone import now
from Prediction.models import Match, Team, Table
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from django.db import IntegrityError
from selenium.webdriver.chrome.options import Options
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Account.models import CustomUser
from Prediction.models import Prediction


def calculate_prediction_score(predicted_score1, predicted_score2, actual_score1, actual_score2):
    if predicted_score1 == actual_score1 and predicted_score2 == actual_score2:
        return 10  # پیش‌بینی دقیق
    elif (predicted_score1 - predicted_score2) == (actual_score1 - actual_score2):
        return 7  # اختلاف گل صحیح
    elif (
        (predicted_score1 > predicted_score2 and actual_score1 > actual_score2) or
        (predicted_score1 < predicted_score2 and actual_score1 < actual_score2) or
        (predicted_score1 == predicted_score2 and actual_score1 == actual_score2)
    ):
        return 5  # پیش‌بینی تیم برنده یا تساوی صحیح
    else:
        return 2  # هیچ‌کدام درست نیست


def get_matches():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # حالت بدون رابط کاربری
    chrome_options.add_argument('--disable-gpu')  # غیرفعال کردن GPU
    chrome_options.add_argument('--no-sandbox')  # غیرفعال کردن sandbox در محیط‌های لینوکس

    # تنظیم WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # باز کردن صفحه وب
    url = "https://football360.ir/predictions/da20f58a-2d05-4c81-a4a3-c775e9f894fa"
    driver.get(url)
    time.sleep(5)

    round_element = driver.find_element(By.CLASS_NAME, 'PredictionWeeks_active__kcrGo')

    if round_element.text.strip():
        round_value = round_element.text
    else:
        round_value = "---"

    # استخراج اسامی تیم‌ها و تاریخ‌های مسابقات
    team_elements = driver.find_elements(By.CLASS_NAME, 'PredictionMatchCard_title__FYuAe')
    teams = [element.text for element in team_elements]

    prediction_deadline_elements = driver.find_elements(By.CLASS_NAME, 'PredictionMatchCard_statusTitle__kHMEw')
    prediction_deadlines = [element.text for element in prediction_deadline_elements]

    for i in range(0, len(teams), 2):

        team1_name = teams[i]

        team2_name = teams[i + 1]
        prediction_deadline = prediction_deadlines[i // 2]
        print("**", team1_name + "-" + team2_name, "***")
        try:
            # بررسی وجود تیم‌ها در پایگاه داده
            team1 = Team.objects.get(name=team1_name)
            team2 = Team.objects.get(name=team2_name)

            # بررسی اینکه آیا مسابقه مشابهی وجود دارد
            existing_match = Match.objects.filter(
                team1=team1, team2=team2, round=round_value
            ).exists()

            if existing_match:
                continue
            else:
                # ایجاد مسابقه جدید اگر مشابهی وجود نداشته باشد
                match = Match(
                    team1=team1,
                    team2=team2,
                    date=prediction_deadline,
                    round=round_value
                )
                match.save()

        except IntegrityError as e:
            print("+++++++++++++++++++ ERor",e)

    # بستن مرورگر
    driver.quit()


def update_matches():
    logging.basicConfig(level=logging.INFO, filename="match_update.log",
                        format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("شروع به‌روزرسانی مسابقات")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    url = "https://football360.ir/league/matches"
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'style_header__k3HEZ'))
        )
    except Exception as e:
        logging.error(f"خطا در بارگذاری صفحه: {e}")
        driver.quit()
        return

    header_elements = driver.find_elements(By.CLASS_NAME, 'style_header__k3HEZ')

    round_to_element_map = {}
    for header in header_elements:
        header_text = header.text.strip()
        if "هفته" in header_text:
            round_number = header_text.split(" - ")[-1]
            round_to_element_map[round_number] = header

    active_matches = Match.objects.filter(is_active=True)

    for match in active_matches:
        match_round = match.round

        if match_round in round_to_element_map:
            try:
                match_list_element = round_to_element_map[match_round].find_element(By.XPATH, "..").find_element(
                    By.CLASS_NAME, 'style_matchList__P_pNF')
                match_items = match_list_element.find_elements(By.TAG_NAME, 'li')

                for match_item in match_items:
                    home_team_name = match_item.find_element(By.CLASS_NAME, 'style_HomeTeam__Bi3Zc').find_element(
                        By.CLASS_NAME, 'style_title__VxtR3').text.strip()
                    away_team_name = match_item.find_element(By.CLASS_NAME, 'style_AwayTeam__HPFe1').find_element(
                        By.CLASS_NAME, 'style_title__VxtR3').text.strip()

                    if (
                            (match.team1.name == home_team_name and match.team2.name == away_team_name) or
                            (match.team1.name == away_team_name and match.team2.name == home_team_name)
                    ):
                        result_text = match_item.find_element(By.CLASS_NAME, 'style_Result__M8la1').find_element(
                            By.CLASS_NAME, 'style_match__Fiqcg').text.strip()

                        if '-' in result_text:
                            home_score, away_score = map(int, result_text.split('-'))
                        else:
                            home_score, away_score = None, None

                        match.score_team1 = home_score
                        match.score_team2 = away_score
                        match.is_active = False
                        match.save()
                        logging.info(f"مسابقه {home_team_name} و {away_team_name} به‌روزرسانی شد.")
                        break
            except Exception as e:
                logging.error(f"خطا در پردازش مسابقه {match_round}: {e}")

    driver.quit()
    logging.info("به‌روزرسانی مسابقات به پایان رسید.")


def update_predictions():
    # گرفتن تمام مسابقات به‌روزرسانی‌شده
    updated_matches = Match.objects.filter(is_active=False, score_team1__isnull=False, score_team2__isnull=False)

    for match in updated_matches:
        predictions = match.predictions.all()  # تمام پیش‌بینی‌های مربوط به این مسابقه

        for prediction in predictions:
            predicted_score1 = prediction.predicted_score_team1
            predicted_score2 = prediction.predicted_score_team2
            actual_score1 = match.score_team1
            actual_score2 = match.score_team2

            # محاسبه امتیاز
            prediction.score = calculate_prediction_score(predicted_score1, predicted_score2, actual_score1,
                                                          actual_score2)
            prediction.save()


def update_user_scores():
    # گرفتن تمام پیش‌بینی‌های مسابقاتی که is_active=False هستند
    predictions = Prediction.objects.filter(match__is_active=False)

    # دیکشنری برای جمع کردن امتیاز کاربران
    user_scores = {}

    for prediction in predictions:
        user = prediction.user
        if user.id not in user_scores:
            user_scores[user.id] = 0
        user_scores[user.id] += prediction.score  # اضافه کردن امتیاز پیش‌بینی

    # به‌روزرسانی فیلد امتیاز کاربران
    for user_id, total_score in user_scores.items():
        CustomUser.objects.filter(id=user_id).update(score=total_score)


def update_table():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # حالت بدون رابط کاربری
    chrome_options.add_argument('--disable-gpu')  # غیرفعال کردن GPU
    chrome_options.add_argument('--no-sandbox')  # غیرفعال کردن sandbox در محیط‌های لینوکس

    # تنظیم WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

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

        # پیمایش ردیف‌ها و استخراج اطلاعات
        for row in rows[1:]:  # اولین ردیف شامل هدر است
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                try:
                    rank = int(cells[0].text.strip())
                    team_name = cells[1].text.strip()
                    games = int(cells[2].text.strip())
                    points = int(cells[3].text.strip())

                    # به‌روزرسانی یا ایجاد رکورد در جدول Table
                    table_record, created = Table.objects.update_or_create(
                        team=team_name,
                        defaults={
                            "rank": rank,
                            "games": games,
                            "points": points,
                        }
                    )

                except Exception as e:
                    continue

    finally:
        # بستن مرورگر
        driver.quit()


class DailyTaskMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.last_run_date = None  # ذخیره تاریخ آخرین اجرا

    def __call__(self, request):
        # بررسی زمان جاری
        current_time = now()
        if self.last_run_date is None or self.last_run_date.date() < current_time.date():
            if current_time.hour == 0:
                get_matches()
                update_matches()
                update_predictions()
                update_user_scores()
                update_table()
                self.last_run_date = current_time

        response = self.get_response(request)
        return response
