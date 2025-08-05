from organizations.models import Class, School, OrganizationType

def check_organization_exists(organization_type, organization_id):
    if organization_type == OrganizationType.CLASS:
        return Class.objects.filter(id=organization_id).exists()
    elif organization_type == OrganizationType.SCHOOL:
        return School.objects.filter(id=organization_id).exists()
    else:
        return False