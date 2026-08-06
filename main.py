import requests
import time

URL = "https://nobat.dums.ac.ir/ShafaSchedule/doctor/1042"

while True:
    try:
        r = requests.get(URL, timeout=20)

        if "متأسفانه پزشک وقت خالی" in r.text:
            print("هنوز نوبتی وجود ندارد")

        elif "اولین نوبت خالی" in r.text:
            print("نوبت پیدا شد")

        else:
            print("وضعیت صفحه تغییر کرده است")

    except Exception as e:
        print(e)

    time.sleep(30)
