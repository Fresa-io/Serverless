import os
import io
import sys
import json
import time
import base64
import boto3
import botocore
import psycopg2
import requests
import datetime
import pandas as pd
from io import StringIO
from utility import api_tracker

RDS_HOST = os.environ['RDS_HOST'].strip()
RDS_PORT = os.environ['RDS_PORT'].strip()
RDS_DB = os.environ['RDS_DB'].strip()
RDS_USER = os.environ['RDS_USER'].strip()
RDS_PWD = os.environ['RDS_PWD'].strip()
AWS_ACCESS_KEY_ID = os.environ['ACCESS_KEY'].strip()
AWS_SECRET_ACCESS_KEY = os.environ['SECRET_ACCESS'].strip()
AWS_BUCKET_NAME = os.environ['AWS_BUCKET_NAME'].strip()
COMPLETE_COLUMN = os.environ['COMPLETE_COLUMN'].strip()

conn_str = "host=%s port=%s dbname=%s user=%s password=%s" % (RDS_HOST, RDS_PORT, RDS_DB, RDS_USER, RDS_PWD)


def tracer_import_status(trace_id):
    output_summary = {}
    result = False
    conn = psycopg2.connect(conn_str)
    query = """
                with cte_raw_input as 
                (
                    select
                        a.trace_id,
                        b.id,
                        cast(a.create_ts as varchar) as create_ts,
                        a.import_file,
                        a.records as import_file_records,
                        a.unique_records as import_file_unique_records,
                        a.import_stats as import_status,
                        b.cust_id,
                        lower(coalesce(first_name,'')||' '||coalesce(last_name,'')) as cust_name,
                        lower(coalesce(address,'')||' '||coalesce(city,'')||' '||coalesce(state_cd,'')||' '||coalesce(zip_code,'')) as address, 
                        b.email,
                        b.phone1,
                        b.phone2,
                        case when b.%s is null then 0 else 1 end as processed
                    from
                        dbo.trace_import a
                        inner join dbo.customer_import b
                        on a.trace_id = b.trace_id
                    where
                        a.trace_id = cast($$%s$$ as uuid)
                ),

                cte_trace as 
                (
                    select
                            a.trace_id,
                            a.id,
                            json_array_elements(coalesce(case when tracers = '[]' then '[{}]' else tracers end::json,'[{}]'))->>'phone1' as appended_phone1,
                            json_array_elements(coalesce(case when tracers = '[]' then '[{}]' else tracers end::json,'[{}]'))->>'phone2' as appended_phone2,
                            json_array_elements(coalesce(case when tracers = '[]' then '[{}]' else tracers end::json,'[{}]'))->>'email1' as appended_email1,
                            json_array_elements(coalesce(case when tracers = '[]' then '[{}]' else tracers end::json,'[{}]'))->>'first_name' as appended_first_name,
                            json_array_elements(coalesce(case when tracers = '[]' then '[{}]' else tracers end::json,'[{}]'))->>'last_name' as appended_last_name
                        from
                            dbo.customer_import a 
                        where
                            a.trace_id = cast($$%s$$ as uuid)
                ),

                cte_address as 
                (
                    select
                        trace_id,
                        id,
                        lower(coalesce(address,'')||' '||coalesce(city,'')||' '||coalesce(state,'')||' '||coalesce(zipcode,'')) as appended_address
                    from
                        (select
                            trace_id,
                            id,
                            json_array_elements(coalesce(pii_query::json,'[{}]'))->>'address' as address,
                            json_array_elements(coalesce(pii_query::json,'[{}]'))->>'city' as city,
                            json_array_elements(coalesce(pii_query::json,'[{}]'))->>'state' as state,
                            json_array_elements(coalesce(pii_query::json,'[{}]'))->>'zipcode' as zipcode
                        from
                            dbo.customer_import 
                        where
                            trace_id = cast($$%s$$ as uuid)
                        )cte_address_raw
                        where length(coalesce(address,'')||coalesce(city,'')||coalesce(state,'')||coalesce(zipcode,''))>0
                ),

                cte_vehicles as 
                (
                    select
                        id,
                        trace_id,
                        jsonb_array_elements(coalesce(pii_query::jsonb,'[]'))->>'vin' as vin
                    from
                        dbo.customer_import 
                    where
                        trace_id = cast($$%s$$ as uuid)
                ),

                cte_customer_summary as 
                (
                    select
                        a.trace_id,
                        a.id,
                        a.cust_name,
                        a.import_file,
                        a.create_ts,
                        a.import_status,
                        a.import_file_records,
                        a.import_file_unique_records,
                        a.processed,
                        a.email,
                        jsonb_agg(distinct coalesce(b.appended_email1,'')) filter (where coalesce(b.appended_email1,'') <> '') as appended_email,
                        a.phone1, 
                        a.phone2,  
                        jsonb_agg(distinct coalesce(b.appended_phone1,'')) filter (where replace(coalesce(b.appended_phone1,''),'-','') <> replace(coalesce(a.phone1,''),'-','') and replace(coalesce(b.appended_phone1,''),'-','') <> replace(coalesce(a.phone2,''),'-','') and coalesce(appended_phone1,'') <> '') ||
                        jsonb_agg(distinct coalesce(b.appended_phone2,'')) filter (where replace(coalesce(b.appended_phone2,''),'-','') <> replace(coalesce(a.phone1,''),'-','') and replace(coalesce(b.appended_phone2,''),'-','') <> replace(coalesce(a.phone2,''),'-','') and coalesce(appended_phone2,'') <> '') as appended_phone,
                        jsonb_agg(distinct lower(coalesce(b.appended_first_name,'')|| ' ' ||coalesce(b.appended_last_name,''))) filter( where lower(coalesce(b.appended_first_name,'')|| ' ' ||coalesce(b.appended_last_name,'')) <> coalesce(a.cust_name,'') ) as appended_name,
                        a.address,
                        jsonb_agg(distinct coalesce(c.appended_address,'')) filter(where coalesce(a.address,'')<>coalesce(c.appended_address,'')) as appended_address,
                        jsonb_agg(distinct d.vin) filter(where d.vin is not null) as vehicles
                    from
                        cte_raw_input a

                        left outer join cte_trace b
                        on a.id = b.id and a.trace_id = b.trace_id

                        left outer join cte_address c
                        on a.id = c.id and a.trace_id = c.trace_id

                        left outer join cte_vehicles d
                        on a.id = d.id and a.trace_id = d.trace_id
                    group by
                        a.trace_id,
                        a.id,
                        a.cust_name,
                        a.import_file,
                        a.create_ts,
                        a.import_status,
                        a.import_file_records,
                        a.import_file_unique_records,
                        a.processed,
                        a.email,
                        a.phone1, 
                        a.phone2,
                        a.address
                ),

                cte_final as
                (
                    select 
                        trace_id,
                        max(import_file) as import_file,
                        max(create_ts) as create_ts,
                        max(import_status) as import_status,
                        max(import_file_records) as import_file_records,
                        max(import_file_unique_records) as import_file_unique_records,
                        sum(processed) as processed,
                        case when max(import_file_unique_records) = sum(processed) then 'Complete' else 'Waiting to finish import process.!' end as processed_status,
                        case when max(import_file_unique_records) = sum(processed) then 1 else -1 end as code,
                        count(case when length(trim(cust_name))>0 then 1 end) as names_in,
                        sum(jsonb_array_length(appended_name)) as names_out,
                        sum(case 
                            when (coalesce(phone1,'') <> coalesce(phone2,'') and (coalesce(phone1,'') <> '' and coalesce(phone2,'') <> '')) then 2
                            when (coalesce(phone1,'') <> coalesce(phone2,'') and (coalesce(phone1,'') <> '' and coalesce(phone2,'') = '')) then 1
                            when (coalesce(phone1,'') <> coalesce(phone2,'') and (coalesce(phone1,'') = '' and coalesce(phone2,'') <> '')) then 1
                            when (coalesce(phone1,'') <> coalesce(phone2,'') and (coalesce(phone1,'') = '' and coalesce(phone2,'') = '')) then 0
                            else 0 
                        end) as phones_in,	
                        sum(jsonb_array_length(appended_phone)) as phones_out,
                        count(case when length(trim(email))>0 then 1 end) as emails_in,
                        sum(jsonb_array_length(appended_email)) as emails_out,
                        count(case when length(trim(address))>0 then 1 end) as addresses_in,
                        sum(jsonb_array_length(appended_address)) as addresses_out,
                        sum(jsonb_array_length(vehicles)) as vehicles_out
                    from 
                        cte_customer_summary
                    group by
                        trace_id
                ),

                cte_output_summary as 
                (
                    select
                        trace_id,
                        jsonb_build_object(
                            'trace_id',trace_id,
                            'code',code,
                            'import_file_name',import_file,
                            'import_file_rows',import_file_records,
                            'import_file_unique_rows',import_file_unique_records,
                            'import_file_status',import_status,
                            'processed_rows',processed,
                            'processed_file_status',processed_status,
                            'names_in',names_in,
                            'names_out',names_out,
                            'addresses_in',addresses_in,
                            'addresses_out',addresses_out,
                            'phones_in',phones_in,
                            'phones_out',phones_out,
                            'emails_in',emails_in,
                            'emails_out',emails_out,
                            'vehicles_out',vehicles_out
                        ) as output_summary
                    from
                        cte_final
                )

                update dbo.trace_import a 
                    set output_summary = b.output_summary,  output_summary_ts = now()
                from 
                    cte_output_summary b 
                where
                    a.trace_id = b.trace_id
                returning a.output_summary;
            """ % (COMPLETE_COLUMN, trace_id, trace_id, trace_id, trace_id)
    try:
        # print(query)
        cur = conn.cursor()
        cur.execute(query)
        records = cur.fetchone()
        conn.commit()
        if records:
            output_summary = json.loads(records[0])
            # print(output_summary)
            if output_summary['processed_file_status'] == 'Complete':
                result = True
    except psycopg2.Error as e:
        print(e.pgerror)
    conn.close()
    return result, output_summary


