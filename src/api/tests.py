import datetime

s = "2022-07-25"
target_date = datetime.datetime.strptime(s, '%Y-%m-%d').date()

print(target_date)
print(target_date < datetime.date.today())
