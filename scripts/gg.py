from global_giving.models import GlobalGivingNGO, NGO,GlobalGivingIndexedUrl

def copy_from_gg():
    """
    copy all the data from global giving to the main table
    """
    # use the bulk create method
    # get all the data from global giving
    print("Copying data from Global Giving to the main table")
    gg_data = GlobalGivingNGO.objects.all()
    # create a list of all the data
    all_data = []
    
    for data in gg_data:
        all_data.append(NGO(
            **{
                "organization_name": data.organization_name,
                "organization_address": data.organization_address,
                "country": data.country,
                "state": data.state,
                "cause": data.cause,
                "email": data.email,
                "phone": data.phone,
                "website": data.website,
                "mission": data.mission,
                "description": data.description,
                "govt_reg_number": data.govt_reg_number,
                "govt_reg_number_type": data.govt_reg_number_type,
                "registration_date_year": data.registration_date_year,
                "registration_date_month": data.registration_date_month,
                "registration_date_day": data.registration_date_day,
                "gross_income": data.gross_income,
                "image": data.image,
                "domain": data.domain,
                "urls_scraped": data.urls_scraped
            }
        ))

    NGO.objects.bulk_create(all_data, ignore_conflicts=True)
    print("Done")
    return
    

def unscrape():
    GlobalGivingIndexedUrl.objects.update(is_scraped=False, locked=False, trial=0)