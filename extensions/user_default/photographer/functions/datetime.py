
import datetime

def get_date_and_time():
    now = datetime.datetime.now()
    current_time = now.strftime("%H%M%S")
    current_date = str(datetime.date.today())[2:]

    return current_time,current_date