import boto3
import os
import uuid
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
    api_key = os.environ.get('PRINTNODE_API_KEY')
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
    pdf_file = "./{}template.pdf".format(uuid.uuid4().hex)
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
