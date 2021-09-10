import boto3
import os
import uuid
import base64
from reportlab.pdfgen.canvas import Canvas
from printnodeapi import Gateway
import json


def lambda_handler(event, context):
    printer_channel = PrinterChannel(event)
    printer_channel.submit()

class PrinterChannel(object):
    def __init__(self, event):
        self._companydata = {
            "name": os.environ.get("COMPANY_NAME", ''),
            "address": os.environ.get("COMPANY_ADDRESS", ''),
            "city": os.environ.get("COMPANY_CITY", ''),
            "postcode": os.environ.get("COMPANY_POSTCODE", ''),
            "number": os.environ.get("COMPANY_NUMBER", ''),
        }
        self._event = event
        try:
            self._api_key = os.environ['PRINTNODE_API_KEY']
        except KeyError:
            raise MissingEnvironmentVariableError(name='PRINTNODE_API_KEY')
        self._setup_printer()
        

    def submit(self):
        for endpoint in self._event['Endpoints'].values(): 
            userdata = {
                "address": endpoint['Address'],
                    "name": '{} {}'.format(endpoint['Attributes']['FirstName'],
                                       endpoint['Attributes']['LastName'])
            }
            pdf_file = self._create_sample_pdf(userdata)
            if os.environ.get("PRINT_ENABLED", True):
                print_job = self._submit_print_job(pdf_file, userdata)
                print(print_job)
        return
    
    def _setup_printer(self):
        # Setup printers
        self._gateway=Gateway(url='https://api.printnode.com',apikey=self._api_key)
        try:
            self._default_printer = [p for p in self._gateway.printers() if p.default][0]
        except IndexError:
            print("No default printer found")
            self._gateway = None
            self._default_printer = None

    def _submit_print_job(self, pdf_file, userdata):
        with open(pdf_file, "rb") as pdf_file:
            pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        response = self._gateway.PrintJob(
            printer=self._default_printer.id,
            base64=pdf_base64)
        result = {
            "job_id": response.id,
            "job_timestamp": response.create_timestamp,
            "printer_id": response.printer.id,
            "printer_name": response.printer.name,
            "computer_id": response.printer.computer.id,
            "computer_name": response.printer.computer.name,
            "userdata": userdata
        }
        return result
    
    def _create_sample_pdf(self, userdata):
        pdf_file = "/tmp/{}template.pdf".format(uuid.uuid4().hex)
        canvas = Canvas(pdf_file)
        lines = [
            self._companydata['name'],
            self._companydata['address'],
            self._companydata['city'] + ' ' + self._companydata['postcode'],
            self._companydata['number'],
            '', '',
            'Dear ' + userdata['name'] + ',',
            '',
            'Unfortunately we were not able to contact you through digital channels.',
            'Please call us on ' + self._companydata['number'] + ' to update your details.',
            '', '',
            'Yours sincerely,', self._companydata['name']
        ]
        self._add_lines(canvas, lines)
        canvas.save()
        return pdf_file
    
    def _add_lines(self,
                   canvas,
                   lines,
                   lineheight=20,
                   top=750,
                   left=70):
        for idx, line in enumerate(lines):
            canvas.drawString(left, top-(idx * lineheight),  line)

class MissingEnvironmentVariableError(Exception):
    def __init__(self, name):
        super().__init__("Environment variable {} is not defined."
                         .format(name))

