from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from louslist.models import User
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test.client import Client

def search(driver: webdriver, term: str):
    search_input = driver.find_element(By.XPATH, "/html/body/nav/form/input")
    search_input.send_keys(term)
    driver.execute_script("document.querySelector('.search-button').click()")


class TestCart(StaticLiveServerTestCase):
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
        #self.driver.quit()
    
    def test_cart_add(self):
        self.driver.get(self.live_server_url)

        search(self.driver, "CS 3240")

        #Add to Cart
        self.driver.find_element(By.CSS_SELECTOR, "#add-CS-3240").click()
        self.assertIsNotNone(self.driver.find_element(By.CSS_SELECTOR, "#remove-CS-3240"))
    
    def test_schedule_builder_cart(self):
        self.driver.get(self.live_server_url)
        search(self.driver, "CS 2150")
        self.driver.find_element(By.CSS_SELECTOR, "#add-CS-2150").click()
        self.driver.get(self.live_server_url + "/schedule-builder")
        self.assertTrue("CS 2150" in self.driver.page_source)
    