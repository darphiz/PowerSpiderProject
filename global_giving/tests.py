from .models import NGO, GlobalGivingIndexedUrl
def rem():
    NGO.objects.all().delete()
    GlobalGivingIndexedUrl.objects.update(
        is_scraped=False, locked=False, trial=0
    )
    print("Done")