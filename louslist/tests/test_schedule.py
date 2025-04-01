from django.test import TestCase
from louslist.models import Course, User, Schedule


class Cart(TestCase):
    fixtures = ['users.json']

    def test_add_class_to_cart(self):
        self.client.login(username='test_user', password='password')
        resp = self.client.post('/api/add-course-to-cart/', {'subject': 'CS', 'course_number': 16618,
        'description': 'Machine Learning', 'catalog_number': '4774', 'course_section': '001', 'component': 'LEC',
        'units': '3', 'enrollment_total': 0, 'class_capacity': 0, 'instructor': 'Rich Nguyen', 'topic': '',
        'meetings': [{'days': 'TuTh', 'start_time': '15:30', 'end_time': '16:45', 'facility_description': ''}]},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        self.assertTrue(
            Course.objects.filter(subject='CS', course_number=16618).exists()
        )
        self.assertTrue(
            User.objects.filter(cart__course_number=16618).exists()
        )
        resp = self.client.get('/')
        self.assertEquals(
            resp.context['user'].cart.all().get(),
            Course.objects.get(subject='CS', course_number=16618, meeting__days="TuTh",
            meeting__start_time='15:30', meeting__end_time='16:45')
        )

    def test_add_class_to_cart_failure(self):
        self.client.login(username='test_user', password='password')
        resp = self.client.post('/api/add-course-to-cart/', {'subject': 'CS',
        'description': 'Machine Learning', 'catalog_number': '4774', 'course_section': '001', 'component': 'LEC',
        'units': '3', 'enrollment_total': 0, 'class_capacity': 0, 'instructor': 'Rich Nguyen', 'topic': '',
        'meetings': [{'days': 'TuTh', 'start_time': '15:30', 'end_time': '16:45', 'facility_description': ''}]},
        content_type='application/json')
        #self.assertNotEquals(resp.json()['result'], 'Failure')
        self.assertFalse(
            Course.objects.filter(subject='CS').exists()
        )
        self.assertFalse(
            User.objects.filter(cart__subject='CS').exists()
        )
        resp = self.client.post('/api/add-course-to-cart/', {'course_number': 16618,
        'description': 'Machine Learning', 'catalog_number': '4774', 'course_section': '001', 'component': 'LEC',
        'units': '3', 'enrollment_total': 0, 'class_capacity': 0, 'instructor': 'Rich Nguyen', 'topic': '',
        'meetings': [{'days': 'TuTh', 'start_time': '15:30', 'end_time': '16:45', 'facility_description': ''}]},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Failure')
        self.assertFalse(
            Course.objects.filter(course_number=16618).exists()
        )
        self.assertFalse(
            User.objects.filter(cart__course_number=16618).exists()
        )

    def test_remove_class_from_cart(self):
        self.client.login(username='test_user', password='password')
        self.client.post('/api/add-course-to-cart/', {'subject': 'CS', 'course_number': 16618,
        'description': 'Machine Learning', 'catalog_number': '4774', 'course_section': '001', 'component': 'LEC',
        'units': '3', 'enrollment_total': 0, 'class_capacity': 0, 'instructor': 'Rich Nguyen', 'topic': '',
        'meetings': [{'days': 'TuTh', 'start_time': '15:30', 'end_time': '16:45', 'facility_description': ''}]},
        content_type='application/json')
        self.assertTrue(
            Course.objects.filter(subject='CS', course_number=16618).exists()
        )
        resp = self.client.post('/api/remove-course-from-cart/', {'prefix': 'CS', 'number': 16618}, content_type="application/json")
        self.assertEquals(resp.json()['result'],"Success")
        self.assertFalse(
            User.objects.filter(cart__course_number=16618).exists()
        )


class Schedules(TestCase):
    fixtures = ['users.json']

    def setUp(self) -> None:
        self.client.login(username='test_user', password='password')
        self.client.post('/api/add-course-to-cart/', {'subject': 'CS', 'course_number': 16618,
        'description': 'Machine Learning', 'catalog_number': '4774', 'course_section': '001', 'component': 'LEC',
        'units': '3', 'enrollment_total': 0, 'class_capacity': 0, 'instructor': 'Rich Nguyen', 'topic': '',
        'meetings': [{'days': 'TuTh', 'start_time': '15:30', 'end_time': '16:45', 'facility_description': ''}]},
        content_type='application/json')
        self.client.post('/api/add-course-to-cart/', {'subject': 'CS', 'course_number': 15569,
        'description': '', 'catalog_number': '', 'course_section': '', 'component': '',
        'units': '', 'enrollment_total': 0, 'class_capacity': 0, 'instructor': '', 'topic': '',
        'meetings': [{'days': 'TuTh', 'start_time': '14:00', 'end_time': '15:15', 'facility_description': ''}]},
        content_type='application/json')
        self.client.post('/api/add-course-to-cart/', {'subject': 'STS', 'course_number': 16867,
        'description': '', 'catalog_number': '', 'course_section': '', 'component': '',
        'units': '', 'enrollment_total': 0, 'class_capacity': 0, 'instructor': '', 'topic': '',
        'meetings': [{'days': 'TuTh', 'start_time': '12:30', 'end_time': '13:45', 'facility_description': ''}]},
        content_type='application/json')
        self.client.post('/api/add-course-to-cart/', {'subject': 'CS', 'course_number': 19555,
        'description': '', 'catalog_number': '', 'course_section': '', 'component': '',
        'units': '', 'enrollment_total': 0, 'class_capacity': 0, 'instructor': '', 'topic': '',
        'meetings': [{'days': 'TuTh', 'start_time': '15:30', 'end_time': '16:45', 'facility_description': ''}]},
        content_type='application/json')
        self.client.post('/api/add-course-to-cart/', {'subject': 'APMA', 'course_number': 16496,
        'description': '', 'catalog_number': '', 'course_section': '', 'component': '',
        'units': '', 'enrollment_total': 0, 'class_capacity': 0, 'instructor': '', 'topic': '',
        'meetings': [{'days': 'MoWe', 'start_time': '15:30', 'end_time': '16:45', 'facility_description': ''}]},
        content_type='application/json')
        self.client.post('/api/add-course-to-cart/', {'subject': 'STS', 'course_number': 15548,
        'description': '', 'catalog_number': '', 'course_section': '', 'component': '',
        'units': '', 'enrollment_total': 0, 'class_capacity': 0, 'instructor': '', 'topic': '',
        'meetings': [{'days': 'Tu', 'start_time': '15:00', 'end_time': '16:15', 'facility_description': ''}]},
        content_type='application/json')
        self.client.post('/api/add-course-to-cart/', {'subject': 'CS', 'course_number': 19682,
        'description': '', 'catalog_number': '', 'course_section': '', 'component': '',
        'units': '', 'enrollment_total': 0, 'class_capacity': 0, 'instructor': '', 'topic': '',
        'meetings': [{'days': 'Mo', 'start_time': '09:30', 'end_time': '10:15', 'facility_description': ''},
        {'days': 'WeFr', 'start_time': '12:00', 'end_time': '12:45', 'facility_description': ''}]},
        content_type='application/json')
        self.client.post('/api/add-course-to-cart/', {'subject': 'APMA', 'course_number': 18152,
        'description': '', 'catalog_number': '', 'course_section': '', 'component': '',
        'units': '', 'enrollment_total': 0, 'class_capacity': 0, 'instructor': '', 'topic': '',
        'meetings': [{'days': 'We', 'start_time': '09:30', 'end_time': '10:15', 'facility_description': ''},
        {'days': 'TuTh', 'start_time': '15:00', 'end_time': '16:15', 'facility_description': ''}]},
        content_type='application/json')
        self.client.post('/api/add-course-to-cart/', {'subject': 'STS', 'course_number': 15632,
        'description': '', 'catalog_number': '', 'course_section': '', 'component': '',
        'units': '', 'enrollment_total': 0, 'class_capacity': 0, 'instructor': '', 'topic': '',
        'meetings': [{'days': 'MoWe', 'start_time': '11:45', 'end_time': '12:30', 'facility_description': ''},
        {'days': 'Fr', 'start_time': '13:00', 'end_time': '14:15', 'facility_description': ''}]},
        content_type='application/json')
        self.client.post('/api/add-course-to-cart/', {'subject': 'CS', 'course_number': 17152,
        'description': '', 'catalog_number': '', 'course_section': '', 'component': '',
        'units': '', 'enrollment_total': 0, 'class_capacity': 0, 'instructor': '', 'topic': '',
        'meetings': [{'days': 'We', 'start_time': '09:15', 'end_time': '10:00', 'facility_description': ''},
        {'days': 'MoFr', 'start_time': '12:30', 'end_time': '13:45', 'facility_description': ''}]},
        content_type='application/json')
        self.client.post('/api/add-schedule/', {"semester": 1228, "name": "Test Schedule", "color": "#000000"}, content_type="application/json")
        return super().setUp()

    def test_add_courses_to_schedule(self):
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'CS', 'course_number': 16618, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'CS', 'course_number': 15569, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'STS', 'course_number': 16867, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        self.assertEquals(
            Schedule.objects.get(user=resp.context['user']).classes.get(course_number=16618),
            Course.objects.get(course_number=16618)
        )
        self.assertEquals(
            Schedule.objects.get(user=resp.context['user']).classes.get(course_number=15569),
            Course.objects.get(course_number=15569)
        )
        self.assertEquals(
            Schedule.objects.get(user=resp.context['user']).classes.get(course_number=16867), Course.objects.get(course_number=16867)
        )

    def test_add_nonconflicting_courses(self):
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'CS', 'course_number': 16618, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'APMA', 'course_number': 16496, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        self.assertEquals(
            Schedule.objects.get(user=resp.context['user']).classes.get(course_number=16618), Course.objects.get(course_number=16618)
        )
        self.assertEquals(
            Schedule.objects.get(user=resp.context['user']).classes.get(course_number=16496), Course.objects.get(course_number=16496)
        )

    def test_add_conflicting_courses(self):
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'CS', 'course_number': 16618, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'CS', 'course_number': 19555, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Time Conflict')
        resp = self.client.get('/')
        self.assertEquals(
            Schedule.objects.get(user=resp.context['user']).classes.get(course_number=16618), Course.objects.get(course_number=16618)
        )
        self.assertFalse(
            Schedule.objects.filter(classes__course_number=19555).exists()
        )
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'STS', 'course_number': 15548, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Time Conflict')
        resp = self.client.get('/')
        self.assertFalse(
            Schedule.objects.filter(classes__course_number=15548).exists()
        )

    def test_add_to_multiple_schedules(self):
        self.client.post('/api/add-schedule/', {"semester": 1228, "name": "Test Schedule", "color": "#000000"}, content_type="application/json")
        self.client.post('/api/add-schedule/', {"semester": 1228, "name": "Test Schedule", "color": "#000000"}, content_type="application/json")
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'CS', 'course_number': 16618, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'CS', 'course_number': 15569, 'schedule_id': 2},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'STS', 'course_number': 16867, 'schedule_id': 3},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'STS', 'course_number': 16867, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        self.assertEquals(
            Schedule.objects.get(pk=1).classes.get(course_number=16618), Course.objects.get(course_number=16618)
        )
        self.assertEquals(
            Schedule.objects.get(pk=2).classes.get(course_number=15569), Course.objects.get(course_number=15569)
        )
        self.assertEquals(
            Schedule.objects.get(pk=3).classes.get(course_number=16867), Course.objects.get(course_number=16867)
        )
        self.assertEquals(
            Schedule.objects.get(pk=1).classes.get(course_number=16867), Course.objects.get(course_number=16867)
        )

    def test_add_nonconflicting_multiple_meetings(self):
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'CS', 'course_number': 19682, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'APMA', 'course_number': 18152, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.get('/')
        self.assertEquals(
            Schedule.objects.get(user=resp.context['user']).classes.get(course_number=19682,), Course.objects.get(course_number=19682)
        )
        self.assertEquals(
            Schedule.objects.get(user=resp.context['user']).classes.get(course_number=18152), Course.objects.get(course_number=18152)
        )

    def test_add_conflicting_multiple_meetings(self):
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'CS', 'course_number': 19682, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'STS', 'course_number': 15632, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Time Conflict')
        resp = self.client.get('/')
        self.assertEquals(
            Schedule.objects.get(user=resp.context['user']).classes.get(course_number=19682), Course.objects.get(course_number=19682)
        )
        self.assertFalse(
            Schedule.objects.filter(classes__course_number=15632).exists()
        )
        resp = self.client.post('/api/add-course-to-schedule/', {'subject': 'CS', 'course_number': 17152, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Time Conflict')
        resp = self.client.get('/')
        self.assertFalse(
            Schedule.objects.filter(classes__course_number=17152).exists()
        )

    def test_remove_from_schedule_pass(self):
        self.client.post('/api/add-course-to-schedule/', {'course_number': 16618, 'schedule_id': 1},
        content_type='application/json')
        self.client.post('/api/add-course-to-schedule/', {'course_number': 15569, 'schedule_id': 1},
        content_type='application/json')
        resp = self.client.get('/')
        self.assertEquals(
            Schedule.objects.get(user=resp.context['user']).classes.get(course_number=16618),
            Course.objects.get(course_number=16618)
        )
        self.assertEquals(
            Schedule.objects.get(user=resp.context['user']).classes.get(course_number=15569),
            Course.objects.get(course_number=15569)
        )
        resp = self.client.post('/api/remove-course-from-schedule/', {'course_number': 16618, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Success')
        self.assertFalse(
            Schedule.objects.filter(classes__course_number=16618).exists()
        )
        resp = self.client.get('/')
        self.assertEquals(
            Schedule.objects.get(user=resp.context['user']).classes.get(course_number=15569),
            Course.objects.get(course_number=15569)
        )
        
    def test_remove_from_schedule_failure(self):
        self.client.post('/api/add-course-to-schedule/', {'course_number': 16618, 'schedule_id': 1},
        content_type='application/json')
        resp = self.client.get('/')
        self.assertEquals(
            Schedule.objects.get(user=resp.context['user']).classes.get(course_number=16618),
            Course.objects.get(course_number=16618)
        )
        resp = self.client.post('/api/remove-course-from-schedule/', {'course_number': 15569, 'schedule_id': 1},
        content_type='application/json')
        self.assertEquals(resp.json()['result'], 'Failure')
        resp = self.client.get('/')
        self.assertEquals(
            Schedule.objects.get(user=resp.context['user']).classes.get(course_number=16618),
            Course.objects.get(course_number=16618)
        )