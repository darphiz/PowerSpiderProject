from django.db import models

class CrawlCursor(models.Model):
    current_page = models.IntegerField(default=1)
    max_cursor = models.IntegerField(default=20)
    app = models.CharField(max_length=100, null=False)
    
    def save(self, *args, **kwargs):
        if self.current_page > self.max_cursor:
            self.current_page = self.max_cursor
            print("Increment cannot be greater than max_cursor")
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.current_page} - {self.max_cursor}"

class FailedPages(models.Model):
    page = models.IntegerField(default=1, primary_key=True)
    error = models.TextField(null=True)
    trial = models.IntegerField(default=0)
    locked = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f"{self.page}"


class NGO(models.Model):
    organization_name = models.CharField(max_length=200)
    organization_address = models.CharField(max_length=200)
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

    def __str__(self) -> str:
        return self.organization_name

    class Meta:
        verbose_name_plural = "NGOs"
        # ordering = ['organization_name']

class LastPage(models.Model):
    page = models.IntegerField(default=1)
    state = models.CharField(max_length=200, null=False)
    cause = models.CharField(max_length=200, null=False)

    def __str__(self) -> str:
        return f"{self.page} - {self.state} - {self.cause}"