import web
import json
#import random, string
#import os
#import re


# Define pages
urls = (
    '/', 'index',
    '/(.[a-z0-9.\-_!?]+)/', 'page'
)

# Define template
render = web.template.render('templates/')

# Run the app
if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

# Index page displays start page
class page :
    def GET(self, page_id):
        page_path = "static/pages/%s" % page_id
        print(page_path)
        try :
            with open("%s/page.json" % page_path, 'r') as page_fp :
                page_json = json.loads(page_fp.read())
            with open("%s/page.html" % page_path, 'r') as page_fp :
                content = page_fp.read().replace("\n\n","\n").replace(">\n<","><")
            title = page_json["title"]
            published = parse_date(page_json["published"])
            abstract = page_json.get("abstract","")
            return render.page(title, published, abstract, content, page_id)
        except IOError as e :
            return "Page '%s' not found (%s)" % (page_id, e)

# Index page displays start page
class index :
    def GET(self):
        return render.main()

def parse_date(date_string) :
    date_list = date_string[0:10].split("-")
    year = int(date_list[0])
    month = {
        "01" : "January",
        "02" : "February",
        "03" : "March",
        "04" : "April",
        "05" : "May",
        "06" : "June",
        "07" : "July",
        "08" : "August",
        "09" : "September",
        "10" : "October",
        "11" : "November",
        "12" : "December"}[date_list[1]]
    day = int(date_list[2])
    day_suffix = {
        "1" : "st",
        "2" : "nd",
        "3" : "rd"}.get(str(day)[-1], "th")
    return "%s %i%s %i" % (month, day, day_suffix, year)
