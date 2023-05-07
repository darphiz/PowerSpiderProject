result_size = 15

def q_builder(cause:str, state:str,  page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    causes: ["{cause}"], 
                    states: ["{state}"]
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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



def cause_only_builder(cause:str, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    causes: ["{cause}"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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
    
def state_only_builder(state:str, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    states: ["{state}"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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

def beacon_only_builder(beacon:str, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    beacons: ["{beacon}"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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

def ratings_only_builder(rating:str, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    ratings: ["{rating}"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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
    
def state_beacon_builder(state:str, beacon:str, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    states: ["{state}"], 
                    beacons: ["{beacon}"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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
    
def state_ratings_builder(state:str, rating:str, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    states: ["{state}"], 
                    ratings: ["{rating}"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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
    
def cause_beacon_builder(cause:str, beacon:str, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    causes: ["{cause}"], 
                    beacons: ["{beacon}"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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
    
def cause_ratings_builder(cause:str, rating:str, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    causes: ["{cause}"], 
                    ratings: ["{rating}"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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
    
def beacon_ratings_builder(beacon:str, rating:str, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    beacons: ["{beacon}"], 
                    ratings: ["{rating}"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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
def state_cause_beacon_builder(state:str, cause:str, beacon:str, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    states: ["{state}"], 
                    causes: ["{cause}"], 
                    beacons: ["{beacon}"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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

def state_cause_ratings_builder(state:str, cause:str, rating:str, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    states: ["{state}"], 
                    causes: ["{cause}"], 
                    ratings: ["{rating}"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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
    
def state_beacon_ratings_builder(state:str, beacon:str, rating:str, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    states: ["{state}"], 
                    beacons: ["{beacon}"], 
                    ratings: ["{rating}"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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
    
def cause_beacon_ratings_builder(cause:str, beacon:str, rating:str, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    causes: ["{cause}"], 
                    beacons: ["{beacon}"], 
                    ratings: ["{rating}"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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

def state_cause_beacon_ratings_builder(state:str, cause:str, beacon:str, rating:str, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    states: ["{state}"], 
                    causes: ["{cause}"], 
                    beacons: ["{beacon}"], 
                    ratings: ["{rating}"], 
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
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