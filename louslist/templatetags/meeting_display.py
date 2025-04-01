from django import template

register = template.Library()

def am_pm(military_time: str) -> str:
    if military_time == ":":
        return "TBD"
    elif military_time == "":
        return ""
    colon_index = military_time.find(":")
    hour = int(military_time[:colon_index])
    minutes = military_time[colon_index+1:]
    if hour == 0:
        return f"12:{minutes} AM"
    elif hour == 12:
        return f"12:{minutes} PM"
    elif hour > 12:
        return f"{hour-12}:{minutes} PM"
    return f"{hour}:{minutes} AM"

@register.simple_tag
def time_str(course_days:str, start_time:str, end_time:str) -> str:
    if start_time == ":" and end_time == ":":
        return "TBD"
    else:
        return f"{course_days} {am_pm(start_time)} - {am_pm(end_time)}"

@register.filter
def location(location: str):
    if location == "-":
        return ""
    return location
