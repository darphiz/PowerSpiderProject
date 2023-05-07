from irs_app.models import ZIP_NGO
from merger.models import UniqueNGO

def merge_zip():
    all_zip_ngos = ZIP_NGO.objects.all()
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
    