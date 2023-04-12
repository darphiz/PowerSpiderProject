from django.shortcuts import render
from django.views import View
from irs_app.models import NGO_V2, ZIP_NGO
from pledge_app.models import NGO as Pledge_NGO
from fcra_app.models import FCR_NGO
from guidestar_app.models import NGO as GuideStar_NGO
from global_giving.models import GlobalGivingNGO
from global_giving_india.models import NGO as GGIndiaNGO
from c_navigator.models import NGO as CNavNGO

class SummaryView(View):
    def get(self, request, *args, **kwargs):
        irs_xml = {
            "total": NGO_V2.objects.count(),
            "Name": "IRS XML",
            "status": "Approved"
        } 
        irs_zip = {
            "total": ZIP_NGO.objects.count(),
            "Name": "IRS ZIP",
            "status": "Approved"
        }
        
        pledge = {
            "total": Pledge_NGO.objects.count(),
            "Name": "Pledge App",
            "status": "Running"
        }
        
        fcra_app = {
            "total": FCR_NGO.objects.count(),
            "Name": "FCRA App",
            "status": "Approved"
        }
        
        guide_star = {
            "total": GuideStar_NGO.objects.count(),
            "Name": "GuideStar App",
            "status": "Running"
        }

        global_giving = {
            "total": GlobalGivingNGO.objects.count(),
            "Name": "Global Giving",
            "status": "Approved"
        }
        
        gg_india = {
            "total": GGIndiaNGO.objects.count(),
            "Name": "Guidestar India",
            "status": "Approved"
        }
        
        c_nav = {
            "total": CNavNGO.objects.count(),
            "Name": "Charity Navigator",
            "status": "Running"
        }
        
        
        
        data = [pledge, c_nav, guide_star, global_giving, irs_xml, irs_zip,fcra_app,gg_india]
        
        total = sum([i["total"] for i in data])
        expected = 5000000
        
        percentage = int((total/expected)*100)
        
        return render(request, 'index.html', {
            "apps": data,
            "total": total,
            "percentage": percentage,
        })