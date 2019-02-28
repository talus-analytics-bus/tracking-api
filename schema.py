import functools
# from enum import Enum
from graphene import Schema, ObjectType, String, ID, Int, Float, List, Field
# from graphene.types.json import JSONString
# List, Float, Field, Union
# from graphene.types.datetime import Date
from pony.orm import db_session, Database
from pony.orm.core import Entity

from models import Company as c
from models import CustomerZone as cz
# from pandas.io.json import json_normalize

db = Database()


def recursive_to_dict(dataset, _has_iterated=False, **kwargs):
    if isinstance(dataset, Entity):
        dataset = dataset.to_dict(**kwargs)

    delete_these = []
    for key, value in dataset.items():
        if _has_iterated:
            if isinstance(value, (list, tuple)):
                for iterable in value:
                    if isinstance(iterable, Entity):
                        delete_these.append(key)
                        break
                continue
        else:
            if isinstance(value, (list, tuple)):
                value_list = []
                for iterable in value:
                    if isinstance(iterable, Entity):
                        value_list.append(recursive_to_dict(iterable, True,
                                                            **kwargs))
                dataset[key] = value_list

        if isinstance(value, Entity) and not _has_iterated:
            dataset[key] = recursive_to_dict(value, True, **kwargs)

        elif isinstance(value, Entity) and _has_iterated:
            delete_these.append(key)

    for deletable_key in delete_these:
        del dataset[deletable_key]

    return dataset


def cached(func):
    """ Magic memoizing cache """
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = str(kwargs)
        if key in cache:
            return cache[key]

        results = func(*args, **kwargs)
        cache[key] = results
        return results

    return wrapper


@db_session
def get_company(id):

    company = c[id]

    policy_count = 0
    tiv = 0
    policies = []
    for policy in company.policies:
        policy_count += 1
        tiv += policy.tiv
        policies.append(policy)

    zones = []
    for zone in company.zones:
        zones.append(zone)

    return Company(
                 id=company.id,
                 name=company.name,
                 policy_count=policy_count,
                 tiv=tiv,
                 policies=policies,
                 zones=zones)


@db_session
def get_customer_zone(id):

    customer_zone = cz[id]

    policies = []
    for policy in customer_zone.policies:
        policies.append(policy)

    breakdown = customer_zone.breakdown
    _ = breakdown.none_percent
    _ = breakdown.minimal_percent
    _ = breakdown.moderate_percent
    _ = breakdown.high_percent
    _ = breakdown.extreme_percent

    customer = customer_zone.customer
    _ = customer.name

    zone = customer_zone.zone
    _ = zone.id
    _ = zone.size
    _ = zone.state
    _ = zone.area

    return CustomerZone(
                id=customer_zone.id,
                customer=customer,
                zone=zone,
                policies=policies,
                policy_count=customer_zone.policy_count,
                tiv=customer_zone.tiv,
                pml=customer_zone.pml,
                pml_to_tiv=customer_zone.pml / customer_zone.tiv,
                pml_50=customer_zone.pml_50,
                pml_100=customer_zone.pml_100,
                pml_250=customer_zone.pml_250,
                mean_bp=customer_zone.mean_bp,
                breakdown=breakdown,
                )


class Breakdown(ObjectType):
    id = ID()
    none_percent = Float()
    minimal_percent = Float()
    moderate_percent = Float()
    high_percent = Float()
    extreme_percent = Float()


class Zone(ObjectType):
    id = ID()
    size = String()
    state = String()
    area = Float()
    zips = List(lambda: Zip)
    fires = List(lambda: Fire)


class Policy(ObjectType):
    company = Field(lambda: Company)
    id = ID()
    status = String()
    address = String()
    city = String()
    county = String()
    state = String()
    zip = String()
    tiv = Int()
    latitude = Float()
    longitude = Float()
    model_type = String()
    loss_type = String()
    overall_risk_class = String()
    severity_class = String()
    frequency_class = String()
    distance_to_high_hazard = Float()
    customer_zone = Field(lambda: CustomerZone)


class CustomerZone(ObjectType):
    id = ID()
    customer = Field(lambda: Company)
    zone = Field(Zone)
    policies = List(Policy)
    policy_count = Int()
    tiv = Float()
    pml = Float()
    pml_to_tiv = Float()
    pml_50 = Float()
    pml_100 = Float()
    pml_250 = Float()
    mean_bp = Float()
    breakdown = Field(Breakdown)


class Company(ObjectType):
    id = ID()
    name = String()
    tiv = Float()
    policy_count = Int()
    policies = List(Policy)
    zones = List(CustomerZone)


class Fire(ObjectType):
    id = ID()
    name = String()


class Zip(ObjectType):
    id = ID()
    code = String()


class Query(ObjectType):

    company = Field(
        Company,
        id=ID(required=True),
    )

    customer_zone = Field(
        CustomerZone,
        id=ID(required=True),
    )

    @cached
    @db_session
    def resolve_company(self, info, id=1):
        company_data = get_company(id)
        return company_data

    @cached
    @db_session
    def resolve_customer_zone(self, info, id=1):
        cz_data = get_customer_zone(id)
        return cz_data


schema = Schema(query=Query, types=[Company, CustomerZone])
