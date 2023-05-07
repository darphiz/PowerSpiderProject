from global_giving_india.models import NGO
from merger.models import UniqueNGO




def merge_ggi():
    all_fcra_ngos = NGO.objects.filter(govt_reg_number__isnull=False)
    total = all_fcra_ngos.count()
    print(f"Total: {total}")
    bulk_NGOs = [
        UniqueNGO(
            govt_reg_number=ngo.govt_reg_number,
            govt_reg_number_type="darpan id",
        ) for ngo in all_fcra_ngos if ngo.govt_reg_number
    ]
    UniqueNGO.objects.bulk_create(bulk_NGOs, ignore_conflicts=True, batch_size=1000)
    print(f"Created {total} UniqueNGOs")
    return total