import boto3

def lambda_handler(event, context):
    customEndpoints = 0
    numEndpoints = len(event['Endpoints'])
    
    print("Payload:\n", event)
    print("Endpoints in payload: " + str(numEndpoints))

    for key in event['Endpoints'].keys(): 
        userdata = {
            "address": event['Endpoints'][key]['Address'],
            "FirstName": event['Endpoints'][key]['Attributes']['FirstName'][0],
            "LastName": event['Endpoints'][key]['Attributes']['LastName'][0]
        }
        pdf_file = _create_pdf(userdata)
        print_job = _create_print_job(pdf_file)
        print(response)
    return

def _create_pdf():
    pdf_file = None
    from fpdf import Template

    #this will define the ELEMENTS that will compose the template. 
    elements = [
        { 'name': 'company_name', 'type': 'T', 'x1': 17.0, 'y1': 32.5, 'x2': 115.0, 'y2': 37.5, 'font': 'Arial', 'size': 12.0, 'bold': 1, 'italic': 0, 'underline': 0, 'foreground': 0, 'background': 0, 'align': 'I', 'text': '', 'priority': 2, },
        { 'name': 'box', 'type': 'B', 'x1': 15.0, 'y1': 15.0, 'x2': 185.0, 'y2': 260.0, 'font': 'Arial', 'size': 0.0, 'bold': 0, 'italic': 0, 'underline': 0, 'foreground': 0, 'background': 0, 'align': 'I', 'text': None, 'priority': 0, },
        { 'name': 'box_x', 'type': 'B', 'x1': 95.0, 'y1': 15.0, 'x2': 105.0, 'y2': 25.0, 'font': 'Arial', 'size': 0.0, 'bold': 1, 'italic': 0, 'underline': 0, 'foreground': 0, 'background': 0, 'align': 'I', 'text': None, 'priority': 2, },
        { 'name': 'user_message', 'type': 'L', 'x1': 100.0, 'y1': 25.0, 'x2': 100.0, 'y2': 57.0, 'font': 'Arial', 'size': 0, 'bold': 0, 'italic': 0, 'underline': 0, 'foreground': 0, 'background': 0, 'align': 'I', 'text': None, 'priority': 3, },
    ]
    
    #here we instantiate the template and define the HEADER
    f = Template(format="A4", elements=elements,
                 title="Sample Invoice")
    f.add_page()
    
    #we FILL some of the fields of the template with the information we want
    #note we access the elements treating the template instance as a "dict"
    f["company_name"] = "Sample Company"
    f["user_message"] = "This is a user message"
    
    #and now we render the page
    pdf_file = "./template.pdf"
    f.render(pdf_file)
    return pdf_file
    
def _create_print_job(pdf_file):
    from printnodeapi import Gateway
    try:
        os.environ['API_KEY']
        pdf_base64 = a = open(pdf_file, "rb").read().encode("base64")
        gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
        response = gateway.PrintJob(printer=None,base64=pdf_base64))
        '''
        Results:
        PrintJob(id=251153, printer=Printer(id=50120, computer=Computer(id=10027, name='5.2015-07-10 15:04:40.253763.TEST-COMPUTER', inet=None, inet6=None, hostname=None, version=None, create_timestamp='2015-07-10T15:04:40.253Z', state='created'), name='10027.3.TEST-PRINTER', description='description', capabilities={'capability_1': 'one', 'capability_2': 'two'}, default=False, create_timestamp='2015-07-10T15:04:40.253Z', state=None), title='PrintJob', content_type='pdf_uri', source='PythonApiClient', expire_at=None, create_timestamp='2015-07-10T15:05:27.087Z', state='new')
        '''
    except:
        response = {}
    return response
    