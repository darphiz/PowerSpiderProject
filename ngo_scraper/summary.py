from django.shortcuts import render
from django.views import View
from irs_app.models import NGO_V2, ZIP_NGO
from pledge_app.models import NGO as Pledge_NGO
from fcra_app.models import FCR_NGO
from guidestar_app.models import NGO as GuideStar_NGO
from global_giving.models import NGO as GlobalGivingNGO
from global_giving_india.models import NGO as GGIndiaNGO
from c_navigator.models import NGO as CNavNGO
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@method_decorator(cache_page(60 * 2), name='dispatch')
class SummaryView(View):


    def get(self, request, *args, **kwargs):
        irs_xml = {
            # "total": NGO_V2.objects.count(),
            "total": 2290886,
            "Name": "IRS XML",
            "status": "Approved"
        } 
        irs_zip = {
            "total": 854801,
            # "total": ZIP_NGO.objects.count(),
            "Name": "IRS ZIP",
            "status": "Approved"
        }
        
        pledge = {
            "total": Pledge_NGO.objects.count(),
            "Name": "Pledge App",
            "status": "Awaiting Approval"
        }
        
        fcra_app = {
            "total": 3399,
            # "total": FCR_NGO.objects.count(),
            "Name": "FCRA App",
            "status": "Approved"
        }
        
        guide_star = {
            "total": GuideStar_NGO.objects.count(),
            "Name": "GuideStar App",
            "status": "Action Required"
        }

        global_giving = {
            "total": GlobalGivingNGO.objects.count(),
            # "total": 3408,
            "Name": "Global Giving",
            "status": "Approved"
        }
        
        gg_india = {
            # "total": GGIndiaNGO.objects.count(),
            "total": 1964,
            "Name": "Guidestar India",
            "status": "Approved"
        }
        
        c_nav = {
            "total": CNavNGO.objects.count(),
            "Name": "Charity Navigator",
            "status": "Awaiting Approval"
        }
        
        
        
        data = [pledge, c_nav, guide_star, global_giving, irs_xml, irs_zip,fcra_app,gg_india]
        
        total = sum([i["total"] for i in data])
        expected = 6000000
        
        percentage = int((total/expected)*100)
        
        return render(request, 'index.html', {
            "apps": data,
            "total": total,
            "percentage": percentage,
        })