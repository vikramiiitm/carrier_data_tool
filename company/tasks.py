import enum
import json
import logging
import os.path
import socket
import ssl
import threading
import zipfile
import datetime
from pathlib import Path
from threading import Thread
from traceback import format_exc

from bs4 import BeautifulSoup
from dateutil import parser
from typing import Optional
import requests
from requests.adapters import HTTPAdapter, DEFAULT_POOLBLOCK, PoolManager
from carrier_data_tool.celery_app import app

from twocaptcha import TwoCaptcha
from bs4 import BeautifulSoup
import pandas as pd

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
    carrier_data = carrier_data.get('content', None)
    if carrier_data is not None:
        carrier_data = carrier_data.get('carrier', None)
        if carrier_data is not None:
            data = dict()
            data['is_active'] = True if carrier_data.get("allowedToOperate") == "Y" else False
            data['dot'] = carrier_data.get('dotNumber')
            data['legal_name'] = carrier_data.get('legalName')
            data['dba'] = carrier_data.get('dbaName')
            # print(data)
            try:
                serializer = CompanySerializer(data=data)
                serializer.is_valid(raise_exception=True)
                company_obj = serializer.save()

                # calling async task to get insurance data from fmcsa
                try:
                    Insurance_history.delay(data['dot'])
                except Exception as exc:
                    logger.info(f'some error occurred in creating insurance data: {str(exc)}')
            except:
                return
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
    if operation_class_data:
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
    if basics_data['content']:
        if basics_data['content']:
            for bd in basics_data['content']:
                basic = bd.get('basic')

                data['basics_id'] = basic.get('id').get('basicsId')
                data['percentile'] = basic.get('basicsPercentile') if type(basic.get('basicsPercentile', None)) == float else None
                data['run_date'] = parser.isoparse(basic.get('basicsRunDate')) if basic.get('basicsRunDate', None) else None
                data['violation_threshold'] = basic.get('basicsViolationThreshold')
                data['exceeded_fmcsa_intervention_threshold'] = basic.get('exceededFMCSAInterventionThreshold')
                data['measure_value'] = basic.get('measureValue')
                data['on_road_performance_threshold_violation_indicator'] = basic.get('onRoadPerformanceThresholdViolationIndicator', None)
                data['serious_violation_investigation_past_12month_Indicator'] = basic.get('seriousViolationFromInvestigationPast12MonthIndicator', None)
                data['total_inspection_with_violation'] = basic.get('totalInspectionWithViolation', None)
                data['total_violation'] = basic.get('totalViolation', None)
                data['company'] = company_obj.id

                print(f'data::: {count}: {data}')
                count+=1
                serializer = BasicSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                basic_obj = serializer.save()
                data.clear()

                #BASICS TYPE
                basicstype = basic.get('basicsType', None)
                if basicstype:
                    data['code'] = basicstype.get('basicsCode', None)
                    data['code_mcmis'] = basicstype.get('basicsCodeMcmis', None)
                    data['long_description'] = basicstype.get('basicsLongDesc', None)
                    data['short_description'] = basicstype.get('basicsShortDesc', None)
                    data['basics'] = basic_obj.id
                    # print(data)
                    serializer = BasicEntitySerializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    data.clear()

    #CARGO CARRIED
    print('cargo_carrid: ', cargo_data)
    cargo_data = cargo_data['content']
    if cargo_data:
        for cd in cargo_data:
            data['description'] = cd.get('cargoClassDesc',None)
            data['cargo_id'] = cd.get('id').get('cargoClassId', None)
            data['company'] = company_obj.id

            serializer = CargoCarriedSerialzer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data.clear()

    return

