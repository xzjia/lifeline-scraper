import billboard
import json
import datetime


decades = [1995, 1990, 1985, 1980, 1975, 1970, 1965, 1960, 1955, 1950]
for decade in decades:
    print(decade)
    # decade = 2000
    chart = billboard.ChartData('hot-100', str(decade+4) + "-12-25")
    data = []
    dtPreviousDate = datetime.datetime.strptime(chart.previousDate, '%Y-%m-%d')

    while dtPreviousDate > datetime.datetime(decade, 1, 1):
        print(chart.previousDate)
        dtPreviousDate = datetime.datetime.strptime(
            chart.previousDate, '%Y-%m-%d')
        data.append(json.loads((chart.json())))
        chart = billboard.ChartData('hot-100', chart.previousDate)

    with open('data_' + str(decade) + '.json', 'w') as outfile:
        json.dump(data, outfile, indent=2)
