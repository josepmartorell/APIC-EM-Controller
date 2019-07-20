#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# Let's import the environment mouler for the APIC-EM REST API:
# JSON encoder and decoder module, requests module used to send REST requests to API.
import json
import requests
from tabulate import *

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

class   ciscoApicEm:

    def __init__(self, api_url):
        # api_url = "https://{YOUR-APICEM}.cisco.com/api/v1/ticket"
        self.api_url = api_url

    # TICKET API URL
    def get_ticket(self):


        # Notice that all APIC-EM Rest APIs request and response content json type :)
        headers = {
            "content-type": "application/json"
        }

        body_json = {
            "username": "devnetuser",  # don't forget to change this if using a different APIC-EM sandbox
            "password": "Cisco123!"  # don't forget to change this if using a different APIC-EM sandbox
        }

        # Store the request's response in the variable "resp"
        resp = requests.post(self.api_url, json.dumps(body_json), headers=headers, verify=False)

        # Create the object "response_json" with the converted json-formatted response
        response_json = resp.json()

        # parse data for service ticket and display service ticket value
        serviceTicket = response_json["response"]["serviceTicket"]

        # display service ticket value to check return value
        print("The service ticket number is: ", serviceTicket)

        # return the service ticket value to the program that calls the function
        return serviceTicket

        # HOST API URL
    def print_hosts(self):

        api_url = "https://SandBoxAPICEM.cisco.com/api/v1/host"

        # Notice that all APIC-EM Rest APIs request and response content json type :)
        ticket = self.get_ticket()
        headers = {
            "content-type": "application/json",
            "X-Auth-Token": ticket
        }

        resp = requests.get(api_url, headers=headers, verify=False)
        # Display the http request status
        print("Status of /host request: ", resp.status_code)
        # Check if the request status was OK
        if resp.status_code != 200:
            raise Exception("Status code does not equal 200. Response text: " + resp.text)
        # Convert the JSON response data into a Python dictionary format
        response_json = resp.json()

        # Now create a list of host info to be held in host_list
        host_list = []
        i = 0
        for item in response_json["response"]:
            i += 1
            host = [
                i,
                item["hostType"],
                item["hostIp"]
            ]
            host_list.append(host)

        table_header = [
            "Number",
            "Type",
            "IP"
        ]
        print(tabulate(host_list, table_header))

    # NETWORK-DEVICE API URL
    def print_devices(self):

        # api_url = "https://{YOUR-APICEM}.cisco.com/api/v1/network-device"
        api_url = "https://SandBoxAPICEM.cisco.com/api/v1/network-device"

        # Setup API request headers.
        ticket = self.get_ticket()
        headers = {
            "content-type": "application/json",
            "X-Auth-Token": ticket
        }

        resp = requests.get(api_url, headers=headers, verify=False)
        print("Status of GET /network-device request: ", resp.status_code)  # This is the http request status
        # Check if the request status was OK
        if resp.status_code != 200:
            raise Exception("Status code does not equal 200. Response text: " + resp.text)
        # Get the json-encoded content from response
        response_json = resp.json()

        # Now create a list of host summary info
        device_list = []
        i = 0
        for item in response_json["response"]:
            i += 1
            device = [
                i,
                item["type"],
                item["managementIpAddress"]
            ]
            device_list.append(device)

        table_header = [
            "Number",
            "Type",
            "IP"
        ]
        print(tabulate(device_list, table_header))


# Creates an object to display the dictionaries deployed by the methods
api = "https://SandBoxAPICEM.cisco.com/api/v1/ticket"  # change this if using a different APIC-EM sandbox
display = ciscoApicEm(api)
print(display.get_ticket())
display.print_hosts()
display.print_devices()

