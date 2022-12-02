import enum
import json
import logging
import socket
import ssl
from dateutil import parser
from typing import Optional
import requests
from requests.adapters import HTTPAdapter, DEFAULT_POOLBLOCK, PoolManager
from carrier_data_tool.celery_app import app

from company.serializers import *
BASE_URL = 'https://mobile.fmcsa.dot.gov/qc/services'


class InvalidCountryException(Exception):
    pass


class FMCSAEndpoints(enum.Enum):
    GET_CARRIER_BY_NAME = '/carriers/name/{}'
    GET_CARRIER_BY_DOT = '/carriers/{}'
    GET_CARRIER_BY_DOCKET_NUMBER = '/carriers/docket-number/{}'
    GET_CARRIER_BASICS = '/carriers/{}/basics'  # https://mobile.fmcsa.dot.gov/qc/services/carriers/3802151/basics
    GET_CARRIER_CARGO_CARRIED = '/carriers/{}/cargo-carried'
    GET_CARRIER_OPERATION_CLASSIFIED = '/carriers/{}/operation-classification'
    GET_CARRIER_OOS = '/carriers/{}/oos'
    GET_CARRIER_DOCKET_NUMBERS = '/carriers/{}/docket-numbers'
    GET_CARRIER_AUTHORITY = '/carriers/{}/authority'


default_headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.8,ru;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'mobile.fmcsa.dot.gov',
    'User-Agent': 'PostmanRuntime/7.28.1'
}


class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=DEFAULT_POOLBLOCK, **pool_kwargs):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1_2)


