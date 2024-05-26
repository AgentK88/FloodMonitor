points = {'N': 'North',
          'NNE': 'North North East',
          'NE': 'North East',
          'ENE': 'East North East',
          'E': 'East',
          'ESE': 'East South East',
          'SE': 'South East',
          'SSE': 'South South East',
          'S': 'South',
          'SSW': 'South South West',
          'SW': 'South West',
          'WSW': 'West South West',
          'W': 'West',
          'WNW': 'West North West',
          'NW': 'North West',
          'NNW': 'North North West'}

def compassPoint(Code):
    return points.get(Code, 'Unknown')

#print(compassPoint('NW'))