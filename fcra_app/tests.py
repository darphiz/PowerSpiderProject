from .models import FCR_Cursor

def generate_state_year_list(states):
    state_year_list = []
    for state in states:
        for year in range(2023, 2011, -1):
            state_year_list.append({"name": state[0], "id": state[1], "year": str(year)})
    return state_year_list

states = [    ("Andaman & Nicobar Islands", "24"), 
    ("Andhra Pradesh", "01"), 
    ("Arunachal Pradesh", "31"), 
    ("Assam", "02"), 
    ("Bihar", "03"), 
    ("Chandigarh", "29"), 
    ("Chhattisgarh", "32"), 
    ("Dadra & Nagar Haveli", "26"), 
    ("Daman and Diu", "35"), 
    ("Delhi", "23"), 
    ("Goa", "27"), 
    ("Gujarat", "04"), 
    ("Haryana", "17"), 
    ("Himachal Pradesh", "18"), 
    ("Jammu & Kashmir", "15"), 
    ("Jharkhand", "33"), 
    ("Karnataka", "09"), 
    ("Kerala", "05"), 
    ("Lakshwadeep", "25"), 
    ("Madhya Pradesh", "06"), 
    ("Maharashtra", "08"), 
    ("Manipur", "19"), 
    ("Meghalaya", "21"), 
    ("Mizoram", "30"), 
    ("Nagaland", "16"), 
    ("Orissa", "10"), 
    ("Pondicherry", "28"), 
    ("Punjab", "11"), 
    ("Rajasthan", "12"), 
    ("Sikkim", "22"), 
    ("Tamil Nadu", "07"), 
    ("Telangana", "36"), 
    ("Tripura", "20"), 
    ("Uttar Pradesh", "13"), 
    ("Uttarakhand", "34"), 
    ("West Bengal", "14")]

def bump():
    data = generate_state_year_list(states)
    for d in data:
        print("dumping ....")
        FCR_Cursor.objects.create(
            state = d["name"],
            state_id = d["id"],
            year=d["year"]
        )
        
    return "done"