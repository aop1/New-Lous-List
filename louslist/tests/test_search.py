from django.test import TestCase
from django.urls import reverse
from requests import get

class AdvancedSearch(TestCase):
    fixtures = ['../scripts/prefix.json']

    def test_search_CS_and_Sherriff(self):
        resp = self.client.post('/results/', {'mnemonic': 'CS', 'instructor': 'Sherriff'})
        self.assertGreaterEqual(len(resp.context['courses_by_number']), 1)
        for courses in resp.context['courses_by_number'].values():
            self.assertGreaterEqual(len(courses), 1)
            for course in courses:
                self.assertIn('Sherriff', course['instructor']['name'])
                self.assertEquals('CS', course['subject'])

    def test_search_she_instructor_name(self):
        resp = self.client.post('/results/', {'instructor': 'she'})
        self.assertGreaterEqual(len(resp.context['courses_by_number']), 1)
        for courses in resp.context['courses_by_number'].values():
            self.assertGreaterEqual(len(courses), 1)
            for course in courses:
                self.assertIn('she', course['instructor']['name'].lower())

    def test_search_9AM_5PM(self):
        resp = self.client.post('/results/', {'start_time': '09:00', 'end_time': '17:00'})
        self.assertGreaterEqual(len(resp.context['courses_by_number']), 1)
        for courses in resp.context['courses_by_number'].values():
            self.assertGreaterEqual(len(courses), 1)
            for course in courses:
                self.assertLessEqual(900, int(course['start_time'][:2] + course['start_time'][3:5]))
                self.assertGreaterEqual(1700, int(course['end_time'][:2] + course['end_time'][3:5]))

    def test_search_20(self):
        resp = self.client.post('/results/', {'number': '20'})
        self.assertGreaterEqual(len(resp.context['courses_by_number']), 1)
        for courses in resp.context['courses_by_number'].values():
            self.assertGreaterEqual(len(courses), 1)
            for course in courses:
                self.assertIn('20', course['catalog_number'])

    def test_search_TuTh(self):
        resp = self.client.post('/results/', {'tu': 'Tu', 'th': 'Th'})
        self.assertGreaterEqual(len(resp.context['courses_by_number']), 1)
        for courses in resp.context['courses_by_number'].values():
            self.assertGreaterEqual(len(courses), 1)
            for course in courses:
                self.assertIn('TuTh', course['days'])

    def test_search_intro(self):
        resp = self.client.post('/results/', {'name': 'intro'})
        self.assertGreaterEqual(len(resp.context['courses_by_number']), 1)
        for courses in resp.context['courses_by_number'].values():
            self.assertGreaterEqual(len(courses), 1)
            for course in courses:
                self.assertIn('intro', course['description'].lower())

    def test_search_20_min(self):
        resp = self.client.post('/results/', {'min': 20})
        self.assertGreaterEqual(len(resp.context['courses_by_number']), 1)
        for courses in resp.context['courses_by_number'].values():
            self.assertGreaterEqual(len(courses), 1)
            for course in courses:
                self.assertLessEqual(20, course['enrollment_available'])

    def test_east_asian_languages(self):
        resp = self.client.post('/results/', {'dept': 'east asian lang'})
        mnemonics = ['CHIN', 'CHTR', 'EALC', 'EAST', 'JAPN', 'JPTR', 'KOR']
        self.assertGreaterEqual(len(resp.context['courses_by_number']), 1)
        for courses in resp.context['courses_by_number'].values():
            self.assertGreaterEqual(len(courses), 1)
            for course in courses:
                self.assertIn(course['subject'], mnemonics)

    def test_search_all(self):
        resp = self.client.post('/results/', {'mnemonic': 'apma', 'instructor': 'meiqin',
        'mo': 'Mo', 'we': 'We', 'name': 'linear', 'number': '80', 'start_time': '10:00',
        'end_time':'14:00', 'min': 3, 'dept': 'applied math'})
        self.assertEquals(1, len(resp.context['courses_by_number']))
        for courses in resp.context['courses_by_number'].values():
            self.assertEquals(2, len(courses))
            for course in courses:
                self.assertEquals('APMA', course['subject'])
                self.assertEquals('Meiqin Li', course['instructor']['name'])
                self.assertIn('MoWe', course['days'])
                self.assertEquals('Linear Algebra', course['description'])
                self.assertEquals('3080', course['catalog_number'])
                self.assertLessEqual(1000, int(course['start_time'][:2] + course['start_time'][3:5]))
                self.assertGreaterEqual(1400, int(course['end_time'][:2] + course['end_time'][3:5]))
                self.assertLessEqual(3, course['enrollment_available'])

    def test_nonexistent(self):
        resp = self.client.post('/results/', {'mnemonic': 'non', 'instructor': 'inst'})
        self.assertEquals(0, len(resp.context['courses_by_number']))
        self.assertIn('No courses matched', resp.context['error_message'])
        self.assertEquals(['Class Mnemonic: NON', 'Instructor: inst'], resp.context['filters'])

    def test_nonexistent_all(self):
        resp = self.client.post('/results/', {'mnemonic': 'non', 'instructor': 'inst',
        'mo': 'Mo', 'we': 'We', 'name': 'nonexistent', 'number': '80', 'start_time': '10:00',
        'end_time':'14:00', 'min': 5, 'dept': 'dept'})
        self.assertEquals(0, len(resp.context['courses_by_number']))
        self.assertIn('No courses matched', resp.context['error_message'])
        self.assertEquals(['Class Title: nonexistent', 'Class Mnemonic: NON', 'Class Number: 80',\
            'Department: dept', 'Instructor: inst', 'Meeting Days: MoWe', 'Start Time: 10:00 AM',\
            'End Time: 2:00 PM', 'Minimum Seats Available: 5'], resp.context['filters'])

