#!/usr/bin/python

import xmlrpclib
import sys
import urllib2
import tldextract
import logging
logging.basicConfig()

def print_sync(string):
    sys.stdout.write(string)
    sys.stdout.flush()

if len(sys.argv) <= 1:
    print("Usage: " + sys.argv[0] + " subdomain API_KEY")
    sys.exit(1);

api = xmlrpclib.ServerProxy('https://rpc.gandi.net/xmlrpc/')

no_fetch_extract = tldextract.TLDExtract(suffix_list_url=False)
extract = no_fetch_extract(sys.argv[1])
domain = extract.domain + '.' + extract.suffix
subdomain = extract.subdomain

apikey = sys.argv[2]

print_sync("Get IP...")
ip = urllib2.urlopen('http://ip.42.pl/raw').read()
record_filter = {'type': 'A','name': subdomain}
new_record = record_filter.copy()
new_record['ttl'] = 600
new_record['value'] = ip
print(ip)

print("Get domain info")
domain_info = api.domain.info(apikey, domain)
zone_id = domain_info['zone_id']

print_sync("Get current record ip...")
current_record = api.domain.zone.record.list(apikey, zone_id, 0, record_filter)[0]
print(current_record['value'])

if ip == current_record['value']:
    print("No need update IP")
    sys.exit(1)

print_sync("Create new version...")
new_zone_ver = api.domain.zone.version.new(apikey, zone_id)
print(new_zone_ver)

print("Get new record list")
new_subdomain_record = api.domain.zone.record.list(apikey, zone_id, new_zone_ver, record_filter)[0]

print("Update record")
api.domain.zone.record.update(apikey, zone_id, new_zone_ver, {'id': new_subdomain_record['id']}, new_record)

print("Set new version")
api.domain.zone.version.set(apikey, zone_id, new_zone_ver)

print("Done!")