def thread_create_leads(bot, dot):
    bot.get_data(str(dot), FMCSAEndpoints.GET_CARRIER_BY_DOT.value)
    carrier_data = bot.last_json or {'content': None}
    # content = json.dumps(carrier_data.get('content'), indent=4)
    # print('content', content)

    bot.get_data(str(dot), FMCSAEndpoints.GET_CARRIER_OPERATION_CLASSIFIED.value)
    operation_classification_data = bot.last_json or {'content': None}
    # content = json.dumps(operation_classification_data.get('content'), indent=4)
    # print('content', content)

    bot.get_data(str(dot), FMCSAEndpoints.GET_CARRIER_BASICS.value)
    basics_data = bot.last_json or {'content': None}
    # content = json.dumps(basics_data.get('content'), indent=4)
    # print('content',content)

    bot.get_data(str(dot), FMCSAEndpoints.GET_CARRIER_OOS.value)
    oos_data = bot.last_json or {'content': None}
    # content = json.dumps(oos_data.get('content'), indent=4)
    # print('content', content)

    bot.get_data(str(dot), FMCSAEndpoints.GET_CARRIER_CARGO_CARRIED.value)
    cargo_data = bot.last_json or {'content': None}
    # content = json.dumps(oos_data.get('content'), indent=4)
    # print('content', content)

    create_database(carrier_data, operation_classification_data, basics_data, oos_data, cargo_data)

    dot += 1

@app.task(bind=True)
def get_leads(self):
    print("Welcome to MetroMax Lead Finder\n")
    bot = FMCSABot('4ac96297a698eb309980998ca8d2f2c2594858ef')
    threads = list()
    batchsize = 10 #don't change
    try:
        for i in range(3333450, 3333460, batchsize):
            print('batch: ', batchsize)
            for j in range(i,i+batchsize):
                x = threading.Thread(target=thread_create_leads, args=(bot, j))
                threads.append(x)
                x.start()

            for index, thread in enumerate(threads):
                logging.info("Main    : before joining thread %d.", index)
                thread.join()
                logging.info("Main    : thread %d done", index)

            threads.clear()
    except Exception as exc:
        print("Something went wrong, please contact developer")
        print(str(exc))

    # data[legal_name]
    # CompanySerialzers


from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

FILE_DIR = Path('/tmp')

FMCSA_BASE_URL = 'https://ai.fmcsa.dot.gov'
DOWNLOAD_SECTION_ENDPOINT = '/SMS/Tools/Downloads.aspx'
hazmat_carrier_text = 'The SMS Summary Results for active Interstate carriers and active Intrastate Hazmat'
hazmat_carrier_text_2 = 'Motor Carriers'
non_hazmat_carrier_text = 'The SMS Summary Results for active Intrastate Non-Hazmat Motor Carriers'

def unzip():
    with zipfile.ZipFile('tmp/hazmat.zip') as zf:
        zf.extractall('zips')


def zip_extract(file_name):
    with zipfile.ZipFile(file_name) as zip_:
        file_name = file_name.split('.')[0]
        print('extracting files', file_name)
        zip_.extractall(f'{file_name}')
        # for file_ in zip_.namelist():
        #     print(f'filename: ',file_)
        #     if 'SMS' in file_:
        #         # old_file = FILE_DIR.joinpath(file_)
        #         old_file = os.path.join(FILE_DIR, file_)
        #         if os.path.exists(old_file):
        #             print((f'old file: {old_file}'))
        #             new_file = file_name
        #             if '/' in file_name:
        #                 new_file = file_name.split('/')[-1]
        #             new_file = new_file.strip('zip')
        #             new_file += 'txt'
                    # os.rename(old_file, new_file)
                    # old_file.rename(os.path.join(FILE_DIR, new_file))



