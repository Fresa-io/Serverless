import os
import requests
import json
import re
import boto3
import base64
import psycopg2
import Levenshtein as lev
from datetime import datetime, date, timedelta
from utility import api_tracker

RDS_HOST = os.environ['RDS_HOST'].strip()
RDS_PORT = os.environ['RDS_PORT'].strip()
RDS_DB = os.environ['RDS_DB'].strip()
RDS_USER = os.environ['RDS_USER'].strip()
RDS_PWD = os.environ['RDS_PWD'].strip()
API_SEARCH_TYPE = os.environ['API_SEARCH_TYPE'].strip()
API_USER_NAME = os.environ['API_USER_NAME'].strip()
API_PASSWORD = os.environ['API_PASSWORD'].strip()
API_URL = os.environ['API_URL'].strip()
LEV_DISTANCE = int(os.environ['LEV_DISTANCE'].strip())
ADDRESS_YEARS_HISTORY = int(os.environ['ADDRESS_YEARS_HISTORY'].strip())
PII_QUERY_SQS_URL = os.environ['PII_QUERY_SQS_URL'].strip()
TRACER_SQS_URL = os.environ['TRACER_SQS_URL'].strip()
ENV_TYPE = os.environ['ENV_TYPE'].strip()
# ENV_TYPE = "DEV"
EMAIL_API_URL = os.environ['EMAIL_API_URL'].strip()
EMAIL_API_KEY = os.environ['EMAIL_API_KEY'].strip()
EMAIL_API_SRC = os.environ['EMAIL_API_SRC'].strip()
MAX_EMAIL_CACHE_AGE = os.environ['MAX_EMAIL_CACHE_AGE'].strip()

conn_str = "host=%s port=%s dbname=%s user=%s password=%s" % (RDS_HOST, RDS_PORT, RDS_DB, RDS_USER, RDS_PWD)


def tracers_broad_append(index, first_name='', last_name='', street='', zipcode='', phone_number='', email='', requester_id=''):
    appends = TracersBroadAppend(lev_distance=LEV_DISTANCE, years_of_address=ADDRESS_YEARS_HISTORY, requester_id=requester_id)
    appends.map_data(index, first_name, last_name, street, zipcode, phone_number, email)
    return appends.post_query()


