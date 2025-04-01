from django.test import TestCase, override_settings
from louslist.models import Schedule, Comment
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test.client import Client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class SearchUsers(TestCase):
    fixtures = ['users.json']

    def setUp(self) -> None:
        self.client.login(username='test_user', password='password')
        return super().setUp()

    def test_search_user_by_username(self):
        resp = self.client.get('/social/?q=Admin')
        usernames = [x['username'] for x in resp.context['users']]
        self.assertIn('admin', usernames)
        resp = self.client.get('/social/?q=uSEr')
        usernames = [x['username'] for x in resp.context['users']]
        self.assertNotIn('test_user', usernames)
        self.assertIn('test2_user', usernames)
        self.assertIn('test3_user', usernames)

    def test_search_user_by_lastname(self):
        resp = self.client.get('/social/?q=lastnAme')
        usernames = [x['username'] for x in resp.context['users']]
        self.assertIn('test2_user', usernames)
        self.assertIn('test3_user', usernames)

    def test_search_user_by_firstname(self):
        resp = self.client.get('/social/?q=test2')
        usernames = [x['username'] for x in resp.context['users']]
        self.assertIn('test2_user', usernames)
        self.assertNotIn('test3_user', usernames)
        resp = self.client.get('/social/?q=test3')
        usernames = [x['username'] for x in resp.context['users']]
        self.assertNotIn('test2_user', usernames)
        self.assertIn('test3_user', usernames)

    def test_search_nonexistent_user(self):
        resp = self.client.get('/social/?q=nonexistent')
        self.assertFalse('users' in resp.context)