class FMCSABot:
    def __init__(self, api_key, log=True, log_level=logging.INFO):
        self.logger = logging.getLogger('custom_logger')
        self.logger.setLevel(log_level)
        if log:
            s_handler = logging.StreamHandler()

            s_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            s_handler.setFormatter(s_formatter)
            self.logger.addHandler(s_handler)

        # country = self.get_country()
        # if country != 'US':
        #     self.logger.error(F"Can't fetch country")
        #     raise InvalidCountryException()

        self.base_url = BASE_URL
        self.api_key = api_key
        self.endpoints = FMCSAEndpoints
        self.default_headers = default_headers
        self.session = requests.Session()
        self.get_new_session()

        self.last_json = self.last_response = None

        self.logger.info('FMCSA Bot initialized')
        self.basics = None
        self.oos = None
        self.operation_classification = None
        self.carrier_authority = None

    def get_new_session(self):
        self.logger.info('Resetting session')
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)
        self.session.mount('https://', MyAdapter())

    def get_country(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print(ip)
        endpoint = f'http://ipinfo.io/{ip}/country?token=71309f58e4aebf'

        response = requests.get(endpoint, verify=True)

        if response.status_code != 200:
            return

        data = response.json()
        # print(data)
        return data['country']

    def send_request(self, endpoint: str, header: Optional[dict] = None):
        url = f'{self.base_url}{endpoint}?webKey={self.api_key}'
        if header:
            self.session.headers.update(header)
        try:
            # self.logger.info(f'Sending request to {url}')
            response = self.session.get(url)
        except Exception as exc:
            self.logger.error(str(exc))
        else:
            # self.logger.info(response.text)  # TEST
            try:
                resp_json = response.json()
            except json.JSONDecoder:
                self.logger.error('Response is not JSON Serializable.')
            else:
                self.last_json = resp_json
            self.last_response = response

            if response.status_code == 200:
                return True
        return False

    def get_carrier_by_dot(self, dot_number):
        url = self.endpoints.GET_CARRIER_BY_DOT.value.format(dot_number)
        return self.send_request(url)

    def get_data(self, dot_number, endpoint):
        url = endpoint.format(dot_number)
        return self.send_request(url)

def create_database(carrier_data, operation_class_data, basics_data, oos_data, cargo_data):
    # print(json.dumps(carrier_data, indent=4))
    #CARRIER DETAILS
    carrier_data = carrier_data.get('content')
    carrier_data = carrier_data.get('carrier')
    data = dict()
    data['is_active'] = True if carrier_data.get("allowedToOperate") == "Y" else False
    data['dot'] = carrier_data.get('dotNumber')
    data['legal_name'] = carrier_data.get('legalName')
    data['dba'] = carrier_data.get('dbaName')
    # print(data)
    serializer = CompanySerializer(data=data)
    serializer.is_valid(raise_exception=True)
    company_obj = serializer.save()
    data.clear()

    #OOS
        #vehicle
    data['type'] = Inspection.inspection_type.VEHICLE
    data['Inspections'] = carrier_data.get('vehicleInsp')
    data['oos'] = carrier_data.get('vehicleOosInsp')
    data['national_average'] = carrier_data.get('vehicleOosRateNationalAverage')
    data['company'] = company_obj.id
    serializer = InspectionSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    data.clear()

        #Driver
    data['type'] = Inspection.inspection_type.DRIVER
    data['Inspections'] = carrier_data.get('driverInsp')
    data['oos'] = carrier_data.get('driverOosInsp')
    data['national_average'] = carrier_data.get('driverOosRateNationalAverage')
    data['company'] = company_obj.id
    serializer = InspectionSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    data.clear()
    
        #HAZMAT
    data['type'] = Inspection.inspection_type.HAZMAT
    data['Inspections'] = carrier_data.get('hazmatInsp')
    data['oos'] = carrier_data.get('hazmatOosInsp')
    data['national_average'] = carrier_data.get('hazmatOosRateNationalAverage')
    data['company'] = company_obj.id
    serializer = InspectionSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    data.clear()


    #CARRIER ADDRESS
    data['city'] = carrier_data.get('phyCity')
    data['country'] = carrier_data.get('phyCountry')
    data['state'] = carrier_data.get('phyState')
    data['zip_code'] = carrier_data.get('phyZipcode')
    data['company'] = company_obj.id

    serializer = AddressSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    data.clear()

    #OPERATION CLASSIFICATION
    operation_class_data = operation_class_data['content']
    count = 0
    for opd in operation_class_data:
        data['operation_classification_description'] = opd.get('operationClassDesc')
        data['operaton_classfication_id'] = opd.get('id').get('operationClassId')
        data['company'] = company_obj.id

        serializer = OperationClasficationSerialzer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data.clear()

    #  BASICS
    # print('basic_data: ', basics_data)
    count = 1
    for bd in basics_data['content']:
        basic = bd.get('basic')

        data['basics_id'] = basic.get('id').get('basicsId')
        data['percentile'] = basic.get('basicsPercentile') if type(basic.get('basicsPercentile')) == float else None
        data['run_date'] = parser.isoparse(basic.get('basicsRunDate'))
        data['violation_threshold'] = basic.get('basicsViolationThreshold')
        data['exceeded_fmcsa_intervention_threshold'] = basic.get('exceededFMCSAInterventionThreshold')
        data['measure_value'] = basic.get('measureValue')
        data['on_road_performance_threshold_violation_indicator'] = basic.get('onRoadPerformanceThresholdViolationIndicator')
        data['serious_violation_investigation_past_12month_Indicator'] = basic.get('seriousViolationFromInvestigationPast12MonthIndicator')
        data['total_inspection_with_violation'] = basic.get('totalInspectionWithViolation')
        data['total_violation'] = basic.get('totalViolation')
        data['company'] = company_obj.id

        print(f'data::: {count}: {data}')
        count+=1
        serializer = BasicSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        basic_obj = serializer.save()
        data.clear()

        #BASICS TYPE
        data['code'] = basic.get('basicsType').get('basicsCode')
        data['code_mcmis'] = basic.get('basicsType').get('basicsCodeMcmis')
        data['long_description'] = basic.get('basicsType').get('basicsLongDesc')
        data['short_description'] = basic.get('basicsType').get('basicsShortDesc')
        data['basics'] = basic_obj.id
        # print(data)
        serializer = BasicEntitySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data.clear()

    #CARGO CARRIED
    print('cargo_carrid: ', cargo_data)
    cargo_data = cargo_data['content']
    for cd in cargo_data:
        data['description'] = cd.get('cargoClassDesc')
        data['cargo_id'] = cd.get('id').get('cargoClassId')
        data['company'] = company_obj.id

        serializer = CargoCarriedSerialzer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data.clear()



    return


@app.task(bind=True)
def get_leads(self):
    print("Welcome to MetroMax Lead Finder\n")
    get_new = True
    # dot = 386839   #3790182   # '3143777' 3477979
    dot = 1021143
    # while True:
    #     try:
    #         dot = int(input('Please enter a DOT number to start from. Suggested: '))
    #     except ValueError:
    #         print('Please enter a valid DOT number.')
    #         continue
    #     else:
    #         if not 6 <= len(str(dot)) <= 7:
    #             print('Please enter a valid DOT number with 6 or 7 digits!\n')
    #             continue
    #         break

    bot = FMCSABot('4ac96297a698eb309980998ca8d2f2c2594858ef')
    n = 1
    try:
        while dot<1021442:
    #     print(f'\nDOT: {dot}')
            bot.get_data(str(dot), FMCSAEndpoints.GET_CARRIER_BY_DOT.value)
            carrier_data = bot.last_json or {'content': None}
            content = json.dumps(carrier_data.get('content'), indent=4)
            # print('content', content)

            bot.get_data(str(dot), FMCSAEndpoints.GET_CARRIER_OPERATION_CLASSIFIED.value)
            operation_classification_data = bot.last_json or {'content': None}
            content = json.dumps(operation_classification_data.get('content'), indent=4)
            # print('content', content)

            bot.get_data(str(dot), FMCSAEndpoints.GET_CARRIER_BASICS.value)
            basics_data = bot.last_json or {'content': None}
            content = json.dumps(basics_data.get('content'), indent=4)
            # print('content',content)

            bot.get_data(str(dot), FMCSAEndpoints.GET_CARRIER_OOS.value)
            oos_data = bot.last_json or {'content': None}
            content = json.dumps(oos_data.get('content'), indent=4)
            # print('content', content)

            bot.get_data(str(dot), FMCSAEndpoints.GET_CARRIER_CARGO_CARRIED.value)
            cargo_data = bot.last_json or {'content': None}
            content = json.dumps(oos_data.get('content'), indent=4)
            # print('content', content)

            create_database(carrier_data,operation_classification_data, basics_data, oos_data, cargo_data)

            dot+=1
    #
    #     if content is None:
    #         if n == 1:
    #             print('DOT number not yet registered, checking previous one')
    #             sleep(1)
    #             dot -= 1
    #             continue
    #         print(f"DOT Number not yet assigned, will check again in 5 seconds")
    #         sleep(5)
    #         continue
    #     carrier = content.get('carrier')
    #     legal_name = carrier.get('legalName')
    #     print(f'Carrier Found: {legal_name}')
    #     print(f'Looking for next DOT number\n')
            # https://mobile.fmcsa.dot.gov/qc/services/carriers/3790183/basics
            # csv_columns = list(reversed(safe_data.keys()))
            # csv_file_name = 'safe_data.csv'
            # try:
            #     with open(csv_file_name, 'w') as csvfile:
            #         writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            #         writer.writeheader()
            #
            #         for i in range(100):
            #             carrier_data = bot.get_data(str(dot), FMCSAEndpoints.GET_CARRIER_BY_DOT.value)
            #             if carrier_data:
            #                 data = bot.last_json
            #                 print(data)
            #                 writer.writerow(data["content"]['carrier'])
            #             dot += 1
            # except IOError as exc:
            #     print(f"I/O error: {str(exc)}")
            # except Exception as exc:
            #     print(str(exc))
            # dot += 500
            # n += 1
    except Exception as exc:
        print("Something went wrong, please contact developer")
        print(str(exc))

    # else:
    #     with open('fmcsa_carrier_info_fci.json.json', 'r') as f:
    #         data = json.loads(f.read())
    #         print(data['content']['_links'])
    #         d_ = data["content"]['carrier']
    #         print(d_)
    #         for x in d_:
    #             print(f'{x}: {d_[x]}')
    #
    #         # multiple_level = pd.json_normalize(data, record_path=['content'])
    #         # print(multiple_level)


    # data[legal_name]
    # CompanySerialzers
