import json
from guidestar_app.models import NGO
from merger.models import UniqueNGO


def update_gs_ngo(ein, email):
    try:
        ngo = NGO.objects.get(govt_reg_number=ein)
        if not ngo.email:
            ngo.email = email
            ngo.save()
            print(f"Updated {ngo.organization_name} with email {email}")
        else:
            print(f"Email already exists for {ngo.organization_name}")
    except NGO.DoesNotExist:
        print(f"Could not find NGO with EIN {ein}")
    return 
    


def import_emails():
    with open('merger/scripts/gs_urls.json') as f:
        data = json.load(f)
    gs_urls = data['gs_primary_email_only']
    for gs_data in gs_urls:
        ein = gs_data['EIN']
        email = gs_data['primary_email']
        update_gs_ngo(ein, email)
    return

def merge():
    all_zip_ngos = NGO.objects.all()
    total = all_zip_ngos.count()
    print(f"Total: {total}")
    bulk_NGOs = [
        UniqueNGO(
            govt_reg_number=ngo.govt_reg_number,
            govt_reg_number_type="ein",
        ) for ngo in all_zip_ngos if ngo.govt_reg_number
    ]
    UniqueNGO.objects.bulk_create(bulk_NGOs, ignore_conflicts=True, batch_size=1000)
    print(f"Created {total} UniqueNGOs")
    return total