class TracersBroadAppend:
    def __init__(self, lev_distance=2, years_of_address=5, requester_id=''):
        self.distance = lev_distance
        self.addr_years = years_of_address
        # to-do: move hard coded credentials to config object
        self.SEARCH_TYPE = API_SEARCH_TYPE  # 'Person'  # 'Business' #'Person' #ReversePhone
        self.USER_NAME = API_USER_NAME  # 'stjames'
        self.PASSWORD = API_PASSWORD  # '0c02c416042046839729f9aa62bbbaf5'
        self.url = API_URL  # 'https://api.galaxysearchapi.com/PersonSearch'
        self.conn_str = conn_str
        self.headers = {
            'galaxy-ap-name': self.USER_NAME,
            'galaxy-ap-password': self.PASSWORD,
            'galaxy-search-type': self.SEARCH_TYPE,
            'SourceID': f"expansion_service:{str(requester_id)}",
            'Content-Type': 'application/json'  # ; charset=UTF-8"
        }
        self.body = {}

    def map_data(self, index, first_name, last_name, street, zipcode, phone_number, email):
        response = {}
        # print(index, first_name, last_name, street, zipcode, phone_number, email)
        self.id_ = index
        self.first_name = first_name
        self.last_name = last_name
        # self.street = street
        if len(street) > 4:
            self.street = street
        else:
            self.street = ''
        self.zipcode = zipcode
        self.phone_number = phone_number
        self.email = email
        self.last_name_match = last_name
        self.query_type = 'address'
        self._choose_query_type()

    def _choose_query_type(self):
        if self.first_name != '' and self.last_name != '' and self.street != '' and self.zipcode != '':
            # print('first, last, zipcode')
            self.query_type = 'address'
            self.body = {
                'FirstName': self.first_name,
                'MiddleName': '',
                'LastName': self.last_name,
                'Phone': '',
                'Email': '',
                'Addresses': [
                    {
                        'AddressLine1': self.street,
                        'AddressLine2': self.zipcode
                    }
                ],
            }
        elif self.phone_number != '':
            # print('phone number')
            self.query_type = 'phone'
            self.body = {
                'FirstName': '',
                'MiddleName': '',
                'LastName': '',
                'Phone': self.phone_number,
                'Email': '',
                'Addresses': [
                    {
                        'AddressLine1': '',
                        'AddressLine2': ''
                    }
                ],
            }

        elif self.email != '':
            # print('email')
            self.query_type = 'email'
            self.body = {
                'FirstName': self.first_name,
                'MiddleName': '',
                'LastName': self.last_name,
                'Phone': self.phone_number,
                'Email': self.email,
                'Addresses': [
                    {
                        'AddressLine1': self.street,
                        'AddressLine2': self.zipcode
                    }
                ],
            }

    def _choose_correct_person(self) -> dict:
        # find the best dictionary to match the input where first and last name is given
        for persons in self.reply.get('persons'):
            if self._name_match(self.last_name_match, persons.get('name').get('lastName')) or self.last_name == '':
                return persons
        return None

    def post_query(self):
        # print(self.body)
        if self.body:
            api_tracker(self.id_, self.conn_str, self.url, self.body)
            self.response = requests.post(self.url, data=json.dumps(self.body), headers=self.headers)
            self.reply = self.response.json()
            # print(self.reply)
            # print(f'the reply is {self.reply}')
            # need to enumerate the results and name match and then only use the matched person
            # result to populate the return
            response_code = self.response.status_code
            payload = []
            if not self.reply:
                print(f"No tracers response for id: {self.id_}")
                return [{'code': response_code, 'message': 'No tracers response.', 'query_type': self.query_type}]
            if 'persons' in self.reply:
                persons = self._choose_correct_person()
                if persons:
                    first_name, last_name, dob, combined_addr, city, state, zipcode, phone1, phone2, email1, email2, email3, email4, email5 = '', '', '', '', '', '', '', '', '', '', '', '', '', ''
                    first_name = persons.get('name').get('firstName')
                    last_name = persons.get('name').get('lastName')
                    dob = persons.get('dob')
                
                    ## Grabbing phone 1 and 2
                    phone1 = phone2 = ''
                    for phone in persons.get('phoneNumbers', []):
                        cleaned_phone = re.sub("\D", "", phone.get('phoneNumber', ''))
                        if phone.get('phoneType') == 'Wireless' and not phone1:
                            phone1 = cleaned_phone  # Assign the first wireless number to phone1
                        elif cleaned_phone != phone1 and not phone2:
                            phone2 = cleaned_phone  # Assign the first available number to phone2
                        if phone1 and phone2:  # If both are assigned, stop iterating
                            break
                        
                    ##grabbing email address 1 through 5
                    email1 = email2 = email3 = email4 = email5 = ''
                    if persons.get('emailAddresses'):
                        email1 = persons.get('emailAddresses')[0].get('emailAddress')
                    if len(persons.get('emailAddresses')) > 1:
                        email2 = persons.get('emailAddresses')[1].get('emailAddress')
                    if len(persons.get('emailAddresses')) > 2:
                        email3 = persons.get('emailAddresses')[2].get('emailAddress')
                    if len(persons.get('emailAddresses')) > 3:
                        email4 = persons.get('emailAddresses')[3].get('emailAddress')
                    if len(persons.get('emailAddresses')) > 4:
                        email5 = persons.get('emailAddresses')[4].get('emailAddress')
                    ##grabbing the address information
                    if len(persons.get('addresses')) > 0:
                        for addr in persons.get('addresses'):
                            addr_order = str(addr.get('addressOrder'))
                            last_reported = addr.get('lastReportedDate')
                            if addr_order and last_reported:
                                last_reported = datetime.strptime(last_reported, '%m/%d/%Y')
                                # using last_reported to grab any addresses reported in the last (self.addr_years) years
                                if addr_order == '1' or (
                                        last_reported > (datetime.today() - timedelta(days=(self.addr_years * 365)))):
                                    street_number = addr.get('houseNumber')
                                    street_pre_direction = addr.get('streetPreDirection')
                                    street_name = addr.get('streetName')
                                    street_post_direction = addr.get('streetPostDirection')
                                    street_type = addr.get('streetType')
                                    street_unit = addr.get('unit')
                                    city = addr.get('city')
                                    state = addr.get('state')
                                    zipcode = addr.get('zip')
                                    addr_list = [street_number, street_pre_direction, street_name,
                                                 street_post_direction, street_type, street_unit]
                                    combined_addr = ' '.join(addr_list)
                                    combined_addr = ' '.join(combined_addr.split())
                                    # record_id, first_name, last_name, dob, combined_addr, city,
                                    # state, zipcode, phone1, phone2, email1, email2, email3, email4, email5
                                    response = {'record_id': self.id_, 'query_type': self.query_type,
                                                'addr_order': addr_order, 'first_name': first_name,
                                                'last_name': last_name,
                                                'dob': dob, 'street': combined_addr, 'city': city,
                                                'state': state, 'zipcode': zipcode, 'phone1': phone1, 'phone2': phone2,
                                                'email1': email1, 'email2': email2, 'email3': email3, 'email4': email4,
                                                'email5': email5, 'code': response_code}
                                    payload.append(response)
                else:
                    return [{'code': response_code, 'message': 'No Record Found.', 'query_type': self.query_type}]
            else:
                return [{'code': response_code, 'message': 'No Record Found.', 'query_type': self.query_type}]
            return payload if len(payload) > 0 else [
                {'code': response_code, 'message': 'No Record Found.', 'query_type': self.query_type}]
        return [{'code': -1, 'message': 'Insufficient Input to Append.'}]

    def _name_match(self, source_last_name, dest_last_name):
        # matches appended name info to make sure its the right person
        # is either last name in the other?
        # if not what is the levenshtein distance between them?
        match1 = source_last_name.lower() in dest_last_name.lower()
        match2 = dest_last_name.lower() in source_last_name.lower()
        combo_match = (match1 or match2)

        lev_distance = lev.distance(source_last_name.lower(), dest_last_name.lower())
        lev_valid = lev_distance <= self.distance
        verified_match = (combo_match or lev_valid)
        return verified_match


