def q_builder(result_size:int = 5, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    causes: ["Arts and culture", "Education", "Environment", "Health", "Technology", "Forensic science", "Public safety", "Public affairs", "Agriculture, fishing and forestry", "Religion", "Sports and recreation", "Human rights", "Human services", "International relations", "Unknown or not classified"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    results {{
                        ein
                        name
                        mission
                        organization_url
                        charity_navigator_url
                        cause
                        street
                        street2
                        city
                        state
                        zip
                        country
                    }}
                }}
            }}
        '''
    }


def get_full_region_name(short_name):
        states = {
            'AK': 'Alaska',
            'AL': 'Alabama',
            'AR': 'Arkansas',
            'AS': 'American Samoa',
            'AZ': 'Arizona',
            'CA': 'California',
            'CO': 'Colorado',
            'CT': 'Connecticut',
            'DC': 'District of Columbia',
            'DE': 'Delaware',
            'FL': 'Florida',
            'GA': 'Georgia',
            'GU': 'Guam',
            'HI': 'Hawaii',
            'IA': 'Iowa',
            'ID': 'Idaho',
            'IL': 'Illinois',
            'IN': 'Indiana',
            'KS': 'Kansas',
            'KY': 'Kentucky',
            'LA': 'Louisiana',
            'MA': 'Massachusetts',
            'MD': 'Maryland',
            'ME': 'Maine',
            'MI': 'Michigan',
            'MN': 'Minnesota',
            'MO': 'Missouri',
            'MP': 'Northern Mariana Islands',
            'MS': 'Mississippi',
            'MT': 'Montana',
            'NA': 'National',
            'NC': 'North Carolina',
            'ND': 'North Dakota',
            'NE': 'Nebraska',
            'NH': 'New Hampshire',
            'NJ': 'New Jersey',
            'NM': 'New Mexico',
            'NV': 'Nevada',
            'NY': 'New York',
            'OH': 'Ohio',
            'OK': 'Oklahoma',
            'OR': 'Oregon',
            'PA': 'Pennsylvania',
            'PR': 'Puerto Rico',
            'RI': 'Rhode Island',
            'SC': 'South Carolina',
            'SD': 'South Dakota',
            'TN': 'Tennessee',
            'TX': 'Texas',
            'UT': 'Utah',
            'VA': 'Virginia',
            'VI': 'Virgin Islands',
            'VT': 'Vermont',
            'WA': 'Washington',
            'WI': 'Wisconsin',
            'WV': 'West Virginia',
            'WY': 'Wyoming'
        }
        state_name = states.get(short_name.upper())
        return short_name.upper() if state_name is None else state_name