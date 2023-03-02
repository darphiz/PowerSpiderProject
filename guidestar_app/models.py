from django.db import models

# Create your models here.
class GuideStarIndexedUrl (models.Model):
    url = models.CharField(max_length=200, unique=True, null=False)
    is_scraped = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    added_on = models.DateTimeField(auto_now=True)
    scraped_on = models.DateTimeField(null=True)
    trial = models.IntegerField(default=0)
    def __str__(self):
        return self.url
    
class CrawlCursor(models.Model):
    increment = models.IntegerField(default=5)
    current_cursor = models.IntegerField(default=1)
    max_cursor = models.IntegerField(default=20)
    app = models.CharField(max_length=100, null=False)
    
    def save(self, *args, **kwargs):
        if self.increment > self.max_cursor:
            self.increment = self.max_cursor
            print("Increment cannot be greater than max_cursor")
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.current_cursor} - {self.max_cursor}"


class SessionTracker(models.Model):
    cookies = models.TextField(null=True)
    created = models.DateTimeField(auto_now=True)

class NGO(models.Model):
    organization_name = models.CharField(max_length=200, unique=True)
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