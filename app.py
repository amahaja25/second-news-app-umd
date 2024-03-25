import os
from peewee import *
from census import Census
from flask import Flask
from flask import render_template
app = Flask(__name__)
db = SqliteDatabase('foreclosures.db')
census_api_key = os.environ.get('CENSUS_API_KEY')
c = Census(census_api_key)

class Notice(Model):
    id = IntegerField(unique=True)
    zip = CharField()
    month = DateField()
    notices = IntegerField()

    class Meta:
        table_name = "notices"
        database = db

@app.route("/")
def index():
    notice_count = Notice.select().count()
    all_zips = (Notice.select(Notice.zip).distinct())
    template = 'index.html'
    return render_template(template, count = notice_count, all_zips = all_zips)

@app.route('/zipcode/<slug>')
def detail(slug):
    zipcode = slug
    notices = Notice.select().where(Notice.zip==slug)
    total_notices = Notice.select(fn.SUM(Notice.notices).alias('sum')).where(Notice.zip==slug).scalar()
    notice_json = []
    for notice in notices:
        notice_json.append({'x': str(notice.month.year) + ' ' + str(notice.month.month), 'y': notice.zip, 'heat': notice.notices})
    owner_occupied = c.acs5.state_zipcode(('NAME', 'B25003_002E'), '24', zipcode)
    return render_template("detail.html", zipcode=zipcode, notices=notices, notices_count=len(notices), notice_json = notice_json, total_notices = total_notices, owner_occupied = int(owner_occupied[0]['B25003_002E']))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)