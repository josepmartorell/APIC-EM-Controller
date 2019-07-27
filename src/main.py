#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# Let's import the environment mouler for the APIC-EM REST API:
# JSON encoder and decoder module, requests module used to send REST requests to API.
import json
import time
import requests
from tabulate import *

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()
# Variable to be used as a global variable inside functions
path_data = ''


class Controller:

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
        service_ticket = response_json["response"]["serviceTicket"]

        # display service ticket value to check return value
        print("The service ticket number is: ", service_ticket)

        # return the service ticket value to the program that calls the function
        return service_ticket

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

    # PATH-TRACE API URL
    def print_path(self):

        response_json = 0
        # Setup the environment and variables required to interact with the APIC-EM
        global path_data
        api_url = "https://SandBoxAPICEM.cisco.com/api/v1/flow-analysis"

        ticket = self.get_ticket()
        headers = {
            "content-type": "application/json",
            "X-Auth-Token": ticket
        }

        # Get the source and destination IP addresses for the Path Trace:
        while True:

            s_ip = input("Please enter the source host IP address for the path trace: ")
            d_ip = input("Please enter the destination host IP address for the path trace: ")

            if s_ip != "" or d_ip != "":

                path_data = {
                    "sourceIP": s_ip,
                    "destIP": d_ip
                }
                print("Source IP address is: ", path_data["sourceIP"])
                print("Destination IP address is: ", path_data["destIP"])
                break
            else:
                print("\n\nYOU MUST ENTER IP ADDRESSES TO CONTINUE.\nUSE CTRL-C TO QUIT\n")
                continue

        # Initiate the Path Trace and get the flowAnalysisId
        path = json.dumps(path_data)
        resp = requests.post(api_url, path, headers=headers, verify=False)
        resp_json = resp.json()
        flow_analysis_id = resp_json["response"]["flowAnalysisId"]
        print("FLOW ANALYSIS ID: ", flow_analysis_id)

        # Check status of Path Trace request, output results when COMPLETED
        check_url = api_url + "/" + flow_analysis_id
        status = ""
        checks = 1

        while status != "COMPLETED":

            r = requests.get(check_url, headers=headers, verify=False)
            response_json = r.json()
            status = response_json["response"]["request"]["status"]
            print("REQUEST STATUS: ", status)
            time.sleep(1)

            if checks == 15:
                raise Exception("Number of status checks exceeds limit. Possible problem with Path Trace.!")
            elif status == "FAILED":
                raise Exception("Problem with Path Trace - FAILED!")
            checks += 1

        # Display results
        path_source = response_json["response"]["request"]["sourceIP"]

        path_dest = response_json["response"]["request"]["destIP"]

        network_elements_info = response_json["response"]["networkElementsInfo"]

        all_devices = []
        device_no = 1

        for networkElement in network_elements_info:

            if "name" not in networkElement:
                name = "Unnamed Host"
                ip = networkElement["ip"]
                egress_interface_name = "UNKNOWN"
                ingress_interface_name = "UNKNOWN"

            else:
                name = networkElement["name"]
                ip = networkElement["ip"]
                if "egressInterface" in networkElement:
                    egress_interface_name = networkElement["egressInterface"]["physicalInterface"]["name"]
                else:
                    egress_interface_name = "UNKNOWN"

                if "ingressInterface" in networkElement:
                    ingress_interface_name = networkElement["ingressInterface"]["physicalInterface"]["name"]
                else:
                    ingress_interface_name = "UNKNOWN"

            device = [
                device_no,
                name,
                ip,
                ingress_interface_name,
                egress_interface_name
            ]
            all_devices.append(device)
            device_no += 1

        print("Path trace: \n Source: ", path_source, "\n Destination: ", path_dest)

        print("List of devices on path:")
        table_header = [
            "Item",
            "Name",
            "IP",
            "Ingress Int",
            "Egress Int"
        ]
        print(tabulate(all_devices, table_header))


# Creates an object to display the dictionaries deployed by the methods


api = "https://SandBoxAPICEM.cisco.com/api/v1/ticket"  # change this if using a different APIC-EM sandbox
display = Controller(api)
display.print_hosts()
display.print_devices()
display.print_path()
