# -*- coding: utf-8 -*-
from suds.client import Client
from suds.transport.http import HttpAuthenticated
from suds.sudsobject import asdict
import collections
import json


class ParlayXClient:
    """Suds Client for ParlayX SOAP communication

    Attributes:
        wsdl: wsdl path.
        username: Username for basic authentication.
        password: Password for basic authentication.
        faults: Default value is False.
    """

    def __init__(self, wsdl, location, username, password, faults=False):
        """
            Initialize authenticated Suds Client object for ParlayX communication.

        :param wsdl:
        :param location:
        :param username:
        :param password:
        :param faults:
        """

        self.wsdl = wsdl
        self.location = location
        self.faults = faults

        # Basic Authentication
        transport_auth = HttpAuthenticated(username=username, password=password)

        # Make Suds Client
        self.client = Client(url=wsdl, location=location, transport=transport_auth, faults=self.faults)

    def send_sms(self, phone_numbers, sender, price, message):
        """
            Send SMS.

        :param phone_numbers:
        :param sender:
        :param price:
        :param message:
        :return: SMS reference id.
        """

        array_eui = self.array_of_end_user_identifier(phone_numbers)
        response = self.client.service.sendSms(array_eui, sender, price, message)
        return response

    def array_of_end_user_identifier(self, phone_numbers):
        """
        Convert list of phone numbers into ParlayX ArrayOfEndUserIdentifier

        :param phone_numbers: List of phone numbers. Should be in e_164 format
        :return: ParlayX ArrayOfEndUserIdentifier
        """

        # array_eui = self.client.factory.create('ns1:ArrayOfEndUserIdentifier')
        array_eui = []
        for phone in phone_numbers:
            eui = self.client.factory.create('ns1:EndUserIdentifier')
            eui.value = ''.join(['tel:', phone])
            array_eui.append(eui)

        return array_eui

    @staticmethod
    def parse_delivery_notification(data):
        """

        :param data: SOAP ParlayX Body
        :return: Request converted to json
        """
        data_json = json.dumps(recursive_asdict(data))

        return data_json

    @staticmethod
    def send_reception_response():
        response = collections.namedtuple('SoapResponse', [ 'status', 'content', 'content_type', 'content_length'])

        content = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:tns="http://www.csapi. org/wsdl/parlayx/sms/v1_0/notification" xmlns:types="http://www.csapi.org/wsdl/parlayx/sms/v1_0/notification/encodedTypes" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body soap:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><q1:notifySmsReceptionResponse xmlns:q1="http://www.csapi.org/wsdl/parlayx/sms" /></soap:Body></soap:Envelope>"""
        content_type = 'text/xml'
        content_length = str(len(content))
        status = 200

        return response(status, content, content_type, content_length)


def recursive_asdict(d):
        """Convert Suds object into serializable format."""
        out = {}
        for k, v in asdict(d).iteritems():
            if hasattr(v, '__keylist__'):
                out[k] = recursive_asdict(v)
            elif isinstance(v, list):
                out[k] = []
                for item in v:
                    if hasattr(item, '__keylist__'):
                        out[k].append(recursive_asdict(item))
                    else:
                        out[k].append(item)
            else:
                out[k] = v
        return out
