#!/usr/bin/env python
#   load_policy.py
#
import sys
import json
from pprint import pprint
import urllib2
import urllib
import requests
from collections import defaultdict

def ReadPolJSON():
    #filename = 'policy.json'
    filename = 'policy.json'

    pol_json = []
    #data = json.load(infile)
    with open(filename) as pol_file:
        pol_json = json.load(pol_file)

    return pol_json
         

    

def CreateQuote(pol_json):
    # Address, Applicant, 
    #  Create the quote with policy json body
    url = 'http://dcdemoappsrv1:8083/direct/quote'
    response = requests.post(url, data=json.dumps(pol_json))
    quote_auth_token = response.headers['quoteauthtoken']
    quote_json = json.loads(response.text)
    
    quote_stream_id = quote_json['streamId']
    quote_stream_rev = quote_json['streamRevision']
    print ('Stream ID: %s ' % quote_stream_id)
    print ('Stream Rev: %s' % quote_stream_rev)
    print ('Auth Token: %s' % quote_auth_token)
        
    # remove all vehicles
    veh_coll = []
    for veh in quote_json['events'][0]['quote']['vehicles']:
        veh_coll.append( veh['id'])
    url = 'http://dcdemoappsrv1:8083/direct/quote/%s/%s/vehicles' % (quote_stream_id, quote_stream_rev)
    payload = {'ids': json.dumps(veh_coll)}
    headers = {'quoteAuthToken': quote_auth_token}
    response = requests.delete(url, params=payload, headers=headers)
    quote_stream_rev =  quote_stream_rev + 1
    #print('vehicle delete response:')
    #print(response.text)
    print('vehicle delete response: %s' % response.status_code)
    
    # add vehicles from input json back on
    #  create json for coverages 
    coverage_input = {}
    vehicles = []
    coverages = []
    for vehicle in pol_json['vehicles']:
        #print('@@@@@@@@@@ Vehicle')
        vehicle_body = {}
        veh = {}
        veh['year'] = vehicle['year']
        veh['make'] = vehicle['make']
        veh['model'] = vehicle['model']
        veh['trim'] = vehicle['trim']
        veh['vin'] = vehicle['vin']
        veh['ownership'] = vehicle['ownership']
        veh['bussinessUse'] = vehicle['businessUse']
        if 'antiTheftDevice' in vehicle:
            veh['antiTheftDevice'] = vehicle['antiTheftDevice']
        #  write vehicle
        url = 'http://dcdemoappsrv1:8083/direct/quote/%s/%s/vehicle' % (quote_stream_id, quote_stream_rev)
        #print(veh)
        payload = json.dumps(veh)
        headers = {'quoteAuthToken': quote_auth_token}
        response = requests.post(url, data=payload, headers=headers)
        quote_stream_rev =  quote_stream_rev + 1
        print('Add vehicle status = %s' % response.status_code)
        #print(response.text)
        # read the response to get new vehicle id
        response_json = json.loads(response.text)
        vehicle_body['id'] = response_json['events'][0]['vehicle']['id']
        coverages = []
        for coverage in vehicle['coverages']:
            coverage_body = {}
            limits = []
            if coverage['type'] == 'RoadsideAssistance':
                continue
            else:
                for limit in coverage['limits']:
                    limit_body = {}
                    limit_body['type'] = limit['type']
                    limit_body['value'] = limit['value']
                    limits.append(limit_body)
    
            coverage_body['type'] = coverage['type']
            coverage_body['limits'] = limits
            coverages.append(coverage_body)
   
        vehicle_body['coverages'] = coverages
        #print('vehicle body')
        #print(vehicle_body)
        vehicles.append(vehicle_body)
        
    
    coverage_input['vehicles'] = vehicles
    #print('coverage_input = %s' % coverage_input)
    url = 'http://dcdemoappsrv1:8083/direct/quote/%s/%s/coverages' % (quote_stream_id, quote_stream_rev)
    payload = json.dumps(coverage_input)
    headers = {'quoteAuthToken': quote_auth_token}
    response = requests.put(url, data=payload, headers=headers)
    quote_stream_rev =  quote_stream_rev + 1
    #print (' ')
    #print(response.text)
    #print(response.url)
    print('Update Coverages status = %s' % response.status_code)
    print ('Stream Rev: %s' % quote_stream_rev)
    
    ##### clean up clients
    drivers_coll = []
    for driver in quote_json['events'][0]['quote']['drivers']:
        drivers_coll.append( driver['id'])
    url = 'http://dcdemoappsrv1:8083/direct/quote/%s/%s/drivers' % (quote_stream_id, quote_stream_rev)
    payload = {'ids': json.dumps(drivers_coll)}
    headers = {'quoteAuthToken': quote_auth_token}
    response = requests.delete(url, params=payload, headers=headers)
    quote_stream_rev =  quote_stream_rev + 1
    print('driver delete response:')
    print(response.text)
    print('driver delete response: %s' % response.status_code)
    
    # add drivers from input json back on
    #  create json for coverages 
    
    drivers = []
    
    for driver in pol_json['drivers']:
        print('@@@@@@@@@@ Driver')
        driver_body = {}
        
        driver_body['firstName'] = driver['firstName']
        driver_body['middleName'] = driver['middleName']
        driver_body['lastName'] = driver['lastName']
        driver_body['birthDate'] = driver['birthDate']
        driver_body['email'] = driver['email']
        driver_body['phoneNumber'] = driver['phoneNumber']
        driver_body['gender'] = driver['gender']
        driver_body['ssn'] = driver['ssn']
        driver_body['maritalStatus'] = driver['maritalStatus']
        #  write driver
        url = 'http://dcdemoappsrv1:8083/direct/quote/%s/%s/driver' % (quote_stream_id, quote_stream_rev)
        
        payload = json.dumps(driver_body)
        headers = {'quoteAuthToken': quote_auth_token}
        response = requests.post(url, data=payload, headers=headers)
        quote_stream_rev =  quote_stream_rev + 1
        print('Add driver status = %s' % response.status_code)
        print(response.text)

        url = 'http://dcdemoappsrv1:8083/direct/quote/%s/%s/rate' % (quote_stream_id, quote_stream_rev)
        headers = {'quoteAuthToken': quote_auth_token}
        data = urllib.urlencode(pol_json)
        response = requests.post(url, data=payload, headers=headers)
        print (' ')
        print(response.text)
        print(response.status_code)
        print(response.url)

'''    
def RateQuote(quote_stream_id, quote_stream_rev, quote_auth_token):
    url = 'http://dcdemoappsrv1:8083/direct/quote/%s/%s/rate' % (quote_stream_id, quote_stream_rev)
    headers = {'quoteAuthToken': quote_auth_token}
    data = urllib.urlencode(pol_json)
    response = requests.post(url, data=payload, headers=headers)
    print (' ')
    print(response.text)
    print(response.status_code)
    print(response.url)
'''    
def main():
   
   pol_json = ReadPolJSON()
   
   CreateQuote(pol_json)
   #Vehicle()
   #Driver()
   #NamedInsured()
   
   
   
   

      
# Start program
if __name__ == "__main__":
   main()
