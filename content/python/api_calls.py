import pandas as pd
import numpy as np
import warnings
import requests
import json
import pandas

def barrier_extent(barrier_type):

    request = 'https://cabd-pro.cwf-fcf.org/bcfishpass/functions/postgisftw.wcrp_barrier_extent/items.json?watershed_group_code=LNIC&barrier_type=' + barrier_type

    response_api = requests.get(request)
    parse = response_api.text
    result = json.loads(parse)
    
    result = [item for item in result if barrier_type in item['crossing_feature_type']]

    blocked_km = result[0]['all_habitat_blocked_km']
    blocked_pct = result[0]['extent_pct']

    return blocked_km, blocked_pct

def barrier_count(barrier_type):
    request = 'https://cabd-pro.cwf-fcf.org/bcfishpass/functions/postgisftw.wcrp_barrier_count/items.json?watershed_group_code=LNIC&barrier_type=' + barrier_type

    response_api = requests.get(request)
    parse = response_api.text
    result = json.loads(parse)
    
    result = [item for item in result if barrier_type == item['crossing_feature_type'] and item['status'] == 'HABITAT']

    n_passable = result[0]['n_passable']
    n_barrier = result[0]['n_barrier']
    n_potential = result[0]['n_potential']
    n_unknown = result[0]['n_unknown']

    sum_bar = (n_passable, n_barrier, n_potential, n_unknown)

    return n_passable, n_barrier, n_potential, n_unknown, sum(sum_bar)

def barrier_severity(barrier_type):

    request = 'https://cabd-pro.cwf-fcf.org/bcfishpass/functions/postgisftw.wcrp_barrier_severity/items.json?watershed_group_code=LNIC&barrier_type=' + barrier_type

    response_api = requests.get(request)
    parse = response_api.text
    result = json.loads(parse)
    
    result = [item for item in result if barrier_type in item['structure_type']]

    n_assessed_barrier = result[0]['n_assessed_barrier']
    n_assess_total = result[0]['n_assess_total']
    pct_assessed_barrier = result[0]['pct_assessed_barrier']

    return n_assessed_barrier, n_assess_total, pct_assessed_barrier

def watershed_connectivity(habitat_type):

    request = 'https://cabd-pro.cwf-fcf.org/bcfishpass/functions/postgisftw.wcrp_habitat_connectivity_status/items.json?watershed_group_code=LNIC&habitat_type=' + habitat_type

    response_api = requests.get(request)
    parse = response_api.text
    result = json.loads(parse)

    connect_stat = result[0]['connectivity_status']
    all_habitat = result[0]['all_habitat']
    all_habitat_acc = result[0]['all_habitat_accessible']

    return round(connect_stat), all_habitat, all_habitat_acc

def capitalize_and_clean_columns(df):

    #creates a mapping of the old column names to the new column names
    new_columns = {col: col.replace('_', ' ').title() for col in df.columns}
    # Rename the columns using the mapping
    df.rename(columns=new_columns, inplace=True)
    return df

def confirmed_barriers(rawDF):

        tableColumns = ['barrier_id', 'modelled_crossing_id', 'watercourse_name', 'road_name','structure_type', 'partial_passability',
                        'structure_owner','num_barriers_set','total_hab_gain_set',
                        'upstream_habitat_quality', 'estimated_cost_$', 'next_steps','reason', 'notes', 'supporting_links', 
                        'structure_list_status', 'priority']
        priorityDF = rawDF[tableColumns]
        
        queryColumn1 = 'structure_list_status'
        priorityDF.query(f'{queryColumn1}  == "Confirmed barrier" & priority !=  "Non-actionable" ', inplace = True)
        priorityDF = priorityDF.drop(columns=['structure_list_status', 'priority'])
        priorityDF.sort_values(by=['total_hab_gain_set'], ascending=False, inplace=True)

        priorityDF = capitalize_and_clean_columns(priorityDF)
        priorityDF.to_csv('data/confirmed_barriers.csv', index=False)
        return priorityDF
#grabs assessed data deficient structures
def assessedStrucDD(rawDF):

        tableColumns = ['barrier_id', 'modelled_crossing_id', 'watercourse_name', 'road_name', 'structure_type', 'structure_owner', 'barrier_status','partial_passability',
                            'assessment_type_completed','total_hab_gain_set','num_barriers_set','next_steps','notes','supporting_links',
                            'structure_list_status']
        priorityDF = rawDF[tableColumns]

        queryColumn1 = 'structure_list_status'
        priorityDF.query(f'{queryColumn1}  == "Assessed structure that remains data deficient" ', inplace = True)
        priorityDF = priorityDF.drop(columns=['structure_list_status'])
        priorityDF.sort_values(by=['total_hab_gain_set'], ascending=False, inplace=True)

        priorityDF = capitalize_and_clean_columns(priorityDF)
        priorityDF.to_csv('data/assessed_strucDD.csv', index=False)
        return priorityDF