class QuickSearch(TestCase):
    fixtures = ['../scripts/prefix.json']

    def test_quick_search(self):
        search_words = ['computer', 'calculus', 'multivar', 'how things', 'intro to cyber']
        for search in search_words:
            resp = self.client.get(f'/search/?q={search}')
            course_resp = get(f'https://thecourseforum.com/search/?q={search}')
            for courses in resp.context['courses_by_number'].values():
                for course in courses:
                    self.assertIn(f"{course['subject']} {course['catalog_number']}", course_resp.text)

    def test_quick_search_mnemonics(self):
        mnemonics = ['CS', 'APma', 'ENGR', 'math', 'ECON', 'STS']
        for mnemonic in mnemonics:
            resp0 = self.client.get(f'/search/?q={mnemonic}')
            resp1 = self.client.post(f'/results/', {'mnemonic': mnemonic})
            for courses0, courses1 in zip(resp0.context['courses_by_number'].values(), resp1.context['courses_by_number'].values()):
                for course0, course1 in zip(courses0, courses1):
                    self.assertEquals(course0['course_number'], course1['course_number'])

    def test_quick_search_departments(self):
        depts = ['computer science', 'applied MAthematics', 'Mathematics', 'EcoNOmics', 'Science, Technology %26 Society']
        dept_pages = ['Computer Science', 'Applied Mathematics', 'Mathematics', 'Economics', 'Science, Technology & Society']
        for dept, dept_page in zip(depts, dept_pages):
            resp0 = self.client.get(f'/search/?q={dept}')
            resp1 = self.client.get(f'/departments/{dept_page}/')
            for courses0, courses1 in zip(resp0.context['courses_by_number'].values(), resp1.context['courses_by_number'].values()):
                for course0, course1 in zip(courses0, courses1):
                    self.assertEquals(course0['course_number'], course1['course_number'])

    def test_nonexistent(self):
        resp = self.client.get('/search/?q=nonexistent')
        self.assertEquals(len(resp.context['courses_by_number']), 0)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("No courses matched 'nonexistent'", resp.context['error_message'])

class Department(TestCase):
    fixtures = ['../scripts/prefix.json']

    def test_Computer_Science(self):
        resp = self.client.get(reverse('department', args=('Computer Science',)))
        self.assertEquals(resp.context['courses_by_number']['CS 1010'][0]['course_number'], 16351)
        self.assertContains(resp, 'Advanced Software Development Techniques')

    def test_Spanish_Italian_Portuguese(self):
        resp = self.client.get(reverse('department', args=('Spanish, Italian & Portuguese',)))
        self.assertGreaterEqual(len(resp.context['courses_by_number']), 1)
        for courses in resp.context['courses_by_number'].values():
            for course in courses:
                self.assertIn(course['subject'], ['ITAL', 'ITTR', 'KICH', 'PORT', 'SPAN'])

    def test_nonexistent_dept(self):
        resp = self.client.get(reverse('department', args=('nonexistent',)))
        self.assertEquals(len(resp.context['courses_by_number']), 0)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("No courses matched 'nonexistent'", resp.context['error_message'])