def validate_emails(emails, earlystop=True):
    """Validates emails and returns only those that are deliverable"""
    payload = [{"record_id": -1, "email_records": [{"email": email, "email_id": -1} for email in emails],
                "earlystop": earlystop,
                "days": MAX_EMAIL_CACHE_AGE}]
    response = requests.post(url=EMAIL_API_URL, json=payload, headers={"X-API-KEY": EMAIL_API_KEY})
    if response.status_code == 200:
        res = response.json()
        deliverable_emails = [record["email"] for record in res[0]["emails"] if record["status"] == "deliverable"]
        return deliverable_emails
    return []


def tracer_emails(provided_email, response, num_emails=5, earlystop=True):
    # print(response)
    all_emails = []
    for res in response:
        all_emails.extend([res.get(f"email{n}") for n in range(1, num_emails + 1)])

    # de-dupe except for provided_email (potentially)
    all_emails = list(set(all_emails))
    all_emails.insert(0, provided_email)

    all_emails = [email for email in all_emails if email]  # remove any None/"empty" values
    deliverable_emails = validate_emails(all_emails, earlystop=earlystop)

    if deliverable_emails:
        for res in response:
            res["valid_email"] = deliverable_emails[0]  # valid_email will be provided_email if it is valid
            for i, email in enumerate(deliverable_emails, 1):
                res[f"email{i}"] = email.lower()
            for j in range(len(deliverable_emails) + 1, num_emails + 1):
                res[f"email{j}"] = ''
    else:
        for res in response:
            for i in range(1, num_emails + 1):
                res[f"email{i}"] = ''

    return response


