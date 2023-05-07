from fcra_app.models import FCR_NGO
from merger.models import UniqueNGO


def merge():
    all_fcra_ngos = FCR_NGO.objects.all()
    total = all_fcra_ngos.count()
    print(f"Total: {total}")
    bulk_NGOs = [
        UniqueNGO(
            govt_reg_number=ngo.govt_reg_number,
            govt_reg_number_type="fcra",
        ) for ngo in all_fcra_ngos
    ]
    UniqueNGO.objects.bulk_create(bulk_NGOs, ignore_conflicts=True, batch_size=1000)
    print(f"Created {total} UniqueNGOs")
    return total