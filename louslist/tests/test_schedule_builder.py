from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from louslist.models import User
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test.client import Client
from .helpers import search
from django.test.utils import override_settings


class TestScheduleBuilder(StaticLiveServerTestCase):
    fixtures = ['users.json']

    def setUp(self):
        super().setUp()
        # chrome_driver = Service(
        # "C:\\Users\\kdu20\\Documents\\Java Files\\chromedriver.exe")
        # options = Options()
        # #options.add_argument("--headless")
        # self.driver = webdriver.Chrome(service=chrome_driver, options=options)
        
        options = webdriver.FirefoxOptions()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)

        #We need to create a login through this method
        self.client.login(username='test_user', password='password') # Native django test client
        cookie = self.client.cookies["sessionid"]
        self.driver.get(self.live_server_url + '/admin/')  # Selenium will set cookie domain based on current page domain
        self.driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.driver.refresh() # Need to update page for logged in user
        self.driver.get(self.live_server_url + '/admin/')
    
    def tearDown(self):
        super().tearDown()
        self.driver.quit()
    
    
    @override_settings(DEBUG=True)
    def test_search(self):
        self.driver.get(self.live_server_url)
        search(self.driver, "CS 2150")
        self.driver.find_element(By.CSS_SELECTOR, "#add-CS-2150").click()
        search(self.driver, "CS 3240")
        self.driver.find_element(By.CSS_SELECTOR, "#add-CS-3240").click()
        self.driver.get(self.live_server_url + "/schedule-builder")
        search_input = self.driver.find_element(By.CSS_SELECTOR, "input#search-cart-input");
        search_input.send_keys("Paul McBurney")
        first_card = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[3]/div/span/h5")
        self.assertIn("CS 3240", first_card.text)

    
    @override_settings(DEBUG=True)
    def test_add_to_schedule(self):
        self.driver.get(self.live_server_url)

        #Adding CS 2150 and CS 3240 to schedule
        search(self.driver, "CS 2150")
        self.driver.find_element(By.CSS_SELECTOR, "#add-CS-2150").click()
        search(self.driver, "CS 3240")
        self.driver.find_element(By.CSS_SELECTOR, "#add-CS-3240").click()
        self.driver.get(self.live_server_url + "/schedule-builder")

        #Create a new schedule
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[2]/div[1]/button").click()
        self.driver.implicitly_wait(10)
        schedule_name_input = self.driver.find_element(By.CSS_SELECTOR, "#create-schedule-modal > div > div > div.modal-body > form > input:nth-child(3)")
        schedule_name_input.send_keys("我喜欢星球大战")
        schedule_semester_dropdown = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[3]/div/div/div[2]/form/select");
        schedule_semester_dropdown.click()
        fall_semester_option = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[3]/div/div/div[2]/form/select/option[2]");
        fall_semester_option.click()
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[3]/div/div/div[2]/form/button").click()
        
        #Add CS 2150 to Schedule
        cs_2150_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div/span/button")
        cs_2150_btn.click()
        
        #self.driver.implicitly_wait(10)

        search_input = self.driver.find_element(By.CSS_SELECTOR, "input#search-cart-input");
        search_input.send_keys("Paul McBurney")
        cs_3240_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[3]/div/span/button")
        cs_3240_btn.click()

        calendar = self.driver.find_element(By.CSS_SELECTOR, "#calendar")     
        self.assertIn("CS 2150 - LEC", calendar.text)
        self.assertIn("CS 3240 - LEC", calendar.text)

    @override_settings(DEBUG=True)
    def test_add_to_schedule(self):
        self.driver.get(self.live_server_url)

        #Adding CS 2150 to cart
        search(self.driver, "CS 2150")
        self.driver.find_element(By.CSS_SELECTOR, "#add-CS-2150").click()
        self.driver.get(self.live_server_url + "/schedule-builder")

        #Create a new schedule
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[2]/div[1]/button").click()
        self.driver.implicitly_wait(10)
        schedule_name_input = self.driver.find_element(By.CSS_SELECTOR, "#create-schedule-modal > div > div > div.modal-body > form > input:nth-child(3)")
        schedule_name_input.send_keys("北京欢迎你")
        schedule_semester_dropdown = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[3]/div/div/div[2]/form/select");
        schedule_semester_dropdown.click()
        fall_semester_option = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[3]/div/div/div[2]/form/select/option[2]");
        fall_semester_option.click()
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[3]/div/div/div[2]/form/button").click()
        
        #Add CS 2150 to Schedule
        cs_2150_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div/span/button")
        cs_2150_btn.click()
        
        #Check if CS 2150's button is clickable
        self.assertIn("disabled", cs_2150_btn.get_attribute("class"))

    @override_settings(DEBUG=True)
    def test_add_to_schedule_conflict(self):
        self.driver.get(self.live_server_url)

        #Adding ANTH 1010 and CS 3250 to schedule
        search(self.driver, "ANTH 1010") 
        self.driver.find_element(By.CSS_SELECTOR, "#add-ANTH-1010").click()
        search(self.driver, "CS 3250")
        self.driver.find_element(By.CSS_SELECTOR, "#add-CS-3250").click()
        self.driver.get(self.live_server_url + "/schedule-builder")

        #Create a new schedule
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[2]/div[1]/button").click()
        self.driver.implicitly_wait(10)
        schedule_name_input = self.driver.find_element(By.CSS_SELECTOR, "#create-schedule-modal > div > div > div.modal-body > form > input:nth-child(3)")
        schedule_name_input.send_keys("我登过八达岭长城")
        schedule_semester_dropdown = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[3]/div/div/div[2]/form/select");
        schedule_semester_dropdown.click()
        fall_semester_option = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[3]/div/div/div[2]/form/select/option[2]");
        fall_semester_option.click()
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[3]/div/div/div[2]/form/button").click()
        
        #Add ANTH 1010 to Schedule
        anth1010_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div/span/button")
        anth1010_btn.click()
        

        search_input = self.driver.find_element(By.CSS_SELECTOR, "input#search-cart-input");
        search_input.send_keys("CS 3250")
        cs3250_btn = self.driver.find_element(By.XPATH, "//html/body/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[3]/div/span/button")
        cs3250_btn.click()

        calendar = self.driver.find_element(By.CSS_SELECTOR, "#calendar")     
        self.assertIn("ANTH 1010 - LEC", calendar.text)
        self.assertNotIn("CS 3250 - LEC", calendar.text)
    
    def test_delete_schedule(self):
        self.driver.get(self.live_server_url + "/schedule-builder")
        #Create a new schedule
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[2]/div[1]/button").click()
        self.driver.implicitly_wait(10)
        schedule_name_input = self.driver.find_element(By.CSS_SELECTOR, "#create-schedule-modal > div > div > div.modal-body > form > input:nth-child(3)")
        schedule_name_input.send_keys("我吃过北京烤鸭")
        schedule_semester_dropdown = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[3]/div/div/div[2]/form/select");
        schedule_semester_dropdown.click()
        fall_semester_option = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[3]/div/div/div[2]/form/select/option[2]");
        fall_semester_option.click()
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[3]/div/div/div[2]/form/button").click()

        #Delete schedule
        self.driver.find_element(By.CSS_SELECTOR, "button[data-bs-target='#delete-schedule-modal']").click()
        self.driver.implicitly_wait(10)
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div[5]/div/div/div[2]/div/form/button").click()
        self.assertNotIn("我吃过北京烤鸭", self.driver.page_source)