#!/usr/bin/env python
import csv
import numpy
import os
import progressbar
import requests
import sys

from matplotlib import pyplot
from matplotlib.ticker import ScalarFormatter

# Amount of time before/after TCE midtransit
BUFFERTIMES = (0.5, 1.5, 5)

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

    for input_row in bar(list(input_rows)):
        input_data = dict(zip(input_headers, input_row))

        lightcurve = requests.get(input_data['datalocation'])

        if lightcurve.status_code != 200:
            print "Warning: Could not download %s" % input_data['datalocation']
            continue

        lightcurve = lightcurve.json()

        userxmin = float(input_data['userxmin'])
        userxmax = float(input_data['userxmax'])
        userxmid = float(input_data['userxmid'])

        output_filename = input_data['datalocation'].split('/')[-1]
        output_filename = output_filename.replace('.json', '')
        output_filename = "%s-%s-%s.png" % (
            output_filename,
            userxmin,
            userxmax
        )

        fig, axes = pyplot.subplots(3, 1)
        fig.set_size_inches(10, 15.0)
        fig.subplots_adjust(right=0.98, top=0.98, left=0.1, bottom=0.04)

        yaxisformatter = ScalarFormatter(useOffset=False)

        alltime = numpy.array(lightcurve['x'])
        allflux = numpy.array(lightcurve['y'])

        for buffertime, ax in zip(BUFFERTIMES, axes):
            # Cutting out region of transit +/- buffertime
            time = 24.0 * (
                alltime[
                    numpy.where(
                        (alltime > (userxmin - buffertime)) &
                        (alltime < (userxmax + buffertime))
                    )
                ] - userxmid
            )

            if len(time) == 0:
                continue

            origflux = allflux[
                numpy.where(
                    (alltime > (userxmin - buffertime)) &
                    (alltime < (userxmax + buffertime))
                )
            ]

            # Normalizing fluxes to ~1.0
            flux = origflux / numpy.nanmedian(origflux)
            ax.plot(time, flux, marker='o', color='b', ls='-')

            # Plotting extra edge space in x-axis
            xlim = numpy.nanmax([
                abs(numpy.nanmin(time)), abs(numpy.nanmax(time))
            ]) + 2.0
            ax.set_xlim(-xlim, xlim)

            # Plotting extra edge space in y-axis
            ydiff = numpy.nanmax(flux) - numpy.nanmin(flux)
            ydifffactor = 0.05
            ylims = (
                numpy.nanmin(flux) - ydiff * ydifffactor,
                numpy.nanmax(flux) + ydiff * ydifffactor
            )
            ax.set_ylim(ylims)
            ax.yaxis.set_major_formatter(yaxisformatter)

            # Drawing vertical lines around transit
            normuserxmin = 24.0 * (userxmin - userxmid)
            normuserxmax = 24.0 * (userxmax - userxmid)

            ax.plot(
                [0, 0],
                ylims,
                marker='None',
                color='k',
                ls='--'
            )
            ax.plot(
                [normuserxmin, normuserxmin],
                ylims,
                marker='None',
                color='k',
                ls='-'
            )
            ax.plot(
                [normuserxmax, normuserxmax],
                ylims,
                marker='None',
                color='k',
                ls='-'
            )
            ax.set_ylabel('Normalized flux')
            ax.set_xlabel('Time (hours from midtransit)')

        # Writing figures or plotting
        fig.savefig(os.path.join(OUTPATH, output_filename))
        pyplot.close(fig)
