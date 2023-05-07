from c_navigator.models import NGO
from merger.models import UniqueNGO


def merge_c_nav():
    all_fcra_ngos = NGO.objects.all()
    total = all_fcra_ngos.count()
    print(f"Total: {total}")
    bulk_NGOs = [
        UniqueNGO(
            govt_reg_number=ngo.govt_reg_number,
            govt_reg_number_type="ein",
        ) for ngo in all_fcra_ngos
    ]
    UniqueNGO.objects.bulk_create(bulk_NGOs, ignore_conflicts=True, batch_size=1000)
    print(f"Created {total} UniqueNGOs")
    return total