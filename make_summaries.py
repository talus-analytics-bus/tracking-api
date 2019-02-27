from sqlalchemy import create_engine

from collections import defaultdict
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

engine = create_engine('postgresql://talus:UKwwGaH5X8q688K4@talus-dev.cvsrrvlopzxr.us-west-1.rds.amazonaws.com/census')
connection = engine.connect()

Session = sessionmaker(bind=engine)

s = Session()

result = connection.execute("SELECT DISTINCT(state) FROM census_metrics")

state_list = []

for row in result:
    state_list.append(row['state'])

Base = declarative_base()


class Metric(Base):
    __tablename__ = 'census_metrics'

    name = Column(String)
    state = Column(String)
    county = Column(String)
    tract = Column(String)
    year = Column(Integer)
    metric = Column(String)
    count = Column(Integer)
    id = Column(Integer, primary_key=True)
    metric_info = Column(Integer)
    type = Column(String)

    def __repr__(self):
        return "<Metric(name='%s', metric='%s', count='%s')>" % (self.name, self.metric, self.count)


county_q = """SELECT name, state, county, year, metric_info, metric,
            SUM(count) AS county_count
            FROM census_metrics cm WHERE cm.state = '{0}' AND year = {1}
            GROUP BY name, state, county, year, metric, metric_info
           """

for state in state_list:

    print('Working on state {0}'.format(state))

    for year in [2016]:
        county_qf = county_q.format(state, year)

        result = connection.execute(county_qf)

        metric_list = []

        state_count_dict = defaultdict(int)
        metric_info_dict = defaultdict(int)

        state_name = ""
        state = ""
        year = 0

        for count, cm in enumerate(result):
            if count == 0:
                state_name = cm.name.split(",")[2].strip()
                state = cm.state
                year = cm.year

            # add to the metric's value for the state overall
            state_count_dict[cm.metric] += cm.county_count
            metric_info_dict[cm.metric] = cm.metric_info

            county_name = cm.name.split(",")[1].strip()

            county_data = Metric(
                                 name=county_name,
                                 state=cm.state,
                                 county=cm.county,
                                 tract='None',
                                 year=cm.year,
                                 metric=cm.metric,
                                 count=cm.county_count,
                                 metric_info=cm.metric_info,
                                 type='county')

            metric_list.append(county_data)

        for sm, count in state_count_dict.items():
            state_data = Metric(
                                 name=state_name,
                                 state=state,
                                 county='None',
                                 tract='None',
                                 year=year,
                                 metric=sm,
                                 count=count,
                                 metric_info=metric_info_dict[sm],
                                 type='state')

            metric_list.append(state_data)

        chunks = [metric_list[x:x+5000] for x in range(0, len(metric_list), 5000)]

        for chunk in chunks:
            s.bulk_save_objects(chunk)

        s.commit()
