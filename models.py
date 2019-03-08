import os
from flask import json  # , current_app as app
from collections import defaultdict


def FundingJSON():
    # filename = os.path.join(app.static_folder, 'data', 'funding_data.json')
    filename = os.path.join('/Users/trae/git_repositories/tracking-api/static',
                            'data', 'funding_data.json')

    with open(filename, encoding='utf-8') as funding_file:
        data = json.load(funding_file)

    funders = defaultdict(lambda: [])
    recipients = defaultdict(lambda: [])

    all_funders = set()
    all_recipients = set()

    for project in data:
        try:
            try:
                project['source'] = project['source']['name']
            except KeyError:
                project['source'] = None

            funders[project['donor_code']].append(project)
            recipients[project['recipient_country']].append(project)

            all_funders.add((project['donor_code'], project['donor_name']))
            all_recipients.add((project['recipient_country'], project['recipient_name']))
        except KeyError:
            print(project['project_name'])

    return (funders, recipients, all_funders, all_funders)
