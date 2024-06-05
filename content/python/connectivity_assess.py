import warnings
import pandas as pd
import numpy as np

warnings.filterwarnings('ignore')


def make_assess_table(species, kea, indicator, poor_upper, fair_upper, good_upper, api_call):
  """ builds the pandas table for connectivity status assessment
  :species:     target species
  :kea:         KEA eg. Accessible Spawning Habitat
  :indicator:   indicator for assessment eg. % of total spawning habitat
  :poor_upper:  upper bound for poor range
  :fair_upper:  upper bound for fair range
  :good_upper:  upper bound for good range
  :api_call:    one of api.connect, api.connect_spawn, api.connect_rear
  
  Note that very good will be inferred from good_upper
  
  """
  if poor_upper == "?":
    poor_bounds_str = "?"
  else:
    poor_bounds_str = "<"+str(poor_upper)+"%"
   # exception if a cell needs to be blank
  if fair_upper == -1:
    fair_bounds_str = "-"
    fair_upper = poor_upper
  elif fair_upper == " ?":
    fair_bounds_str = " ?"
  else:
    fair_bounds_str = str(poor_upper+1)+"-"+str(fair_upper)+"%"
  if good_upper == "? ":
    good_bounds_str = "? "
    very_good_bounds_str = " ? "
  else:
    good_bounds_str = str(fair_upper+1)+"-"+str(good_upper)+"%"
    very_good_bounds_str = ">"+str(good_upper)+"%"
    
  df = pd.DataFrame({"Target Species":[str(species)," "],
                   "KEA":[str(kea)," "],
                   "Indicator":[str(indicator),"Current Status:"],
                   "Poor":[poor_bounds_str," "],
                   "Fair":[fair_bounds_str," "],
                   "Good":[good_bounds_str, " "],
                   "Very Good":[very_good_bounds_str," "] 
                   })
                   

  if poor_upper != "?":               
    if api_call < poor_upper:
      df["Poor"][1] = str(api_call)
    elif api_call < fair_upper:
      df["Fair"][1] = str(api_call)
    elif api_call < good_upper:
      df["Good"][1] = str(api_call)
    else:
      df["Very Good"][1] = str(api_call)
  
    
  def colour_table(val):
    red = '#ff0000;'
    yellow = '#ffff00;'
    lgreen = '#92d050;'
    dgreen = '#03853e;'
    
  
    if val == poor_bounds_str : color = red
    elif val.isdigit() and int(val) < poor_upper : color = red
    elif val == fair_bounds_str : color = yellow
    elif val.isdigit() and (int(val) > poor_upper and int(val) < fair_upper) : color = yellow 
    elif val == good_bounds_str  : color = lgreen
    elif val.isdigit() and (int(val) > fair_upper and int(val) < good_upper) : color = lgreen 
    elif val == very_good_bounds_str: color = dgreen
    elif val.isdigit() and int(val) > good_upper : color = dgreen 
    elif val == "Current Status:" : return "font-weight: bold"
    else: color = 'white'
    
    return 'background-color: %s' % color
  
  return df.style.applymap(colour_table).set_table_styles(
   [{
       'selector': 'th',
       'props': [('background-color', '#008270'),('text-align', 'left')]
   }]).hide()