class AddFriends(TestCase):
    fixtures = ['users.json']

    def setUp(self) -> None:
        self.client.login(username='test_user', password='password')
        return super().setUp()

    def test_add_friend_by_id(self):
        resp = self.client.get('/')
        self.assertFalse(resp.context['user'].friends.filter(pk=1).exists())
        resp = self.client.post('/api/add-friend/', {'user_id': 1}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        self.assertTrue(resp.context['user'].friends.filter(pk=1).exists())
    
    def test_add_friend_by_username(self):
        resp = self.client.get('/')
        self.assertFalse(resp.context['user'].friends.filter(username='admin').exists())
        resp = self.client.post('/api/add-friend/', {'username': 'admin'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        self.assertTrue(resp.context['user'].friends.filter(username='admin').exists())

    def test_remove_friend_by_id(self):
        self.client.post('/api/add-friend/', {'user_id': 1}, content_type='application/json')
        resp = self.client.get('/')
        self.assertTrue(resp.context['user'].friends.filter(pk=1).exists())
        resp = self.client.post('/api/remove-friend/', {'user_id': 1}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        self.assertFalse(resp.context['user'].friends.filter(pk=1).exists())

    def test_remove_friend_by_username(self):
        self.client.post('/api/add-friend/', {'username': 'admin'}, content_type='application/json')
        resp = self.client.get('/')
        self.assertTrue(resp.context['user'].friends.filter(username='admin').exists())
        resp = self.client.post('/api/remove-friend/', {'username': 'admin'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        self.assertFalse(resp.context['user'].friends.filter(username='admin').exists())

    def test_add_and_remove(self):
        resp = self.client.get('/')
        self.assertFalse(resp.context['user'].friends.filter(pk=1).exists())
        resp = self.client.post('/api/add-friend/', {'user_id': 1, 'username': 'random'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        self.assertTrue(resp.context['user'].friends.filter(pk=1).exists())
        resp = self.client.post('/api/remove-friend/', {'user_id': 1, 'username': 'random'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        self.assertFalse(resp.context['user'].friends.filter(pk=1).exists())
        resp = self.client.post('/api/add-friend/', {'user_id': 777, 'username': 'admin'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        self.assertTrue(resp.context['user'].friends.filter(pk=1).exists())
        resp = self.client.post('/api/remove-friend/', {'user_id': 777, 'username': 'admin'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        self.assertFalse(resp.context['user'].friends.filter(pk=1).exists())

    def test_add_and_remove_failure(self):
        resp = self.client.post('/api/add-friend/', {'user_id': 777}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Failure')
        resp = self.client.post('/api/add-friend/', {'username': 'random'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Failure')
        resp = self.client.post('/api/add-friend/', {'user_id': 777, 'username': 'random'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Failure')
        resp = self.client.get('/')
        self.assertFalse(resp.context['user'].friends.filter(pk=777).exists())
        self.assertFalse(resp.context['user'].friends.filter(username='random').exists())
        self.client.post('/api/add-friend/', {'user_id': 1}, content_type='application/json')
        resp = self.client.post('/api/add-friend/', {'user_id': 777}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Failure')
        resp = self.client.post('/api/add-friend/', {'username': 'random'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Failure')
        resp = self.client.post('/api/add-friend/', {'user_id': 777, 'username': 'random'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Failure')
        resp = self.client.get('/')
        self.assertTrue(resp.context['user'].friends.filter(pk=1).exists())
        

class Comments(TestCase):
    fixtures = ['users.json']

    def setUp(self) -> None:
        self.client.login(username='admin', password='password')
        resp = self.client.post('/api/add-schedule/', {"semester": 1228, "name": "Test Schedule", "color": "#000000"}, content_type="application/json")
        self.assertEquals(resp.json()['result'], 'Success')
        self.client.logout()
        self.client.login(username='test_user', password='password')
        return super().setUp()

    def test_post_comment(self):
        resp = self.client.post('/api/post-comment/', {'schedule_id': 1, 'text': 'Such empty'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        schedule = Schedule.objects.get(pk=1)
        self.assertTrue(Comment.objects.filter(schedule=schedule, user=resp.context['user'], text='Such empty').exists())

    def test_delete_comment(self):
        resp = self.client.post('/api/post-comment/', {'schedule_id': 1, 'text': 'Such empty'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/delete-comment/', {'comment_id': 1}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        schedule = Schedule.objects.get(pk=1)
        self.assertFalse(Comment.objects.filter(schedule=schedule, user=resp.context['user'], text='Such empty').exists())

    def test_access_denied(self):
        resp = self.client.post('/api/post-comment/', {'schedule_id': 1, 'text': 'Such empty'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        self.client.logout()
        self.client.login(username='admin', password='password')
        resp = self.client.post('/api/delete-comment/', {'comment_id': 1}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Access denied')
        resp = self.client.get('/')
        schedule = Schedule.objects.get(pk=1)
        self.assertFalse(Comment.objects.filter(schedule=schedule, user=resp.context['user'], text='Such empty').exists())

    def test_multiple_comments_and_deletes(self):
        resp = self.client.post('/api/post-comment/', {'schedule_id': 1, 'text': 'Such empty'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/post-comment/', {'schedule_id': 1, 'text': 'Very comment'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/post-comment/', {'schedule_id': 1, 'text': 'Such insight'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/post-comment/', {'schedule_id': 1, 'text': 'Wow'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/post-comment/', {'schedule_id': 1, 'text': 'So facts'}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        schedule = Schedule.objects.get(pk=1)
        self.assertTrue(Comment.objects.filter(schedule=schedule, user=resp.context['user'], text='Such empty').exists())
        self.assertTrue(Comment.objects.filter(schedule=schedule, user=resp.context['user'], text='Very comment').exists())
        self.assertTrue(Comment.objects.filter(schedule=schedule, user=resp.context['user'], text='Such insight').exists())
        self.assertTrue(Comment.objects.filter(schedule=schedule, user=resp.context['user'], text='Wow').exists())
        self.assertTrue(Comment.objects.filter(schedule=schedule, user=resp.context['user'], text='So facts').exists())
        resp = self.client.post('/api/delete-comment/', {'comment_id': 1}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/delete-comment/', {'comment_id': 4}, content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        self.assertFalse(Comment.objects.filter(schedule=schedule, user=resp.context['user'], text='Such empty').exists())
        self.assertTrue(Comment.objects.filter(schedule=schedule, user=resp.context['user'], text='Very comment').exists())
        self.assertTrue(Comment.objects.filter(schedule=schedule, user=resp.context['user'], text='Such insight').exists())
        self.assertFalse(Comment.objects.filter(schedule=schedule, user=resp.context['user'], text='Wow').exists())
        self.assertTrue(Comment.objects.filter(schedule=schedule, user=resp.context['user'], text='So facts').exists())
        
class TestSchedulePostView(StaticLiveServerTestCase):
    fixtures = ['users.json', "schedules.json"]

    def setUp(self):
        super().setUp()
        
        # chrome_driver = Service(
        # "C:\\Users\\kdu20\\Documents\\Java Files\\chromedriver.exe")
        # options = Options()
        # options.add_argument("--headless")
        # options.add_argument("--start-maximized")
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
    
    def test_own_schedule(self):
        self.driver.get(self.live_server_url + "/view-schedule/1")
        self.assertNotIn("Add Friend", self.driver.page_source)
    
    def test_add_comment(self):
        self.driver.get(self.live_server_url + "/view-schedule/1")
        comment_text = "I used to rule the world, seas would rise when I gave the word"
        comment_field = self.driver.find_element(By.CSS_SELECTOR, "#comment-field")
        comment_field.send_keys(comment_text)
        post_button = self.driver.find_element(By.CSS_SELECTOR, "button[onclick='addComment();']")
        self.driver.execute_script("arguments[0].click()", post_button)
        comment_body_text = self.driver.find_element(By.CSS_SELECTOR, "#comments-body").text
        #Check if added to the comment body
        self.assertIn(comment_text, comment_body_text)
        #Check if comment persists
        self.driver.refresh()
        comment_body_text = self.driver.find_element(By.CSS_SELECTOR, "#comments-body").text
        self.assertIn(comment_text, comment_body_text)
    
    def test_add_friend(self):
        self.driver.get(self.live_server_url + "/view-schedule/2")
        add_friend_button = self.driver.find_element(By.CSS_SELECTOR, "#add-friend-1")
        add_friend_button.click()
        self.driver.refresh()
        self.assertIn("Remove Friend", self.driver.page_source)

    def test_remove_friend(self):
        self.driver.get(self.live_server_url + "/view-schedule/2")
        add_friend_button = self.driver.find_element(By.CSS_SELECTOR, "#add-friend-1")
        add_friend_button.click()
        self.driver.implicitly_wait(10)
        remove_friend_button = self.driver.find_element(By.CSS_SELECTOR, "#remove-friend-1")
        remove_friend_button.click()
        self.driver.implicitly_wait(10)
        self.driver.refresh()
        self.assertIn("Add Friend", self.driver.page_source)
    
#     def test_view_friend_schedule(self):
#         self.driver.get(self.live_server_url + "/view-schedule/2")
#         add_friend_button = self.driver.find_element(By.CSS_SELECTOR, "#add-friend-1")
#         add_friend_button.click()
#         self.driver.get(self.live_server_url + "/view-schedule/3")
#         self.assertIn("Public to Friends Schedule User 1", self.driver.page_source)

    def test_unauthorized_public_to_friends(self):
        self.driver.get(self.live_server_url + "/view-schedule/3")
        unauthorized_text = "The owner of this schedule has marked it private for non-friends."
        self.assertIn(unauthorized_text, self.driver.page_source)
    
    def test_unauthorized_private(self):
        self.driver.get(self.live_server_url + "/view-schedule/4")
        unauthorized_text = "The owner of this schedule has marked it private."
        self.assertIn(unauthorized_text, self.driver.page_source)

    def test_private_schedule_friend(self):
        self.driver.get(self.live_server_url + "/view-schedule/2")
        add_friend_button = self.driver.find_element(By.CSS_SELECTOR, "#add-friend-1")
        add_friend_button.click()
        self.driver.get(self.live_server_url + "/view-schedule/4")
        unauthorized_text = "The owner of this schedule has marked it private."
        self.assertIn(unauthorized_text, self.driver.page_source)
        