#grabs rehabilitated structures
def RehabilitatedBarriers(rawDF):
    #To work on later

        tableColumns = ['barrier_id','modelled_crossing_id', 'watercourse_name', 'road_name','type_of_rehabilitation','rehabilitated_by',
                        'rehabilitated_date', 'total_hab_gain_set', 'actual_project_cost_$',
                            'next_steps', 'notes', 'supporting_links',
                            'structure_list_status']
        priorityDF = rawDF[tableColumns]

        queryColumn1 = 'structure_list_status'
        priorityDF.query(f'{queryColumn1}  == "Rehabilitated barrier" ', inplace = True)
        priorityDF = priorityDF.drop(columns=['structure_list_status'])
        priorityDF.sort_values(by=['total_hab_gain_set'], ascending=False, inplace=True)

        priorityDF = capitalize_and_clean_columns(priorityDF)
        priorityDF.to_csv('data/rehabilitated_barriers.csv', index=False)
        return priorityDF

#grabs non-actionable structures
def nonActionable_barriers(rawDF):

        tableColumns = ['barrier_id', 'modelled_crossing_id', 'watercourse_name', 'road_name','structure_type', 'reason', 'notes', 'supporting_links', 
                        'structure_list_status', 'priority']
        priorityDF = rawDF[tableColumns]
        
        queryColumn1 = 'structure_list_status'
        priorityDF.query(f'{queryColumn1}  == "Confirmed barrier" & priority ==  "Non-actionable" ', inplace = True)
        priorityDF = priorityDF.drop(columns=['structure_list_status', 'priority'])

        priorityDF = capitalize_and_clean_columns(priorityDF)
        priorityDF.to_csv('data/nonactionable_barriers.csv', index=False)
        return priorityDF

#grabs excluded strucutures
def ExcludedStructures(rawDF):

        tableColumns = ['barrier_id', 'modelled_crossing_id', 'watercourse_name', 'road_name','structure_type', 
                        'reason_for_exclusion', 'method_of_exclusion','reason', 'notes', 'supporting_links', 
                        'structure_list_status']
        priorityDF = rawDF[tableColumns]

        queryColumn1 = 'structure_list_status'
        priorityDF.query(f'{queryColumn1}  == "Excluded structure" ', inplace = True)
        priorityDF = priorityDF.drop(columns=['structure_list_status'])

        priorityDF = capitalize_and_clean_columns(priorityDF)
        priorityDF.to_csv('data/excluded_structures.csv', index=False)
        return priorityDF

def GetTrackingTableData():
    request = "https://cabd-pro.cwf-fcf.org/bcfishpass/collections/wcrp_lnic.combined_tracking_table_crossings_wcrp_vw_lnic/items.json" 
    response_api = requests.get(request)
    parse = response_api.text
    result = json.loads(parse)
    data = result["features"]
    df = pd.json_normalize(data, sep="_")
    df.columns = [col.replace("properties_", "") for col in df.columns]
    #print (df.head())
    return df


warnings.filterwarnings('ignore')

connect = watershed_connectivity("ALL")[0]
total = watershed_connectivity("ALL")[1] #total km in LNIC
access = watershed_connectivity("ALL")[2]
gain = round((total*0.96)-access,2)

connect_spawn = watershed_connectivity("SPAWNING")[0]
total_spawn = watershed_connectivity("SPAWNING")[1] #total km in LNIC
access_spawn = watershed_connectivity("SPAWNING")[2]
gain_spawn = round((total_spawn*0.96)-access_spawn,2)

connect_rear = round(watershed_connectivity("REARING")[0],2)
total_rear = round(watershed_connectivity("REARING")[1],2) #total km in LNIC
access_rear = round(watershed_connectivity("REARING")[2],2)
gain_rear = round((total_rear*0.96)-access_rear,2)

df = GetTrackingTableData()
confirmed_struc = confirmed_barriers(df)

add_struc = assessedStrucDD(df)
excluded_struc = ExcludedStructures(df)
nonaction_struc = nonActionable_barriers(df)
rehabilitated_struc = RehabilitatedBarriers(df)

count_addStruc = len(add_struc)
count_excludedStruc = len(excluded_struc)
count_nonactionStruc = len(nonaction_struc)
count_rehabilitatedStruc = len(rehabilitated_struc)