@app.task
def get_new_sms_result():
    error_data = {'success': False}
    hazmat_file_name = 'hazmat.zip'
    non_hazmat_file_name = 'nonhazmat.zip'
    response = requests.get('https://ai.fmcsa.dot.gov/SMS/Tools/Downloads.aspx')
    logger.info(f'response: {response}')
    if response.status_code == 200:
        resp = response.content
        try:
            soup = BeautifulSoup(resp, 'html.parser')
            ul = soup.find_all('ul', {'class': 'downloadLinks multi'})

            for ultag in ul:
                li_item = ultag.find_all('li')

                for li_tag in li_item:
                    li_text = li_tag.text

                    if hazmat_carrier_text in li_text and hazmat_carrier_text_2 in li_text:
                        tag = li_tag.find_all('a', href=True)
                        link = FMCSA_BASE_URL + tag[0]['href']
                        file_resp = requests.get(link, stream=True)

                        if file_resp.status_code == 200:
                            logger.info(f'Get {link} successful')
                            new_hazmat_path = os.path.join('tmp',hazmat_file_name)

                            if file_resp.headers.get('Content-Type') == 'application/x-zip-compressed':
                                with open(new_hazmat_path, 'wb') as f:
                                    f.write(file_resp.content)
                                # logger.debug(f"Hazmat File creation status: "
                                #              f"{os.path.join('tmp',hazmat_file_name).is_file()}")
                            else:
                                error_data['error_detail'] = 'Hazmat file content type error'
                        continue

                    if non_hazmat_carrier_text in li_tag.text:
                        tag = li_tag.find_all('a', href=True)
                        link = FMCSA_BASE_URL + tag[0]['href']
                        file_resp = requests.get(link, stream=True)

                        if file_resp.status_code == 200:
                            # logger.info(f'Get {link} successful')

                            if file_resp.headers.get('Content-Type') == 'application/x-zip-compressed':
                                new_non_hazmat_path = os.path.join('tmp', non_hazmat_file_name)
                                with open(new_non_hazmat_path, 'wb') as f:
                                    f.write(file_resp.content)
                                # logger.info("Non Hazmat File creation status: "
                                #             f"{os.path.join('tmp', non_hazmat_file_name).is_file()}")

                            else:
                                error_data['error_detail'] = 'Non Hazmat file content type error'
                        continue

            hazmat_file_path = os.path.join('tmp',hazmat_file_name)

            zip_extract(hazmat_file_path.__str__())
            # hazmat_file_path.unlink()

            non_hazmat_file_path = os.path.join('tmp',non_hazmat_file_name)

            zip_extract(non_hazmat_file_path.__str__())
            # non_hazmat_file_path.unlink()

        except Exception as exc:
            logger.error(str(exc))
            error_data['error_detail'] = str(exc)

    else:
        error_data['error_detail'] = 'SMS Download page error'
        error_data['html'] = response.text

    if error_data.get('error_detail') is not None:
        return error_data

    return {'success': True}


import pandas as pd

