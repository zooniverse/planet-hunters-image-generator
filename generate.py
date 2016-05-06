#!/usr/bin/env python
import csv
import os
import progressbar
import requests
import sys

from matplotlib import pyplot

OUTPATH = os.environ.get('OUTPATH', os.path.join('/', 'out'))

try:
    INPUT_FILE_LIST = sys.argv[1]
except IndexError:
    print "Please specify the name of the file containing lightcurve URLs"
    sys.exit(1)

with open(INPUT_FILE_LIST) as input_files_f:
    input_rows = csv.reader(input_files_f, delimiter=' ')
    input_headers = input_rows.next()
    bar = progressbar.ProgressBar(redirect_stdout=True)

    for input_row in bar(input_rows):
        input_data = dict(zip(input_headers, input_row))

        lightcurve = requests.get(input_data['datalocation'])

        if lightcurve.status_code != 200:
            print "Warning: Could not download %s" % input_data['datalocation']
            continue

        lightcurve = lightcurve.json()

        userxmin = float(input_data['userxmin'])
        userxmax = float(input_data['userxmax'])

        output_filename = input_data['datalocation'].split('/')[-1]
        output_filename = output_filename.replace('.json', '')
        output_filename = "%s-%s-%s.png" % (
            output_filename,
            userxmin,
            userxmax
        )

        sliced_lightcurve = {
            'x': [],
            'y': [],
        }

        for i, x in enumerate(lightcurve['x']):
            # Assumes the data is sorted by x
            if x < userxmin:
                continue
            if x > userxmax:
                break
            sliced_lightcurve['x'].append(x)
            sliced_lightcurve['y'].append(lightcurve['y'][i])

        pyplot.plot(sliced_lightcurve['x'], sliced_lightcurve['y'])
        pyplot.savefig(os.path.join(OUTPATH, output_filename))
        pyplot.close()
