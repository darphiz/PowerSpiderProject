from django.db import models

class FCR_Cursor(models.Model):
    state = models.CharField(max_length=200)
    state_id = models.CharField(max_length=200)
    is_scraped = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    added_on = models.DateTimeField(auto_now=True)
    scraped_on = models.DateTimeField(null=True)
    year = models.CharField(max_length=200)
    
    def __str__(self) -> str:
        return f"{self.state} - {self.year}"
    
class FCR_NGO(models.Model):
    organization_name = models.CharField(max_length=200, unique=True, primary_key=True)
    organization_address = models.CharField(max_length=200)
    country = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True) 
    cause = models.TextField(null=True)
    email = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    website = models.CharField(max_length=200, null=True)
    mission =  models.TextField(null=True)
    description = models.TextField(null=True)
    govt_reg_number = models.CharField(max_length=200, null=True)
    govt_reg_number_type = models.CharField(max_length=200, null=True)
    registration_date_year = models.CharField(max_length=200, null=True)
    registration_date_month = models.CharField(max_length=200, null=True)
    registration_date_day =  models.CharField(max_length=200, null=True)
    gross_income = models.CharField(max_length=200, null=True)
    image = models.TextField(max_length=200, null=True)
    domain = models.CharField(max_length=200, null=True)
    urls_scraped =  models.TextField(null=True)

    def __str__(self) -> str:
        return self.organization_name
    