@app.task()
def update_leads():
    # HAZMAT DATA UPDATE
    hazmat_file = None
    non_hazmat_file = None
    for filename in os.listdir('tmp/hazmat'):
        f = os.path.join('tmp', 'hazmat', filename)
        # checking if it is a file
        if os.path.isfile(f):
            print(f)
            # check if out of two files which one contains data
            k = pd.read_csv(f)
            text = ((k.head(0)).columns).values[0]
            if text:
                if not text == 'The extracted data is from an FMCSA Safety Measurement System (SMS) data.':
                    hazmat_file = f
    for filename in os.listdir('tmp/nonhazmat'):
        # print(filename, 'inside', os.path.isfile(os.path.join('tmp/hazmat', filename)))
        f = os.path.join('tmp', 'nonhazmat', filename)
        # checking if it is a file
        if os.path.isfile(f):
            # check if out of two files which one contains data
            k = pd.read_csv(f)
            text = ((k.head(0)).columns).values[0]
            # print('text: ',text)
            if text:
                if not text == 'The extracted data is from an FMCSA Safety Measurement System (SMS) data.':
                    non_hazmat_file = f
    print('file: ',hazmat_file, non_hazmat_file)


    import time

    df = pd.read_csv(hazmat_file)
    print(df.head(4))
    i = 0
    print('starting the update leads')
    for key, value in df.iterrows():
        dot = value.get('DOT_NUMBER')
        print('hazmat dot: ', dot)
        # if dot>1003210:
        #     break

        try:
            comp_obj = Company.objects.get(dot=dot)
            if comp_obj:
                print('Found the company: ', comp_obj.id)
        except:
            continue  # company doesn't exist

        try:
            print('update')
            inspection = InspectionAndSafetyMeasures.objects.filter(company=comp_obj.id, hazmat=Hazmat.HAZMAT).last()
            print('inspection: ', inspection)
            if inspection:
                data = {
                    # 'is_active': True,
                    'inspection_total': value.get('INSP_TOTAL'),
                    'driver_inspection_total': value.get('DRIVER_INSP_TOTAL'),
                    'driver_oos_inspection_total': value.get('DRIVER_OOS_INSP_TOTAL'),
                    'vehicle_inspection_total': value.get('VEHICLE_INSP_TOTAL'),
                    'vehicle_oos_inspection_total': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'unsafe_driver_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'unsafe_driver_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'hos_driver_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'hos_driver_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'driver_fit_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'driver_fit_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'contr_subst_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'contr_subst_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'vehicle_maintenance_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'vehicle_maintenance_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                }
                serializer = InspectionAndSafetyMeasuresSerializer(inspection, data, partial=True)
                serializer.is_valid(raise_exception=True)
                print(serializer.validated_data)
                obj = serializer.save()
                print('obj')
            else:
                # create
                print('create')
                data = {
                    'company': comp_obj.id,
                    'hazmat': Hazmat.HAZMAT,
                    # 'is_active': True,
                    'inspection_total': value.get('INSP_TOTAL'),
                    'driver_inspection_total': value.get('DRIVER_INSP_TOTAL'),
                    'driver_oos_inspection_total': value.get('DRIVER_OOS_INSP_TOTAL'),
                    'vehicle_inspection_total': value.get('VEHICLE_INSP_TOTAL'),
                    'vehicle_oos_inspection_total': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'unsafe_driver_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'unsafe_driver_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'hos_driver_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'hos_driver_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'driver_fit_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'driver_fit_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'contr_subst_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'contr_subst_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'vehicle_maintenance_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'vehicle_maintenance_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                }
                print('data: ', data)
                serializer = InspectionAndSafetyMeasuresSerializer(data=data)
                print('serializer: ', serializer)
                serializer.is_valid(raise_exception=True)
                print('validated_data: ', serializer.validated_data)
                inspection = serializer.save()
        except:
            pass



    df = pd.read_csv(non_hazmat_file)
    print(df.head(4))
    i = 0
    print('starting the update leads )')
    time.sleep(5)
    start = time.time()
    for key, value in df.iterrows():
        dot = value.get('DOT_NUMBER')
        print('non_hazmat dot, Count: ',i)
        # if dot>1003210:
        #     break
        try:
            comp_obj = Company.objects.get(dot=dot)
            if comp_obj:
                print('Found the company: ', comp_obj.id)
        except:
            continue  # company doesn't exist

        try:
            print('update')
            inspection = InspectionAndSafetyMeasures.objects.filter(company=comp_obj.id, hazmat=Hazmat.NON_HAZMAT).last()
            print('inspection: ', inspection)
            if inspection:
                data = {
                    # 'is_active': True,
                    'inspection_total': value.get('INSP_TOTAL'),
                    'driver_inspection_total': value.get('DRIVER_INSP_TOTAL'),
                    'driver_oos_inspection_total': value.get('DRIVER_OOS_INSP_TOTAL'),
                    'vehicle_inspection_total': value.get('VEHICLE_INSP_TOTAL'),
                    'vehicle_oos_inspection_total': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'unsafe_driver_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'unsafe_driver_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'hos_driver_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'hos_driver_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'driver_fit_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'driver_fit_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'contr_subst_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'contr_subst_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'vehicle_maintenance_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'vehicle_maintenance_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                }
                serializer = InspectionAndSafetyMeasuresSerializer(inspection, data, partial=True)
                serializer.is_valid(raise_exception=True)
                print(serializer.validated_data)
                obj = serializer.save()
                print('obj')
            else:
                # create
                print('create')
                data = {
                    'company': comp_obj.id,
                    'hazmat': Hazmat.NON_HAZMAT,
                    # 'is_active': True,
                    'inspection_total': value.get('INSP_TOTAL'),
                    'driver_inspection_total': value.get('DRIVER_INSP_TOTAL'),
                    'driver_oos_inspection_total': value.get('DRIVER_OOS_INSP_TOTAL'),
                    'vehicle_inspection_total': value.get('VEHICLE_INSP_TOTAL'),
                    'vehicle_oos_inspection_total': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'unsafe_driver_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'unsafe_driver_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'hos_driver_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'hos_driver_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'driver_fit_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'driver_fit_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'contr_subst_inspection_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'contr_subst_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'vehicle_maintenance_violation': value.get('VEHICLE_OOS_INSP_TOTAL'),
                    'vehicle_maintenance_measure': value.get('VEHICLE_OOS_INSP_TOTAL'),
                }
                print('data: ', data)
                serializer = InspectionAndSafetyMeasuresSerializer(data=data)
                print('serializer: ', serializer)
                serializer.is_valid(raise_exception=True)
                print('validated_data: ', serializer.validated_data)
                inspection = serializer.save()
        except:
            pass
    end = time.time()
    print('total time: ',end - start)



