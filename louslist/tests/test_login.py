from django.test import TestCase
from django.test import Client
from django.test.client import RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.helpers import complete_social_login
from allauth.account.models import EmailAddress
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.test.utils import override_settings
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class Login(TestCase):
    
    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP = True)
    def test_auto_signup_login_and_logout(self):
        factory = RequestFactory()
        request = factory.get("/accounts/login/callback/")
        request.user = AnonymousUser()
        SessionMiddleware(lambda request: None).process_request(request)
        MessageMiddleware(lambda request: None).process_request(request)

        User = get_user_model()
        user = User(username="test_user", email="verified@example.com")
        sociallogin = SocialLogin(
            user=user,
            account=SocialAccount(provider="google"),
            email_addresses=[
                EmailAddress(email="verified@example.com", verified=True, primary=True)
            ],
        )
        complete_social_login(request, sociallogin)
        self.assertTrue(User.objects.filter(username="test_user").exists())
        self.assertTrue(SocialAccount.objects.filter(user=user).exists())
        created_user = User.objects.get(username="test_user")
        created_user.is_superuser = True
        created_user.is_staff = True
        created_user.set_password('secret')
        created_user.save()
        resp = self.client.post('/admin/login/', {'username': 'test_user',
        'password': 'secret'})
        self.assertRedirects(resp, '/dashboard')
        resp = self.client.get('/')
        self.assertEquals(resp.context['user'], user)
        resp = self.client.post(reverse('account_logout'))
        self.assertRedirects(resp, '/')
        resp = self.client.get('/')
        self.assertNotEquals(resp.context['user'], user)

    def test_signup_and_logout(self):
        session = self.client.session
        User = get_user_model()
        user = User(username="other", email="other@example.com")
        sociallogin = SocialLogin(
            user=user,
            account=SocialAccount(provider="google"),
            email_addresses=[
                EmailAddress(email="verified@example.com", verified=True, primary=True)
            ],
        )
        session["socialaccount_sociallogin"] = sociallogin.serialize()
        session.save()
        resp = self.client.get(reverse('home'))
        resp = self.client.post(
            reverse("socialaccount_signup"),
            data={"username": "test_user", "email": "verified@example.com",
            "first_name": "Test", "last_name": "User"},
        )
        self.assertRedirects(resp, "/dashboard")
        self.assertTrue(
            User.objects.filter(username="test_user", email="verified@example.com", 
            first_name="Test", last_name="User").exists()
        )
        self.assertTrue(
            SocialAccount.objects.filter(user=User.objects.get(username="test_user")).exists()
        )
        self.assertEqual(1, len(EmailAddress.objects.filter(email="verified@example.com")))
        self.assertEqual(1, len(EmailAddress.objects.all()))
        resp = self.client.get(reverse('home'))
        self.assertEquals(resp.context['user'].username, "test_user")
        self.assertEquals(resp.context['user'].email, "verified@example.com")
        self.assertEquals(resp.context['user'].first_name, "Test")
        self.assertEquals(resp.context['user'].last_name, "User")
        # Logout like the logout button
        resp = self.client.post(reverse("account_logout"))
        # Additional ways to logout
        # self.client.post("/accounts/logout/")
        # self.client.logout()
        self.assertRedirects(resp, '/')
        resp = self.client.get('/')
        self.assertNotEquals(resp.context['user'].username, "test_user")

    def test_signup_different_email_and_logout(self):
        session = self.client.session
        User = get_user_model()
        user = User(username="other", email="other@example.com")
        sociallogin = SocialLogin(
            user=user,
            account=SocialAccount(provider="google"),
            email_addresses=[
                EmailAddress(email="verified@example.com", verified=True, primary=True)
            ],
        )
        session["socialaccount_sociallogin"] = sociallogin.serialize()
        session.save()
        resp = self.client.get(reverse('home'))
        resp = self.client.post(
            reverse("socialaccount_signup"),
            data={"username": "test_user", "email": "test@example.com",
            "first_name": "Test", "last_name": "User"},
        )
        self.assertRedirects(resp, "/dashboard")
        self.assertTrue(
            User.objects.filter(username="test_user", email="verified@example.com", 
            first_name="Test", last_name="User").exists()
        )
        self.assertTrue(
            SocialAccount.objects.filter(user=User.objects.get(username="test_user")).exists()
        )
        resp = self.client.get(reverse('home'))
        self.assertEquals(resp.context['user'].username, "test_user")
        self.assertEquals(resp.context['user'].email, "verified@example.com")
        self.assertEquals(resp.context['user'].first_name, "Test")
        self.assertEquals(resp.context['user'].last_name, "User")
        self.assertFalse(
            EmailAddress.objects.filter(email="test@example.com").exists()
        )
        resp = self.client.post(reverse("account_logout"))
        self.assertRedirects(resp, '/')
        resp = self.client.get('/')
        self.assertNotEquals(resp.context['user'].username, "test_user")

class SeleniumLogin(StaticLiveServerTestCase):
    fixtures = ['users.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # chrome_driver = Service(
        # "C:\\Users\\kdu20\\Documents\\Java Files\\chromedriver.exe")
        # options = Options()
        # #options.add_argument("--headless")
        # cls.selenium = webdriver.Chrome(service=chrome_driver, options=options)

        options = webdriver.FirefoxOptions()
        options.headless = True
        cls.selenium = webdriver.Firefox(options=options)
        cls.selenium.implicitly_wait(10)
    
    def setUp(self):
        client = Client()
        client.login(username='test_user', password='password') # Native django test client
        cookie = client.cookies['sessionid']
        self.selenium.get(self.live_server_url + '/admin/')  # Selenium will set cookie domain based on current page domain
        self.selenium.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.selenium.refresh() # Need to update page for logged in user
        self.selenium.get(self.live_server_url + '/admin/')

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_logout_and_google_redirect(self):
        self.selenium.get(self.live_server_url)
        self.assertIn("test_user", self.selenium.page_source)
        
        #Open Menu
        menu_button = self.selenium.find_element(By.XPATH, "/html/body/nav/div[1]/button")
        menu_button.click()

        self.selenium.find_element(By.XPATH, '//*[@id="menu-offcanvas"]/div[2]/form/button').click()
    

        self.selenium.get('%s%s' % (self.live_server_url, ''))
        self.selenium.find_element(By.XPATH, '/html/body/nav/div[2]/form/button').click()
        # Google realizes it's a bot, so first assertion fails
        # self.assertIn("https://accounts.google.com/o/oauth2/auth?client_id=1097306355332-ug9sdbp013sdsoptti4ogu7bds143s1l.apps.googleusercontent.com", self.selenium.current_url)
        self.assertIn("https://accounts.google.com/", self.selenium.current_url)
    

def search(driver: webdriver, term: str):
    search_input = driver.find_element(By.XPATH, "/html/body/nav/form/input")
    search_input.send_keys(term)
    search_button = driver.find_element(By.XPATH, "/html/body/nav/form/button")
    search_button.click()