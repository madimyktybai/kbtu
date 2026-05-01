from datetime import *

# #1
# current = datetime.now()
# result = current - timedelta(days=5)
# print(result)


# #2
# today = date.today()
# yesterday = today - timedelta(days=1)
# tomorrow = today + timedelta(days=1)

# print(f"Вчера:   {yesterday}")
# print(f"Сегодня: {today}")
# print(f"Завтра:  {tomorrow}")


# #3
# now = datetime.now()
# no_micros = now.replace(microsecond=0)
# print(no_micros)


#4
date1 = datetime(2024, 1, 1, 0, 0, 0)
date2 = datetime.now()


difference = date2 - date1
seconds_diff = difference.total_seconds()

print(seconds_diff)