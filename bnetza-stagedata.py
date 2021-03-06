#!/usr/bin/env ipython
# -*- coding: utf8 -*-
import pandas as pd
import numpy as np
import argparse
import os
# pip install progressbar2
import progressbar as pb

cmd_parser = argparse.ArgumentParser()
cmd_parser.add_argument("datadir", help="directory containing the *.xlsx files")
cmd_parser.add_argument("outfile", help="pickle/.pkl file to create")
args = cmd_parser.parse_args()

print "Slurping data from %s, writing to %s" % (args.datadir,
    args.outfile)
files = sorted(os.listdir(args.datadir))

print "Loading datasets. This might take a while."
alldata = None
with pb.ProgressBar(maxval=len(files)) as progress:
  for idx, file in enumerate(files):
    xl = pd.ExcelFile( os.path.join(args.datadir, file))
    newdata = xl.parse(0)
    if idx == 0:
      alldata = newdata
    else:
      alldata = alldata.append(newdata, ignore_index=True)
    progress.update(idx)
print "Finished reading data into memory."

print "Data cleanup:"
# http://stackoverflow.com/a/17335754
# Rename columns using df.columns = ['W','X','Y','Z']
print "(1) cast types to fix broken data"
alldata[['Beginn']] = pd.to_datetime(alldata['Beginn'], format="%Y-%m-%d %H:%M:%S.%f")

# trafo columns are broken - set type manually. After loading the
# datasets the column data is represented as a unicode string or a
# datetime object. The unicode string can be converted to a float - the
# datetime will be replaced by NaN.
def float_or_nan(value):
  if type(value) is not type(u"foo"):
    return np.nan
  else:
    return np.float(value)
alldata['ntrafo'] = alldata['ntrafo'].apply(lambda val: float_or_nan(val))
alldata['ntrafo_produkt'] = alldata['ntrafo_produkt'].apply(lambda val: float_or_nan(val))
alldata['ktrafo'] = alldata['ktrafo'].apply(lambda val: float_or_nan(val))
alldata['ktrafo_produkt'] = alldata['ktrafo_produkt'].apply(lambda val: float_or_nan(val))

#alldata['ntrafo'] = alldata['ntrafo'].astype(np.float)
#alldata['ntrafo_produkt'] = alldata['ntrafo_produkt'].astype(np.float)
#alldata['ktrafo'] = alldata['ktrafo'].astype(np.float)
#alldata['ktrafo_produkt'] = alldata['ktrafo_produkt'].astype(np.float)

print "(2) Clean label for Netzebene"
def label_netzebene(row):
  if row[u'HöS'] == 1:
    return u"HoeS"
  if row[u'HS'] == 1:
    return u"HS"
  if row[u'MS'] == 1:
    return u"MS"
  if row[u'NS'] == 1:
    return u"NS"
alldata['Netzebene'] = alldata.apply(lambda row: label_netzebene(row),
    axis=1)

print "(3) Forcing category datatype for some columns"
for col in ['Art', 'Anlass', 'Netzebene']:
  alldata[col] = alldata[col].astype('category')

print "(4) Generiere einheitliche Versorger-ID (VID)"
# Die lft. Nr. wurde in den einzelnen Dateien verschieden geschrieben.
# Sie repräsentiert je einen Netzbetreiber. Dieser Index kann
# zusammengefasst werden.
# See http://stackoverflow.com/a/10972557
alldata['VID'] = pd.concat([alldata['lft. Nr'].dropna(), 
  alldata['lft. Nr.'].dropna(), alldata['lft.Nr.'].dropna()]).reindex_like(alldata)
alldata['VID'] = alldata['VID'].astype(np.int64)


print alldata.head()
print alldata.dtypes

print "Writing output file"
alldata.to_pickle(args.outfile)




