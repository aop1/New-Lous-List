from django.forms import model_to_dict
from django.test import TestCase
from louslist.models import User
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test.client import Client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class Settings(TestCase):
    fixtures = ['users.json']

    def setUp(self) -> None:
        self.client.login(username='test_user', password='password')
        return super().setUp()

    def test_change_all_settings(self):
        resp = self.client.post('/api/update-account/', {'username': 'new_username',
        'first_name': 'new_name', 'last_name': 'new_surname', 'major': 'New Major',
        'grad_year': 1999, 'profile_pic': 'new_path'}, content_type='application/json')
        self.assertTrue(
            User.objects.filter(username='new_username', first_name='new_name',
            last_name='new_surname', major='New Major', grad_year=1999,
            profile_pic='new_path').exists()
        )
        resp = self.client.get('/')
        self.assertEquals(resp.context['user'].username, 'new_username')
        self.assertEquals(resp.context['user'].first_name, 'new_name')
        self.assertEquals(resp.context['user'].last_name, 'new_surname')
        self.assertEquals(resp.context['user'].major, 'New Major')
        self.assertEquals(resp.context['user'].grad_year, 1999)
        self.assertEquals(resp.context['user'].profile_pic, 'new_path')

    def test_change_username_only(self):
        resp = self.client.post('/api/update-account/', {'username': 'new_username'},
        content_type='application/json')
        self.assertTrue(
            User.objects.filter(username='new_username', first_name='Test',
            last_name='User', major='Computer Science', grad_year= 2020,
            profile_pic='yhRgWb.md.png').exists()
        )
        resp = self.client.get('/')
        self.assertEquals(resp.context['user'].username, 'new_username')
        self.assertEquals(resp.context['user'].first_name, 'Test')
        self.assertEquals(resp.context['user'].last_name, 'User')
        self.assertEquals(resp.context['user'].major, 'Computer Science')
        self.assertEquals(resp.context['user'].grad_year, 2020)
        self.assertEquals(resp.context['user'].profile_pic, 'yhRgWb.md.png')

    def test_change_nothing(self):
        resp = self.client.post('/api/update-account/', {},
        content_type='application/json')
        self.assertTrue(
            User.objects.filter(username='test_user', first_name='Test',
            last_name='User', major='Computer Science', grad_year= 2020,
            profile_pic='yhRgWb.md.png').exists()
        )
        resp = self.client.get('/')
        self.assertEquals(resp.context['user'].username, 'test_user')
        self.assertEquals(resp.context['user'].first_name, 'Test')
        self.assertEquals(resp.context['user'].last_name, 'User')
        self.assertEquals(resp.context['user'].major, 'Computer Science')
        self.assertEquals(resp.context['user'].profile_pic, 'yhRgWb.md.png')
    
    def test_account_display(self):
        self.client.post('/api/update-account/', {'username': 'new_username',
        'first_name': 'new_name', 'last_name': 'new_surname', 'major': 'New Major',
        'grad_year': 1999, 'profile_pic': 'new_path'},
        content_type='application/json')
        resp = self.client.get("/account-settings/")
        self.assertEquals(resp.context['user'].username, "new_username")
        self.assertEquals(resp.context['user'].first_name, "new_name")
        self.assertEquals(resp.context['user'].last_name, "new_surname")
        self.assertEquals(resp.context['user'].major, 'New Major')
        self.assertEquals(resp.context['user'].profile_pic, 'new_path')
        
    

class TestSettingsSelenium(StaticLiveServerTestCase):
    fixtures = ['users.json']

    def setUp(self):
        super().setUp()
        
        # chrome_driver = Service(
        # "C:\\Users\\kdu20\\Documents\\Java Files\\chromedriver.exe")
        # options = Options()
        # #options.add_argument("--headless")
        # self.driver = webdriver.Chrome(service=chrome_driver, options=options)
        
        # options = webdriver.FirefoxOptions()
        # options.headless = True
        # self.driver = webdriver.Firefox(options=options)
        # self.driver.implicitly_wait(10)

        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(chrome_options=options)
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
    
    def test_default_image(self):
        self.driver.get(self.live_server_url + "/account-settings")
        profile_img = self.driver.find_element(By.CSS_SELECTOR, "#profile-image")
        self.assertIn("yhRgWb.md.png", profile_img.get_attribute("src"))
    
    def test_choose_image(self):
        self.driver.get(self.live_server_url + "/account-settings")
        edit_img_button = self.driver.find_element(By.CSS_SELECTOR, "body > div.d-flex.justify-content-center > div > div > div.profile-image.mb-3 > button")
        edit_img_button.click()
        self.driver.implicitly_wait(10)
        new_img = self.driver.find_element(By.CSS_SELECTOR, "#select-profile-img > div > div > div.modal-body > button:nth-child(1)")
        new_img.click()
        img_input = self.driver.find_element(By.CSS_SELECTOR, "input[name=profile_pic]")
        self.assertIn(".png", img_input.get_attribute("value"))
    
    def test_update_name(self):
        self.driver.get(self.live_server_url + "/account-settings")
        edit_img_button = self.driver.find_element(By.CSS_SELECTOR, "body > div.d-flex.justify-content-center > div > div > div.profile-image.mb-3 > button")
        edit_img_button.click()
        self.driver.implicitly_wait(10)
        profile_img = self.driver.find_element(By.XPATH, "//*[@id='select-profile-img']/div/div/div[2]/button[1]/img")
        profile_img.click()
        self.driver.execute_script("document.querySelector('body > div.modal-backdrop.fade').click()")
        first_name_field = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/form/div/input[1]")
        first_name_field.clear()
        first_name_field.send_keys("Ebenezer")
        last_name_field = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/form/div/input[2]")
        last_name_field.clear()
        last_name_field.send_keys("Scrooge")
        self.driver.execute_script("document.querySelector('#account-form > button').click()")
        self.driver.refresh()
        self.assertIn("Ebenezer", self.driver.page_source)
        self.assertIn("Scrooge", self.driver.page_source)

    def test_update_major(self):
        self.driver.get(self.live_server_url + "/account-settings")
        edit_img_button = self.driver.find_element(By.CSS_SELECTOR, "body > div.d-flex.justify-content-center > div > div > div.profile-image.mb-3 > button")
        edit_img_button.click()
        self.driver.implicitly_wait(10)
        profile_img = self.driver.find_element(By.XPATH, "//*[@id='select-profile-img']/div/div/div[2]/button[1]/img")
        profile_img.click()
        self.driver.execute_script("document.querySelector('body > div.modal-backdrop.fade').click()")
        major_field = self.driver.find_element(By.CSS_SELECTOR, "input[name=major]")
        major_field.clear()
        major_field.send_keys("Civil Engineering")
        self.driver.execute_script("document.querySelector('#account-form > button').click()")
        self.driver.refresh()
        self.driver.implicitly_wait(10)
        self.assertIn("Civil Engineering", self.driver.page_source)
    
    def test_empty(self):
        self.driver.get(self.live_server_url + "/account-settings")
        first_name_field = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/form/div/input[1]")
        first_name_field.clear()
        last_name_field = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/form/div/input[2]")
        last_name_field.clear()
        major_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='major']")
        major_field.clear()
        self.driver.execute_script("document.querySelector('#account-form > button').click()")
        self.driver.refresh()
        self.assertIn("Test", self.driver.page_source)
        self.assertIn("User", self.driver.page_source)
        self.assertIn("Computer Science", self.driver.page_source)
    
    
    
    


        
    
    
    
