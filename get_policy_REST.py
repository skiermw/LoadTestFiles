#!/usr/bin/env python
#   get_policy.py
#
import sys
import json
from pprint import pprint
import urllib2



filename = 'policy.json'
outfile = open(filename, 'w')

url = 'http://dcdemoappsrv1:8081/direct/policy?policyNumber=000000011&everything=true&discounts=true&coverages=true&vehicles=true&nonDescribedVehicle=true&applicant=true&drivers=true&namedInsureds=true&additionalListedInsureds=true'
response = urllib2.urlopen(url).read()

print 'error: %s' % urllib2.URLError
#print repr(response)
#print response

data = json.loads(response)

#print json.dumps(data, sort_keys=True, indent=4, separators=(',', ':'))



outfile.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ':')))

outfile.close()

