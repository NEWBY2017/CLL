from datetime import datetime, timedelta

fmt_full = "%Y-%m-%d %H:%M:%S"

def to_sec(s):
    if " " in s:
        s = s.split(" ")[1]
    s = s.split(":")
    t = int(s[0])*3600
    t += int(s[1])*60
    if len(s) == 3: t += int(s[2])
    return t

def to_hour(s):
    return to_sec(s)/3600

def to_time(hr):
    d = datetime.strptime("2000-01-01", "%Y-%m-%d")
    d += timedelta(seconds=hr*3600)
    return d.strftime("%H:%M:%S")

def dayofweek(s):
    d = datetime.strptime(s, fmt_full)
    return d.weekday()+1

def is_morning_peak(s):
    return "07:00:00" <= s <= "09:30:00"

def is_evening_peak(s):
    return "16:30:00" <= s <= "19:30:00"

def is_peak(s):
    if " " in s: s = s.split(" ")[1]
    if is_morning_peak(s) or is_evening_peak(s):
        return True
    return False


if __name__ == '__main__':
    print(to_time(10.10))

