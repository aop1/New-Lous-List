from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from selenium.webdriver.common.by import By
from django.test.utils import override_settings


class RecentSearchTest(StaticLiveServerTestCase):
    fixtures = ['users.json']

    def setUp(self):
        super().setUpClass()

        # chrome_driver = Service(
        # "C:\\Users\\kdu20\\Documents\\Java Files\\chromedriver.exe")
        # options = Options()
        # #options.add_argument("--headless")
        # self.driver = webdriver.Chrome(service=chrome_driver, options=options)
        
        
        
        options = webdriver.FirefoxOptions()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)
        


        self.client.login(username='test_user', password='password') # Native django test client
        cookie = self.client.cookies["sessionid"]
        self.driver.get(self.live_server_url + '/admin/')  # Selenium will set cookie domain based on current page domain
        self.driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.driver.refresh() # Need to update page for logged in user
        self.driver.get(self.live_server_url + '/admin/')
    
    def tearDown(self):
        super().tearDown()
        self.driver.quit()
    
    def test_dashboard_search(self):
        self.driver.get(self.live_server_url + "/dashboard")

        #Search for CS 3250
        search_input = self.driver.find_element(By.XPATH, "/html/body/nav/form/input")
        search_input.send_keys("CS 3250")
        search_button = self.driver.find_element(By.CSS_SELECTOR, "button.search-button")
        search_button.click()

        #Go to dashboard
        self.driver.get(self.live_server_url + "/dashboard")

        #Check if CS 3250 is in Recent Searches
        recent_searches = self.driver.find_element(By.CSS_SELECTOR, "#recent-body")
        self.assertIn("CS 3250", recent_searches.text)
    
    def test_create_schedule(self):
        self.driver.get(self.live_server_url + "/dashboard")
        create_schedule_btn = self.driver.find_element(By.CSS_SELECTOR, "body > div.d-flex.justify-content-center > div > div.schedules.shadow.card > div > div > button")
        create_schedule_btn.click()
        self.driver.implicitly_wait(10)
        schedule_name_input = self.driver.find_element(By.CSS_SELECTOR, "#create-schedule-modal > div > div > div.modal-body > form > input:nth-child(3)")
        schedule_name_input.send_keys("我为什么要做这是？")
        schedule_semester_dropdown = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div[2]/form/select");
        schedule_semester_dropdown.click()
        fall_semester_option = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div[2]/form/select/option[2]");
        fall_semester_option.click()
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div[2]/form/button").click()
        
        # Check if this is in the schedule builder
        self.assertIn("我为什么要做这是？", self.driver.page_source)
        
        #Check if this is in dashboard
        self.driver.get(self.live_server_url + "/dashboard")
        self.assertIn("我为什么要做这是？", self.driver.page_source)


    