def update_tracers(index, response, column_name):
    result = False
    conn = psycopg2.connect(conn_str)
    query = """
                UPDATE dbo.customer_import
                SET %s = $$%s$$, %s_ts = now()
                WHERE 
                    id = cast($$%s$$ as uuid);
            """ % (column_name, json.dumps(response), column_name, index)
    try:
        # print(query)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        result = True
    except psycopg2.Error as e:
        print(e.pgerror)
        conn.rollback()
    conn.close()
    return result


def prepare_pii_message(index, response):
    conn = psycopg2.connect(conn_str)
    rows = []
    # print(len(response))
    if len(response) > 2:
        query = """
                    with cte_tracer_raw as 
                    (
                        select cast($$%s$$ as uuid) as id,
                        $$%s$$::json as tracers	
                    ),

                    cte_input as 
                    (
                        select 
                            id,
                            cust_hash,
                            first_name,
                            last_name,
                            address,
                            city,
                            state_cd as state,
                            zip_code as zipcode,
                            vin,
                            last_seen_date,
                            coalesce(first_name,'') || coalesce(last_name,'') || coalesce(address,'') || coalesce(city,'') || coalesce(state_cd,'') || coalesce(zip_code,'') as all_values,
                            1 as perference
                        from
                            dbo.customer_import
                        where
                            id = cast($$%s$$ as uuid)
                    ),

                    cte_tracer as 
                    (
                        select
                            id,
                            json_array_elements(tracers::json)->>'first_name' as first_name,
                            json_array_elements(tracers::json)->>'last_name' as last_name,
                            json_array_elements(tracers::json)->>'street' as address,
                            json_array_elements(tracers::json)->>'city' as city,
                            json_array_elements(tracers::json)->>'state' as state,
                            json_array_elements(tracers::json)->>'zipcode' as zipcode
                        from
                            cte_tracer_raw
                    ),

                    cte_tracer_hash as 
                    (
                        select
                            id,
                            md5(regexp_replace(lower(coalesce(first_name,'') || coalesce(last_name,'') || coalesce(address,'') || coalesce(city,'') || coalesce(state,'') || coalesce(zipcode,'')), '[^\w]+','','g'))::uuid as cust_hash,
                            coalesce(first_name,'') as first_name,
                            coalesce(last_name,'') as last_name,
                            coalesce(address,'') as address,
                            coalesce(city,'') as city,
                            coalesce(state,'') as state,
                            coalesce(zipcode,'') as zipcode,
                            '' as vin,
                            null::date as last_seen_date,
                            coalesce(first_name,'') || coalesce(last_name,'') || coalesce(address,'') || coalesce(city,'') || coalesce(state,'') || coalesce(zipcode,'') as all_values,
                            2 as perference
                        from 
                            cte_tracer
                    ),

                    cte_final_selection as 
                    (
                        select id, cust_hash, first_name, last_name, vin, last_seen_date, address, city, state, zipcode 
                        from
                        (
                            select id, cust_hash, first_name, last_name, address, city, state, zipcode, all_values, vin, last_seen_date, perference from cte_input
                            union all
                            select id, cust_hash, first_name, last_name, address, city, state, zipcode, all_values, vin, last_seen_date, perference from cte_tracer_hash
                        )a
                        where
                            all_values <> ''
                        order by perference
                    ),

                    cte_final as 
                    (
                        select 
                            id, first_name, last_name, vin, last_seen_date,
                            jsonb_agg(distinct jsonb_build_object(
                            'address',coalesce(address,''),
                            'city',coalesce(city,''),
                            'state',coalesce(state,''),
                            'zipcode',coalesce(zipcode,''))) as address
                        from 
                            cte_final_selection
                        group by id, first_name, last_name, vin, last_seen_date
                    )

                    select
                        json_agg(json_build_object('index', id,
                                'first_name', first_name,'last_name', last_name, 'vin', vin, 'last_seen_date', last_seen_date,
                                'address_list', address))
                    from
                        cte_final
                """ % (index, response, index)
    else:
        query = """
                    with cte_input as 
                    (
                        select 
                            id, 
                            cust_hash,
                            vin,
                            last_seen_date,
                            coalesce(first_name,'') as first_name, 
                            coalesce(last_name,'') as last_name,
                            jsonb_agg(distinct jsonb_build_object(
                                'address',coalesce(address,''),
                                'city',coalesce(city,''),
                                'state',coalesce(state_cd,''),
                                'zipcode',coalesce(zip_code,''))) as address
                        from
                            dbo.customer_import
                        where
                            id = cast($$%s$$ as uuid)
                        group by
                        	id, 
                            cust_hash, 
                            coalesce(first_name,''), 
                            coalesce(last_name,'')
                    )

                    select
                        json_agg(json_build_object('index', id,
                                'vin', vin, 'last_seen_date', last_seen_date, 'first_name', first_name,'last_name', last_name,
                                'address_list', address))
                    from
                        cte_input
                """ % (index)
    try:
        # print(query)
        cur = conn.cursor()
        cur.execute(query)
        records = cur.fetchone()
        if records:
            rows = records[0]
    except psycopg2.Error as e:
        print(e.pgerror)
    conn.close()
    return rows


