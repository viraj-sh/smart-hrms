
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser


class DashboardPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = CustomUser.objects.create_user(
            email="admin_test@example.com",
            password="TestPass123!",
            role="Admin",
        )
        cls.hr = CustomUser.objects.create_user(
            email="hr_test@example.com",
            password="TestPass123!",
            role="HR",
        )
        cls.employee = CustomUser.objects.create_user(
            email="employee_test@example.com",
            password="TestPass123!",
            role="Employee",
        )

    def setUp(self):
        self.client = Client()

    def test_admin_can_access_admin_dashboard(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_admin_cannot_access_hr_dashboard(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("hr_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_access_employee_dashboard(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("employee_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_hr_can_access_hr_dashboard(self):
        self.client.force_login(self.hr)
        response = self.client.get(reverse("hr_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_hr_cannot_access_admin_dashboard(self):
        self.client.force_login(self.hr)
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_employee_can_access_employee_dashboard(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse("employee_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_employee_cannot_access_admin_dashboard(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_employee_cannot_access_hr_dashboard(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse("hr_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

