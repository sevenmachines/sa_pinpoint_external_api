import boto3
import os
import binascii
import base64
from reportlab.pdfgen.canvas import Canvas

def lambda_handler(event, context):
    customEndpoints = 0
    numEndpoints = len(event['Endpoints'])
    
    print("Payload:\n", event)
    print("Endpoints in payload: " + str(numEndpoints))
    companydata = {
        "name": os.environ.get("COMPANY_NAME", ''),
        "address": os.environ.get("COMPANY_ADDRESS", ''),
        "city": os.environ.get("COMPANY_CITY", ''),
        "postcode": os.environ.get("COMPANY_POSTCODE", ''),
        "number": os.environ.get("COMPANY_NUMBER", ''),
    }
    companydata = {
        "name": "ACME Print",
        "address": "10 Someplace way",
        "city": "London",
        "postcode": "SW10 2DF",
         "number": "0123 1234 321",
   }
    for endpoint in event['Endpoints'].values(): 
        userdata = {
            "address": endpoint['Address'],
            "name": '{} {}'.format(endpoint['Attributes']['FirstName'],
                                   endpoint['Attributes']['LastName'])
        }
        pdf_file = _create_sample_pdf(companydata, userdata)
        print_job = _create_print_job(pdf_file)
        print(print_job)
    return

def _create_print_job(pdf_file):
    from printnodeapi import Gateway
    api_key = os.environ.get('API_KEY',
                             'XXX')
    # Setup printers
    gateway=Gateway(url='https://api.printnode.com',apikey=api_key)
    try:
        default_printer = [p for p in gateway.printers() if p.default][0]
    except IndexError:
        print("No default printer found")
        return {}
    
    with open(pdf_file, "rb") as pdf_file:
        pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
    try:
        response = gateway.PrintJob(printer=default_printer.id,
                                    base64=pdf_base64)
    except:
        print(e)
        response = {}
    return response

def _create_sample_pdf(companydata,
                userdata):
    from reportlab.lib.pagesizes import A4
    pdf_file = "./{}template.pdf".format(binascii.b2a_hex(os.urandom(8)))
    canvas = Canvas(pdf_file, pagesize=A4)
    lines = [
        companydata['name'], companydata['address'], companydata['city'] + ' ' + companydata['postcode'], companydata['number'],
        '', '',
        'Dear ' + userdata['name'] + ',', '',
        'Unfortunately we were not able to contact you through digital channels.',
        'Please give us a call on ' + companydata['number'] + ' and we will update your details.',
        '', '',
        'Yours sincerely,', companydata['name']
    ]
    _add_lines(canvas, lines)
    canvas.save()
    return pdf_file

def _add_lines(canvas, lines,
               lineheight=20,
               top=750,
               left=70):
    for idx, line in enumerate(lines):
        canvas.drawString(left, top-(idx * lineheight),  line)

if __name__ == '__main__':
    event = {
        "Endpoints": {
            "A": {
                "Address": "10 somewhere street",
                "Attributes": {"FirstName": "Bob", "LastName": "Bobert"}
                }
        }}
    context = None
    lambda_handler(event, context)
    
    
'''
        Results:
        PrintJob(id=251153, printer=Printer(id=50120, computer=Computer(id=10027, name='5.2015-07-10 15:04:40.253763.TEST-COMPUTER', inet=None, inet6=None, hostname=None, version=None, create_timestamp='2015-07-10T15:04:40.253Z', state='created'), name='10027.3.TEST-PRINTER', description='description', capabilities={'capability_1': 'one', 'capability_2': 'two'}, default=False, create_timestamp='2015-07-10T15:04:40.253Z', state=None), title='PrintJob', content_type='pdf_uri', source='PythonApiClient', expire_at=None, create_timestamp='2015-07-10T15:05:27.087Z', state='new')
'''