def check_tracer_import_status(trace_id):
    output_summary = {}
    result = False
    conn = psycopg2.connect(conn_str)

    query = """
                select 
                    output_summary 
                from 
                    dbo.trace_import 
                where 
                    trace_id = cast('{}' as uuid)
            """.format(trace_id)
    try:
        # print(query)
        cur = conn.cursor()
        cur.execute(query)
        records = cur.fetchone()
        if records:
            if records[0]:
                output_summary = json.loads(records[0])
                print(output_summary)
                result = True
    except psycopg2.Error as e:
        print(e.pgerror)
    conn.close()
    return result, output_summary


def tracer_import_output(trace_id, output_file):
    rows = []
    conn = psycopg2.connect(conn_str)
    query = """
                with cte_raw as 
                (
                    select
                        a.trace_id,
                        cast(a.create_ts as varchar) as create_ts,x
                        a.import_file,
                        a.records as import_file_records,
                        a.unique_records as import_file_unique_records,
                        a.import_stats as import_status,
                        b.id,
                        b.cust_id,
                        coalesce(b.first_name,'')||'~#~'||coalesce(b.last_name,'') as cust_name,
                        b.first_name,
                        b.last_name,
                        b.address,
                        b.city,
                        b.state_cd,
                        b.zip_code,
                        coalesce(address,'')||'~#~'||coalesce(city,'')||'~#~'||coalesce(state_cd,'')||'~#~'||coalesce(zip_code,'') as full_address, 
                        b.email,
                        b.phone1,
                        b.phone2,
                        json_array_elements(coalesce(case when tracers = '[]' then '[{}]' else tracers end::json,'[{}]'))->>'phone1' as appended_phone1,
                        json_array_elements(coalesce(case when tracers = '[]' then '[{}]' else tracers end::json,'[{}]'))->>'phone2' as appended_phone2,
                        json_array_elements(coalesce(case when tracers = '[]' then '[{}]' else tracers end::json,'[{}]'))->>'email1' as appended_email1,
                        json_array_elements(coalesce(case when tracers = '[]' then '[{}]' else tracers end::json,'[{}]'))->>'valid_email' as valid_email,
                        json_array_elements(coalesce(case when tracers = '[]' then '[{}]' else tracers end::json,'[{}]'))->>'first_name' as appended_first_name,
                        json_array_elements(coalesce(case when tracers = '[]' then '[{}]' else tracers end::json,'[{}]'))->>'last_name' as appended_last_name
                    from
                        dbo.trace_import a
                        inner join dbo.customer_import b
                        on a.trace_id = b.trace_id
                    where
                        a.trace_id = cast($$%s$$ as uuid)
                ),

                cte_address_raw as 
                (
                    select
                        trace_id,
                        id,
                        coalesce(address,'')||'~#~'||coalesce(city,'')||'~#~'||coalesce(state,'')||'~#~'||coalesce(zipcode,'') as appended_address
                    from
                        (select
                            trace_id,
                            id,
                            json_array_elements(coalesce(pii_query::json,'[{}]'))->>'address' as address,
                            json_array_elements(coalesce(pii_query::json,'[{}]'))->>'city' as city,
                            json_array_elements(coalesce(pii_query::json,'[{}]'))->>'state' as state,
                            json_array_elements(coalesce(pii_query::json,'[{}]'))->>'zipcode' as zipcode
                        from
                            dbo.customer_import 
                        where
                            trace_id = cast($$%s$$ as uuid)
                        )cte_address_raw
                        where length(coalesce(address,'')||coalesce(city,'')||coalesce(state,'')||coalesce(zipcode,''))>0
                ),

                cte_tracer as 
                (
                    select
                        a.trace_id,
                        a.create_ts,
                        a.import_file,
                        a.import_file_records,
                        a.import_file_unique_records,
                        a.import_status,
                        a.id,
                        a.cust_id,
                        a.first_name,
                        a.last_name,
                        a.address,
                        a.city,
                        a.state_cd,
                        a.zip_code,
                        a.email,
                        a.phone1,
                        a.phone2,
                        jsonb_agg(distinct coalesce(a.appended_phone1,'')) filter (where replace(coalesce(a.appended_phone1,''),'-','') <> replace(coalesce(a.phone1,''),'-','') and replace(coalesce(a.appended_phone1,''),'-','') <> replace(coalesce(a.phone2,''),'-','') and coalesce(a.appended_phone1,'') <> '') ||
                        jsonb_agg(distinct coalesce(a.appended_phone2,'')) filter (where replace(coalesce(a.appended_phone2,''),'-','') <> replace(coalesce(a.phone1,''),'-','') and replace(coalesce(a.appended_phone2,''),'-','') <> replace(coalesce(a.phone2,''),'-','') and coalesce(a.appended_phone2,'') <> '') as appended_phone,
                        
                        CASE
                            WHEN coalesce(a.valid_email,'') = '' THEN NULL
                            WHEN lower(coalesce(a.valid_email,'')) = lower(coalesce(a.email,'')) 
                                THEN jsonb_build_array(a.valid_email)
                            ELSE jsonb_agg(distinct a.valid_email) FILTER (
                                WHERE coalesce(a.valid_email,'') <> ''
                                AND lower(coalesce(a.valid_email,'')) <> lower(coalesce(a.email,''))
                            )
                        END AS appended_email,

                        jsonb_agg(distinct coalesce(a.appended_first_name,'')|| '~#~' ||coalesce(a.appended_last_name,'')) filter( where lower(coalesce(a.appended_first_name,'')|| '~#~' ||coalesce(a.appended_last_name,'')) <> lower(coalesce(a.cust_name,''))) as appended_name,
                        jsonb_agg(distinct coalesce(b.appended_address,'')) filter(where coalesce(a.full_address,'') <> coalesce(b.appended_address,'')) as appended_address
                    from
                        cte_raw a 
                        left outer join cte_address_raw b
                        on a.trace_id = b.trace_id
                        and a.id = b.id
                    group by
                        a.trace_id,
                        a.create_ts,
                        a.import_file,
                        a.import_file_records,
                        a.import_file_unique_records,
                        a.import_status,
                        a.id,
                        a.cust_id,
                        a.first_name,
                        a.last_name,
                        a.address,
                        a.city,
                        a.state_cd,
                        a.zip_code,
                        a.email,
                        a.phone1,
                        a.phone2
                ),

                cte_registrations_raw as 
                (
                    select
                        id,
                        trace_id,
                        jsonb_array_elements(coalesce(pii_query::jsonb,'[]')) as registration
                    from
                        dbo.customer_import 
                    where
                        trace_id = cast($$%s$$ as uuid)
                ),

                cte_virtual_data_raw as 
                (
                    select
                        id,
                        trace_id,
                        jsonb_array_elements(coalesce(virtual_data::jsonb,'[]'))->>'vin' as vin,
                        jsonb_array_elements(coalesce(virtual_data::jsonb,'[]'))->>'amount_financed' as amount_financed,
                        jsonb_array_elements(coalesce(virtual_data::jsonb,'[]'))->>'cash_price' as cash_price,
                        jsonb_array_elements(coalesce(virtual_data::jsonb,'[]'))->>'interest_rate' as interest_rate,
                        jsonb_array_elements(coalesce(virtual_data::jsonb,'[]'))->>'term' as term,
                        jsonb_array_elements(coalesce(virtual_data::jsonb,'[]'))->>'deal_type' as deal_type
                    from
                        dbo.customer_import 
                    where
                        trace_id = cast($$%s$$ as uuid)
                ),

                cte_projection_data_raw as 
                (
                    select
                        id,
                        trace_id,
                        jsonb_array_elements(coalesce(projection_data::jsonb,'[]'))->>'vin' as vin,
                        jsonb_array_elements(coalesce(projection_data::jsonb,'[]'))->>'current_value' as current_value,
                        jsonb_array_elements(coalesce(projection_data::jsonb,'[]'))->>'depreciation' as depreciation,
                        jsonb_array_elements(coalesce(projection_data::jsonb,'[]'))->>'equity' as equity,
                        jsonb_array_elements(coalesce(projection_data::jsonb,'[]'))->>'maturity_date' as maturity_date,
                        jsonb_array_elements(coalesce(projection_data::jsonb,'[]'))->>'mileage' as mileage,
                        jsonb_array_elements(coalesce(projection_data::jsonb,'[]'))->>'payment' as payment,
                        jsonb_array_elements(coalesce(projection_data::jsonb,'[]'))->>'payments_made' as payments_made,
                        jsonb_array_elements(coalesce(projection_data::jsonb,'[]'))->>'payments_remaining' as payments_remaining,
                        jsonb_array_elements(coalesce(projection_data::jsonb,'[]'))->>'payoff' as payoff
                    from
                        dbo.customer_import 
                    where
                        trace_id = cast($$%s$$ as uuid)
                ),

                cte_market_check as 
                (
                    select
                        id,
                        trace_id,
                        jsonb_array_elements(coalesce(market_check::jsonb,'[]'))->>'vin' as vin,
                        jsonb_array_elements(coalesce(market_check::jsonb,'[]'))->>'msrp' as original_msrp
                    from
                        dbo.customer_import 
                    where
                        trace_id = cast($$%s$$ as uuid)
                ),

                cte_registration as
                (
                    select
                        id, 
                        trace_id,
                        json_agg(registrations) as registrations
                    from
                    (
                        select
                            a.id,
                            a.trace_id,
                            a.registration ||
                                jsonb_build_object('listing_results',jsonb_build_object('original_msrp',m.original_msrp::real))||
                                jsonb_build_object('virtualized_financial_data',
                                    jsonb_build_object('amount_financed',b.amount_financed::real,
                                                      'cash_price',b.cash_price::real,
                                                      'interest_rate',b.interest_rate::real,
                                                      'term',b.term::real,
                                                      'deal_type',b.deal_type)) ||
                                jsonb_build_object('projected_financial_status',
                                    jsonb_build_object('current_value',c.current_value::real,
                                                      'depreciation',c.depreciation::real,
                                                      'equity',c.equity::real,
                                                      'maturity_date',to_char(cast(c.maturity_date as date), 'YYYY-MM-DD'),
                                                      'mileage',c.mileage::real,
                                                      'payment',c.payment::real,
                                                      'payments_made',c.payments_made::real,
                                                      'payments_remaining',c.payments_remaining::real,
                                                      'payoff',c.payoff::real))as registrations
                        from
                            cte_registrations_raw a 

                            left outer join cte_virtual_data_raw b
                            on a.registration->>'vin' = b.vin
                            and a.id = b.id
                            and a.trace_id = b.trace_id

                            left outer join cte_projection_data_raw c
                            on a.registration->>'vin' = c.vin
                            and a.id = c.id
                            and a.trace_id = c.trace_id

                            left outer join cte_market_check m
                            on a.registration->>'vin' = m.vin
                            and a.id = m.id
                            and a.trace_id = m.trace_id
                        where
                            a.registration->>'vin' is not null
                    )b group by id, trace_id
                ),

                cte_appended_address as 
                (
                    select
                        id,
                        trace_id,
                        json_agg(appended_address) as appended_address
                    from
                        (select
                            id,
                            trace_id,
                            json_build_object(
                                'address',split_part(jsonb_array_elements_text(appended_address)::varchar, '~#~', 1),
                                'city',split_part(jsonb_array_elements_text(appended_address)::varchar, '~#~', 2),
                                'state',split_part(jsonb_array_elements_text(appended_address)::varchar, '~#~', 3),
                                'zipcode',split_part(jsonb_array_elements_text(appended_address)::varchar, '~#~', 4)) as appended_address
                        from
                            cte_tracer)a
                    group by id, trace_id
                ),

                cte_appended_names as 
                (
                    select
                        id,
                        trace_id,
                        json_agg(appended_name) as appended_name
                    from
                        (select
                            id,
                            trace_id,
                            json_build_object(
                                'first_name',split_part(jsonb_array_elements_text(appended_name)::varchar, '~#~', 1),
                                'last_name',split_part(jsonb_array_elements_text(appended_name)::varchar, '~#~', 2),
                                'full_name',replace(jsonb_array_elements_text(appended_name)::varchar,'~#~',' ')) as appended_name
                        from
                            cte_tracer)a
                    group by id, trace_id
                ),

                cte_tracer_all as 
                (
                    select 
                        a.trace_id,
                        a.create_ts,
                        a.import_file,
                        a.import_file_records,
                        a.import_file_unique_records,
                        a.import_status,
                        a.id,
                        a.cust_id,
                        a.first_name,
                        a.last_name,
                        a.address,
                        a.city,
                        a.state_cd,
                        a.zip_code,
                        a.email,
                        a.phone1,
                        a.phone2,
                        n.appended_name,
                        a.appended_phone,
                        a.appended_email,
                        d.appended_address,
                        coalesce(c.registrations::json,'[]') as results
                    from
                        cte_tracer a

                        left outer join cte_registration c
                        on a.trace_id = c.trace_id
                        and a.id = c.id

                        left outer join cte_appended_address d
                        on a.trace_id = d.trace_id
                        and a.id = d.id

                        left outer join cte_appended_names n
                        on a.trace_id = n.trace_id
                        and a.id = n.id
                ),

                cte_records as 
                (
                    select 
                        trace_id,
                        create_ts,
                        import_file,
                        import_file_records,
                        import_file_unique_records,
                        import_status,
                        json_agg(json_build_object(
                                'cust_id',cust_id,
                                'first_name',first_name,
                                'last_name',last_name,
                                'address',address,
                                'city',city,
                                'state_cd',state_cd,
                                'zip_code',zip_code,
                                'email',email,
                                'phone1',phone1,
                                'phone2',phone2,
                                'appended_name',appended_name,
                                'appended_phone',appended_phone,
                                'appended_email',appended_email,
                                'appended_address',appended_address,
                                'vehicles',results)) records
                    from 
                        cte_tracer_all
                    group by
                        trace_id,
                        create_ts,
                        import_file,
                        import_file_records,
                        import_file_unique_records,
                        import_status
                )


                select
                    json_build_object(
                        'trace_id',trace_id,
                        'create_ts',create_ts,
                        'import_file_name',import_file,
                        'import_file_records',import_file_records,
                        'import_file_unique_records',import_file_unique_records,
                        'import_status',import_status,
                        'records',records) as results
                from
                    cte_records;
            """ % (trace_id, trace_id, trace_id, trace_id, trace_id, trace_id)
    try:
        # print(query)
        # cur = conn.cursor()
        # cur.execute(query)
        # records = cur.fetchone()
        # if records:
        #     rows = records[0]
        # Save Results to S3
        requests_df = pd.read_sql_query(query, conn)
        json_buffer = io.StringIO()
        requests_df.to_json(json_buffer, orient='records')
        s3_resource = boto3.resource('s3')
        s3_resource.Object(AWS_BUCKET_NAME, output_file).put(Body=json_buffer.getvalue())
    except psycopg2.Error as e:
        print(e.pgerror)
    conn.close()
    return rows


