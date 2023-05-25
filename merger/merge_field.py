from guidestar_app.models import NGO as GStarNGO
from c_navigator.models import NGO as CNavNGO
from merger.models import UniqueNGO
from django.db.models import Q
from .pipe import pipe_list
from pledge_app.models import NGO as PledgeNGO
from global_giving_india.models import NGO as GGIndiaNGO
from fcra_app.models import FCR_NGO
from irs_app.models import NGO_V2 as XMLNGO, ZIP_NGO
from django.db.models.functions import Length

def format_list(lists):
    try:
        if not lists:
            return None
        if not isinstance(lists, list):
            lists = [lists]
        _set = {"\"" + x + "\"" for x in lists}
        _set = str(_set).replace("'", "")
        return _set
    except Exception:
        return None

def merger(Model):
    """
    DO a search and rename the fields to match the field you want to merge
    E.g. This is for merging the gross_income field
    """
    all_model_ngo = Model.objects.filter(
        Q(gross_income__isnull=False) &  ~Q(gross_income='')).values_list('govt_reg_number', flat=True)
    empty_unique_ngos = UniqueNGO.objects.filter(
        Q(gross_income__isnull=True) | Q(gross_income=""),
    ).values_list('govt_reg_number', flat=True)    
    intersect_ein = set(all_model_ngo).intersection(set(empty_unique_ngos))
    total = len(intersect_ein)
    counter = 0
    to_update = Model.objects.filter(govt_reg_number__in=intersect_ein).values_list(
        "govt_reg_number",
        "gross_income",
        "urls_scraped",
        "domain"
    )
    
    bulk_NGOs = []
    for update_ng in to_update:
        unique_ngo = UniqueNGO.objects.get(govt_reg_number=update_ng[0])
        add_to_bulk = False
        if (not unique_ngo.gross_income) and update_ng[1]:
            unique_ngo.gross_income = update_ng[1]
            unique_ngo.urls_scraped = pipe_list(unique_ngo.urls_scraped, update_ng[2])
            unique_ngo.domain = pipe_list(unique_ngo.domain, update_ng[3])
            add_to_bulk = True
        if add_to_bulk:
            bulk_NGOs.append(unique_ngo)
        counter += 1
        print(f"{counter} of {total} done")
    UniqueNGO.objects.bulk_update(bulk_NGOs, ['gross_income', 'urls_scraped', 'domain'], batch_size=1000)
    return None


def merge_xml():
    """
    Special case for merging XMLNGO
    DO a search and rename the fields to match the field you want to merge
    E.g. This is for merging the gross_income field
    """
    xml_ngo = XMLNGO.objects.filter(
        Q(gross_income__isnull=False) &  ~Q(gross_income='')
        ).values_list('govt_reg_number', flat=True)
    empty_unique_ngos = UniqueNGO.objects.filter(
            Q(gross_income__isnull=True) | Q(gross_income="")
        ).values_list('govt_reg_number', flat=True)
    intersect_ein = set(xml_ngo).intersection(set(empty_unique_ngos))
    to_update = XMLNGO.objects.filter(govt_reg_number__in=intersect_ein, gross_income__isnull=False).order_by("-govt_reg_number","-domain").values_list(
        "govt_reg_number",
        "gross_income",
        "urls_scraped",
        "domain"
    )

    total = len(to_update)
    counter = 0
    bulk_NGOs = []
    last_ein = ""
    for x_data in to_update:
        if last_ein != x_data[0]:
            unique_ngo = UniqueNGO.objects.get(govt_reg_number=x_data[0])
            if not unique_ngo.gross_income:
                unique_ngo.gross_income = x_data[1]
                unique_ngo.urls_scraped = pipe_list(unique_ngo.urls_scraped, x_data[2])
                unique_ngo.domain = pipe_list(unique_ngo.domain, x_data[3])
                bulk_NGOs.append(unique_ngo)
        last_ein = x_data[0]
        counter += 1
        print(f"{counter} of {total} done") 
    UniqueNGO.objects.bulk_update(bulk_NGOs, ['gross_income', 'urls_scraped', 'domain'], batch_size=1000)
    return None
    
    
def merge_model():
    """
    Add the models you want to merge here
    Arrange them in the order you want to merge them
    """
    
    
    print("Merging CNavigator")
    merger(CNavNGO)
    print("Merging XMl")
    merge_xml()
    print("Merging GGI")
    merger(GGIndiaNGO)
    print("Merging GuidestarApp")
    merger(GStarNGO)
    print("Merging PledgeApp")
    merger(PledgeNGO)
    print("Merging 990N")
    merger(ZIP_NGO)
    print("Merging FCR")
    merger(FCR_NGO)
    
        
# def fix_null():
#     u = UniqueNGO.objects.filter(cause__isnull=True)
#     unknown_cause = ["11",]
#     cause = format_list(unknown_cause)
#     u.update(cause=cause)

# def fix_ein():
#     u = UniqueNGO.objects.annotate(ein_len=Length('govt_reg_number')).filter(~Q(ein_len=9), govt_reg_number_type="EIN")
#     u.update(govt_reg_number_type=None, govt_reg_number=None)
#     print("done")