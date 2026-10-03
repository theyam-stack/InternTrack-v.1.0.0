from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Company, Interview, Internship, Profile


class InternshipViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='safe-password-123')
        self.other_user = User.objects.create_user(username='other', password='safe-password-123')
        self.company = Company.objects.create(name='Example Co.')
        self.application = Internship.objects.create(
            user=self.user,
            company=self.company,
            role='Software Intern',
            status='Applied',
        )

    def test_new_users_receive_a_profile(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_register_page_renders_and_creates_a_logged_in_user(self):
        response = self.client.get(reverse('register'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create account')

        response = self.client.post(reverse('register'), {
            'username': 'new-candidate',
            'password1': 'secure-password-456',
            'password2': 'secure-password-456',
        })

        self.assertRedirects(response, reverse('internship_list'))
        user = User.objects.get(username='new-candidate')
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_application_list_supplies_pagination_and_counts(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('internship_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_count'], 1)
        self.assertEqual(list(response.context['page_obj']), [self.application])

    def test_creating_an_application_saves_the_company_location(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('internship_create'), {
            'company_name': 'Location Co.',
            'company_location': 'Bangkok, Thailand',
            'role': 'Product Intern',
            'status': 'Applied',
            'application_date': '2026-10-03',
            'notes': '',
        })

        self.assertRedirects(response, reverse('internship_list'))
        self.assertEqual(Company.objects.get(name='Location Co.').location, 'Bangkok, Thailand')

    def test_application_detail_does_not_render_template_comments(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('internship_detail', args=[self.application.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Software Intern')
        self.assertNotContains(response, 'Status pill. The CSS classes')

    def test_dashboard_includes_pending_and_upcoming_interviews(self):
        Interview.objects.create(
            internship=self.application,
            interview_date=timezone.now() + timedelta(days=2),
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['stats']['pending'], 1)
        self.assertEqual(list(response.context['upcoming_interviews'])[0].internship, self.application)

    def test_users_cannot_change_or_add_interviews_to_other_users_applications(self):
        other_application = Internship.objects.create(
            user=self.other_user,
            company=self.company,
            role='Private role',
        )
        self.client.force_login(self.user)

        self.assertEqual(
            self.client.get(reverse('internship_update', args=[other_application.pk])).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse('interview_create', args=[other_application.pk])).status_code,
            404,
        )

    def test_export_honours_a_valid_status_filter(self):
        Internship.objects.create(
            user=self.user,
            company=self.company,
            role='Accepted role',
            status='Accepted',
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('export_csv'), {'status': 'Accepted'})

        body = response.content.decode()
        self.assertIn('Accepted role', body)
        self.assertNotIn('Software Intern', body)

    def test_invalid_sort_and_interview_range_fall_back_safely(self):
        self.client.force_login(self.user)

        list_response = self.client.get(reverse('internship_list'), {'sort': 'invalid_field'})
        interview_response = self.client.get(reverse('interview_list'), {'range': 'not-a-range'})

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.context['sort_order'], '-application_date')
        self.assertEqual(interview_response.status_code, 200)
        self.assertEqual(interview_response.context['range_filter'], '30')