def tracer_import_results(event, context):
    # TODO implement
    # print(event)
    isBase64Encoded = event["isBase64Encoded"]
    bodyStr = event["body"]
    if isBase64Encoded:
        decodestr = base64.b64decode(bodyStr)
        user_data = json.loads(decodestr)
    else:
        user_data = json.loads(bodyStr)

    # -- remote_ip not used here --
    # if event['headers'].get('X-Forwarded-For'):
    #     remote_ip = event['headers']['X-Forwarded-For'].replace(event['requestContext']['identity']['sourceIp'],
    #                                                             '').replace(',', '').strip()
    #     if remote_ip == '':
    #         remote_ip = event['headers']['X-Forwarded-For']
    # else:
    #     if event['requestContext'].get('http'):
    #         remote_ip = event['requestContext']['http']['sourceIp']
    #     else:
    #         remote_ip = event['requestContext']['identity']['sourceIp']

    # print(user_data)
    api_tracker(conn_str, 'tracer_import_results', user_data)
    if 'trace_id' in user_data:
        trace_id = user_data['trace_id']
        result, output_summary = check_tracer_import_status(trace_id)
        if result == False:
            result, output_summary = tracer_import_status(trace_id)
        if output_summary['code'] == -1:
            response = output_summary
        else:
            import_file_folder, import_file_name = os.path.split(output_summary['import_file_name'])
            output_file = os.path.join(import_file_folder, import_file_name.split('.')[0] + "-result" + ".json")
            # rows = tracer_import_output(trace_id, output_file)
            output_summary['json_output_file'] = output_file
            output_summary['csv_output_file'] = output_file.replace(".json", ".csv")
            response = output_summary
    else:
        response = {'code': -1, 'message': 'Invalid Payload.!'}

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response)
    }
