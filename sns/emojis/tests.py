from django.test import TestCase
from apps.core.organizations.organizations.models import OrganizationType
from .utils import check_organization_exists

def check_organization_exists(self):
    self.assertTrue(check_organization_exists(OrganizationType.CLASS, "123"))
    self.assertTrue(check_organization_exists(OrganizationType.SCHOOL, "123"))
    self.assertFalse(check_organization_exists(OrganizationType.CIRCLE, "123"))
