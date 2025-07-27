from .models import Company

def company_info(request):
    try:
        company = Company.objects.first() 
    except Company.DoesNotExist:
        company = None
    return {'company': company}
