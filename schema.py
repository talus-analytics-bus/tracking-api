import functools
# from enum import Enum
from graphene import Schema, ObjectType, String, Int, Float, List, Field, Boolean

from models import FundingJSON

funders, recipients, all_funders, all_recipients = FundingJSON()


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


def parse_capacities(cap_list):
    parsed_list = []
    for capacity in cap_list:
        parsed_list.append(CoreCapacity(name=capacity))

    return parsed_list


def parse_trans(trans_list):
    parsed_list = []
    for transaction in trans_list:
        parsed_list.append(
            Transaction(
                type=transaction['type'],
                amount=transaction['amount'],
                cy=transaction['cy'],
                currency=transaction['currency'],
            )
        )

    return parsed_list


def parse_project(proj):
    transactions = parse_trans(proj['transactions'])
    capacities = parse_capacities(proj['core_capacities'])

    return Project(
        project_id=proj['project_id'],
        project_name=proj['project_name'],
        funder_ref=proj['funder_ref'],
        donor_sector=proj['donor_sector'],
        donor_code=proj['donor_code'],
        donor_name=proj['donor_name'],
        recipient_country=proj['recipient_country'],
        recipient_sector=proj['recipient_sector'],
        recipient_name=proj['recipient_name'],
        transactions=transactions,
        total_committed=proj['total_committed'],
        total_spent=proj['total_spent'],
        total_currency=proj['total_currency'],
        # source = Field(Source),
        # spent_by_year = Field(ByYear),
        # committed_by_year = Field(ByYear),
        core_capacities=capacities,
        amounts_duplicated=proj['amounts_duplicated'],
    )


def get_all_funders():
    funders_list = []

    for funder in all_funders:
        funders_list.append(FunderName(
                                       code=funder[0],
                                       name=funder[1]
        ))

    return FundersList(funders=funders_list)


def get_all_recipients():
    recipients_list = []

    for recipient in all_recipients:
        recipients_list.append(RecipientName(
                                       country=recipient[0],
                                       name=recipient[1]
        ))
    return RecipientsList(recipients=recipients_list)


def get_funder(country, year='all'):
    country_data = funders[country]

    if year == 'all':
        projects = []

        for project in country_data:
            projects.append(parse_project(project))

        return Funder(
            code=country,
            projects=projects
        )
    else:
        country_years = []

        for project in country_data:
            for transaction in project['transactions']:

                if int(transaction['cy']) == year:
                    country_years.append(parse_project(project))

        return Funder(
            code=country,
            projects=country_years,
        )


def get_recipient(country, year='all'):
    country_data = recipients[country]

    if year == 'all':
        projects = []

        for project in country_data:
            projects.append(parse_project(project))

        return Recipient(
            country=country,
            projects=projects
        )
    else:
        country_years = []

        for project in country_data:
            for transaction in project['transactions']:

                if int(transaction['cy']) == year:
                    country_years.append(parse_project(project))

        return Recipient(
            country=country,
            projects=country_years,
        )


class Funder(ObjectType):
    code = String()
    projects = List(lambda: Project)


class FunderName(ObjectType):
    code = String()
    name = String()


class FundersList(ObjectType):
    funders = List(FunderName)


class Recipient(ObjectType):
    country = String()
    projects = List(lambda: Project)


class RecipientName(ObjectType):
    country = String()
    name = String()


class RecipientsList(ObjectType):
    recipients = List(RecipientName)


class Transaction(ObjectType):
    type = String()
    amount = Float()
    cy = Int()
    currency = String()


class Source(ObjectType):
    name = String()
    id = String()
    added_by = String()
    mmddyyyy_added = String()


class ByYear(ObjectType):
    year = Int()
    amount = Int()


class CoreCapacity(ObjectType):
    name = String()


class Project(ObjectType):
    project_id = String()
    project_name = String()
    funder_ref = String()
    donor_sector = String()
    donor_code = String()
    donor_name = String()
    recipient_country = String()
    recipient_sector = String()
    recipient_name = String()
    transactions = List(Transaction)
    total_committed = Float()
    total_spent = Float()
    total_currency = String()
    source = Field(Source)
    spent_by_year = Field(ByYear)
    committed_by_year = Field(ByYear)
    core_capacities = List(CoreCapacity)
    amounts_duplicated = Boolean()


class Query(ObjectType):

    funder = Field(
        Funder,
        code=String(required=True),
        year=Int()
    )

    recipient = Field(
        Recipient,
        country=String(required=True),
        year=Int()
    )

    funders_list = Field(
        FundersList,
    )

    recipients_list = Field(
        RecipientsList,
    )

    @cached
    def resolve_funder(self, info, code='who', year='all'):
        funder_data = get_funder(code, year)
        return funder_data

    @cached
    def resolve_recipient(self, info, country='who', year='all'):
        recipient_data = get_recipient(country, year)
        return recipient_data

    @cached
    def resolve_funders_list(self, info):
        all_funder_data = get_all_funders()
        return all_funder_data

    @cached
    def resolve_recipients_list(self, info):
        all_recipient_data = get_all_recipients()
        return all_recipient_data


schema = Schema(query=Query, types=[Funder, Recipient, FundersList, RecipientsList])