def get_tracers(index):
    rows = []
    conn = psycopg2.connect(conn_str)
    query = """
                select 
                    tracers 
                from 
                    dbo.customer_import_search
                where
                    cust_hash = cast('{}' as uuid)
                    and coalesce(tracers,'') <> 'HOLD'
                order by event_ts desc
                limit 1;
            """.format(index)
    try:
        # print(query)
        cur = conn.cursor()
        cur.execute(query)
        records = cur.fetchone()
        if records:
            rows = json.loads(records[0])
    except psycopg2.Error as e:
        print(e.pgerror)
    conn.close()
    return rows


def is_tracer_processed(index):
    result = False
    conn = psycopg2.connect(conn_str)
    query = """
                select
                    cust_hash,
	                count(tracers) as row_count
                from
                    dbo.customer_import
                where
                    id = cast('{}' as uuid)
                group by cust_hash;
            """.format(index)
    try:
        cur = conn.cursor()
        cur.execute(query)
        records = cur.fetchone()
        if records:
            row_count = records[1]
            cust_hash = records[0]
            print('processed, cust_hash', row_count, cust_hash, index)
            if row_count == 1:
                result = True
    except psycopg2.Error as e:
        print(e.pgerror)
    finally:
        conn.close()
    return result


def queue_pii_query_request(message):
    sqs_client = boto3.client('sqs')
    response = sqs_client.send_message(QueueUrl=PII_QUERY_SQS_URL, MessageBody=json.dumps(message))


def delete_message(receipt_handle):
    sqs_client = boto3.client('sqs')
    response = sqs_client.delete_message(QueueUrl=TRACER_SQS_URL, ReceiptHandle=receipt_handle, )
    # print('delete_message ', receipt_handle)


