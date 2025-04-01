from typing import Dict, List
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import validators
import json


def get_school_blocks(parser: BeautifulSoup) -> Dict:
    departments = {}
    department_elements = parser.select("h3.ui-accordion-header")
    department_bodies = parser.select(".ui-accordion-content")
    for i, element in enumerate(department_elements):
        name = department_elements[i].getText()
        departments[name] = department_bodies[i]
    return departments


def get_department_urls(departments: Dict, block_name: str) -> Dict:
    a_elements = departments[block_name].find_all("a")
    links = {}
    for a in a_elements:
        links[a.getText()] = a.get("href")
    return links


def get_department_codes(driver: webdriver, department_url: str):
    dep_codes = set()
    driver.get(department_url)
    parser = BeautifulSoup(driver.page_source, "html.parser")
    course_nums = parser.select("td.CourseNum")
    for course in course_nums:
        course_text = course.getText()
        space_index = course_text.find(" ")
        if course_text[1:space_index] not in dep_codes:
            dep_codes.add(course_text[1:space_index])
    return dep_codes


def create_prefix_dict(prefix: str, dep_name: str, school=str):
    prefix_dict = {
        "model": "louslist.Prefix",
        "fields": {
            "prefix": prefix,
            "dep_name": dep_name,
            "school": school}
    }
    return prefix_dict


def get_school_codes(driver: webdriver, school_blocks: dict, base_url: str):
    school_urls = {}
    prefixes = []
    for school in school_blocks.keys():
        school_urls[school] = get_department_urls(school_blocks, school)

    for school in school_urls.keys():
        if school == "Special Listings and Raw Data":
            break
        for department in school_urls[school]:
            codes = get_department_codes(
                driver, base_url + school_urls[school][department])
            if (len(codes) > 0):
                for index, code in enumerate(codes):
                    prefixes.append(create_prefix_dict(
                        prefix=code, dep_name=department, school=school))
            print(f"Finished {department}")
            if department == "Youth and Social Innovation":
                break
    for index, prefix in enumerate(prefixes):
        prefix["pk"] = index + 1
    return json.dumps(prefixes)


def main():
    url = "https://louslist.org/"
    chrome_driver = Service(
        "C:\\Users\\kdu20\\Documents\\Java Files\\chromedriver.exe")
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=chrome_driver, options=options)
    driver.get(url)
    parser = BeautifulSoup(driver.page_source, "html.parser")
    school_blocks = get_school_blocks(parser)
    json = get_school_codes(driver, school_blocks, url)
    with open("prefix.json", "w+") as file:
        file.write(json)
    print(json)


if __name__ == "__main__":
    main()
