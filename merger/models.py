from django.db import models

class MergedNGO(models.Model):
    organization_name = models.JSONField(null=True)
    organization_address = models.JSONField(null=True)
    country = models.JSONField(null=True)
    state = models.JSONField(null=True) 
    cause = models.JSONField(null=True)
    email = models.JSONField(null=True)
    phone = models.JSONField(null=True)
    website = models.JSONField(null=True)
    mission =  models.JSONField(null=True)
    description = models.JSONField(null=True)
    govt_reg_number = models.CharField(max_length=200, null=True, unique=True)
    govt_reg_number_type = models.CharField(max_length=200, null=True)
    registration_date_year = models.JSONField(null=True)
    registration_date_month = models.JSONField(null=True)
    registration_date_day =  models.JSONField(null=True)
    gross_income = models.JSONField(null=True)
    image = models.JSONField(null=True)
    domain = models.JSONField(null=True)
    urls_scraped =  models.JSONField(null=True)
    def __str__(self) -> str:
        return self.govt_reg_number
    
    class Meta:
        unique_together = ('govt_reg_number','govt_reg_number_type')
        
        
class UniqueNGO(models.Model):
    organization_name = models.CharField(max_length=200)
    organization_address = models.TextField(null=True)
    country = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True) 
    cause = models.TextField(null=True)
    email = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    website = models.CharField(max_length=200, null=True)
    mission =  models.TextField(null=True)
    description = models.TextField(null=True)
    govt_reg_number = models.CharField(max_length=200, null=True, unique=True)
    govt_reg_number_type = models.CharField(max_length=200, null=True)
    registration_date_year = models.CharField(max_length=200, null=True)
    registration_date_month = models.CharField(max_length=200, null=True)
    registration_date_day =  models.CharField(max_length=200, null=True)
    gross_income = models.CharField(max_length=200, null=True)
    image = models.TextField(max_length=200, null=True)
    domain = models.CharField(max_length=200, null=True)
    urls_scraped =  models.TextField(null=True)
    has_merged = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    
    # 646034462
    def __str__(self) -> str:
        return self.govt_reg_number
    
    class Meta:
        unique_together = ('govt_reg_number','govt_reg_number_type')
    