'''Insurance Data Fetching'''
def SolveCaptcha():
    solver = TwoCaptcha('77709a0c702e02bae50bc25b8902456c')

    result = solver.solve_captcha(
        site_key='6Ldbx1gUAAAAAMEylxZ_DoZS430WhNsmV47Y5t58',
        page_url='https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist'
    )
    return result

def find_payload():
    try:
        with open("get_detail.html") as f:
            soup = BeautifulSoup(f, 'html.parser')
            legal_name = soup.find_all('input', {'name':'pv_legal_name'})[0].get('value')
            docket_number = soup.find_all('input', {'name':'pv_pref_docket'})[0].get('value')
            pv_vpath = soup.find_all('input', {'name':'pv_vpath'})[0].get('value')
            logger.info(f'docket_number, legal_name, pv_vpath: {docket_number, legal_name, pv_vpath}')
            return docket_number,legal_name, pv_vpath
    except:
        return None, None, None
def read_Insurance_from_html():
    df  = pd.read_html('Insurance.html', flavor='bs4')
    insurance_data = df[4]
    logger.info(df[4])
    return df[4]

def find_applicant_id():
    with open("carrlist.html") as f:
        soup = BeautifulSoup(f, 'html.parser')
        try:
            return soup.find('input', {'name':'pv_apcant_id'}).get('value')
        except:
            return 'apcant_id_error'

@app.task()
def Insurance_history(dot):
    # step1 carrlist
    url = "https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist"
    captcha = SolveCaptcha()
    payload={
        'n_dotno': dot,
        's_prefix': '',
        'n_docketno': '',
        's_legalname': '',
        's_state': '',
        'pv_vpath': 'LIVIEW',
        'g_recaptcha_response':captcha
        }
    files=[
    ]
    headers = {}
    session = requests.Session()
    response = session.request("POST", url, headers=headers, data=payload, files=files)
    with open("carrlist.html", "w") as f:
        f.write(response.text)
    # step2: Find pv_apcant_id and request get_detail
    pv_apcant_id = find_applicant_id()
    logger.info(f'pv_apcant_id: {pv_apcant_id}')
    if pv_apcant_id != 'apcant_id_error':
        payload = {
            'pv_apcant_id': pv_apcant_id,
            'pv_vpath': 'LIVIEW'
        }
        url_detail = 'https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_getdetail'
        response = session.request("POST", url_detail, headers=headers, data=payload, files=files)

        with open("get_detail.html", "w") as f:
            f.write(response.text)

        docket_number, legal_name, pv_vpath = find_payload() #it uses get_detail.html

    #step 3 get Insurance History
        if docket_number and legal_name and pv_vpath:
            payload = {
                'pv_apcant_id': pv_apcant_id,
                'pv_legal_name': legal_name,
                'pv_pref_docket': docket_number,
                'pv_usdot_no': dot,
                'pv_vpath': 'LIVIEW'
            }
            insurance_history_url = 'https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_insurancehistory'
            response = session.request('POST', insurance_history_url, headers=headers, data=payload, files=files)

            with open("Insurance.html", "w") as f:
                f.write(response.text)

            df = read_Insurance_from_html()
            # Create Company Insurance data
            company_obj = Company.objects.get(dot=dot)

            for key, value in df.iterrows():
                try:
                    a,b,c = value.get('Effective Date To').split('/')
                    c = c[0:4]
                    date_to = f'{a}/{b}/{c}'
                    data = {
                        'form' : value.get('Form'),
                        'type' : value.get('Type'),
                        'insurance_carrier' : value.get('Insurance Carrier'),
                        'policy_surety' : value.get('Policy/Surety'),
                        'coverage_from' : value.get('Coverage From'),
                        'coverage_to' : value.get('Coverage To'),

                        'effective_date_from' : datetime.datetime.strptime(value.get('Effective Date From'), '%m/%d/%Y').date(),
                        'effective_date_to' : datetime.datetime.strptime(date_to, '%m/%d/%Y').date(),
                        'company' : company_obj.id
                    }
                    insurance_serializer = InsuranceHistorySerializer(data=data)
                    insurance_serializer.is_valid(raise_exception=True)
                    insurance_serializer.save()
                except Exception as exc:
                    logger.info(f'Error occorred in created insurance data for dot {dot}: {str(exc)}')