def check_empty_results(message, response, requester_id):
    for resp in response:
        if resp.get('message') == 'No Record Found.':
            if resp.get('query_type') == 'address' and len(message['phone_number']) > 8:
                # api_tracker(conn_str, API_URL, message)
                response = tracers_broad_append(message['index'], '', '', '', '', message['phone_number'],
                                                message['email'], requester_id)
            elif resp.get('query_type') == 'address' and len(message['phone_number']) < 8 and len(
                    message['email']) > 3:
                # api_tracker(conn_str, API_URL, message)
                response = tracers_broad_append(message['index'], '', '', '', '', '', message['email'], requester_id)
            elif resp.get('query_type') == 'phone' and len(message['email']) > 3:
                # api_tracker(conn_str, API_URL, message)
                response = tracers_broad_append(message['index'], '', '', '', '', '', message['email'], requester_id)
    return response


def get_appended_pii(message, requester_id):
    if ENV_TYPE == 'DEV':
        response = get_tracers(message['cust_hash'])
    else:
        response = tracers_broad_append(message['index'], message['first_name'], message['last_name'],
                                        message['street'], message['zipcode'], message['phone_number'],
                                        message['email'], requester_id)
        # If address returns no records then try with phone number
        response = check_empty_results(message, response, requester_id) if len(response) == 1 else response
        # If phone number returns no records then try with email
        response = check_empty_results(message, response, requester_id) if len(response) == 1 else response
        # Validate Emails
        if message['config'].get('validate_emails'):
            response = tracer_emails(message["email"], response)
    update_tracers(message['index'], response, 'tracers')
    return response


def generate_pii_vehicle_registrations(message, response, requester_id):
    pii_message = prepare_pii_message(message['index'], json.dumps(response))

    if message['config'].get("blind_state"):
        pii_message = [msg for msg in pii_message if msg["vin"]]

        # send messages that have vin
        if pii_message:
            pii_message[0]["requester_id"] = requester_id
            queue_pii_query_request(pii_message)
        else:
            print(f"No VIN for id: {message['index']}")
            update_tracers(message['index'], response, 'tracers')
            update_tracers(message['index'], [], 'pii_query')
            update_tracers(message['index'], [], 'market_check')  # dependent on PPI Results
            update_tracers(message['index'], [], 'virtual_data')  # dependent on PPI Results
            update_tracers(message['index'], [], 'projection_data')  # dependent on PPI Results
    else:
        # print(pii_message)
        if pii_message:
            pii_message[0]["requester_id"] = requester_id
        queue_pii_query_request(pii_message)


def tracer_sqs_consumer(event, context):
    message = json.loads(event['Records'][0]['body'])
    receipt_handle = event['Records'][0]['receiptHandle']
    delete_message(receipt_handle)

    requester_id = message['config'].get('requester_id') or "not_provided"
    
    if 'append_pii' in message['config']:
        if message['config']['append_pii'] and message['config']['pii_vehicle_registrations']:
            processed = is_tracer_processed(message['index'])
            if not processed:
                response = get_appended_pii(message, requester_id)
                generate_pii_vehicle_registrations(message, response, requester_id)
            else:
                print('I already got results why Im here?')
        elif not message['config']['append_pii'] and message['config']['pii_vehicle_registrations']:
            response = []
            update_tracers(message['index'], response, 'tracers')
            generate_pii_vehicle_registrations(message, response, requester_id)
        elif message['config']['append_pii'] and not message['config']['pii_vehicle_registrations']:
            processed = is_tracer_processed(message['index'])
            if not processed:
                _ = get_appended_pii(message, requester_id)
                update_tracers(message['index'], [], 'pii_query')
                update_tracers(message['index'], [], 'market_check')  # dependent on PPI Results
                update_tracers(message['index'], [], 'virtual_data')  # dependent on PPI Results
                update_tracers(message['index'], [], 'projection_data')  # dependent on PPI Results
            else:
                print('I already got results why Im here?')
        else:
            response = []
            update_tracers(message['index'], response, 'tracers')
            update_tracers(message['index'], response, 'pii_query')
            update_tracers(message['index'], response, 'market_check')  # dependent on PPI Results
            update_tracers(message['index'], response, 'virtual_data')  # dependent on PPI Results
            update_tracers(message['index'], response, 'projection_data')  # dependent on PPI Results

