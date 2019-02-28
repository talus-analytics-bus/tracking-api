from pony.orm import set_sql_debug, Database, PrimaryKey, Required, Set
import os
# from enum import Enum

db = Database()


class Company(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    policies = Set("Policy")
    zones = Set("CustomerZone")


class Fire(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    zones = Set("Zone")


class Zip(db.Entity):
    id = PrimaryKey(int, auto=True)
    code = Required(str)
    zones = Set("Zone")


class County(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    fips = Required(str)
    zones = Set("Zone")


class Zone(db.Entity):
    id = PrimaryKey(int, auto=True)
    size = Required(str)
    state = Required(str)
    area = Required(float)
    zips = Set("Zip")
    fires = Set("Fire")
    counties = Set("County")
    customer_zones = Set("CustomerZone")


class Breakdown(db.Entity):
    id = PrimaryKey(int, auto=True)
    none_percent = Required(float)
    minimal_percent = Required(float)
    moderate_percent = Required(float)
    high_percent = Required(float)
    extreme_percent = Required(float)
    customer_zone = Set("CustomerZone")


class CustomerZone(db.Entity):
    id = PrimaryKey(int, auto=True)
    customer = Required(Company)
    zone = Required(Zone)
    policies = Set("Policy")
    policy_count = Required(int)
    tiv = Required(float)
    pml = Required(float)
    pml_50 = Required(float)
    pml_100 = Required(float)
    pml_250 = Required(float)
    mean_bp = Required(float)
    breakdown = Required(Breakdown)


class Policy(db.Entity):
    id = PrimaryKey(int, auto=True)
    company = Required(Company)
    status = Required(str)
    address = Required(str)
    city = Required(str)
    county = Required(str)
    state = Required(str)
    zip = Required(str)
    tiv = Required(int)
    latitude = Required(float)
    longitude = Required(float)
    model_type = Required(str)
    loss_type = Required(str)
    overall_risk_class = Required(str)
    severity_class = Required(str)
    frequency_class = Required(str)
    distance_to_high_hazard = Required(float)
    customer_zone = Required(CustomerZone)


set_sql_debug(True)

usr = os.environ["TALUS_DEV_USR"]
pwd = os.environ["TALUS_DEV_PWD"]
host = 'talus-dev.cvsrrvlopzxr.us-west-1.rds.amazonaws.com'

db.bind(provider='postgres', user=usr, password=pwd, host=host, database='redzone_ui')
db.generate_mapping()  # create_tables=True)
