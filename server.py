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
        try :
            with open("static/pages/%s/page.json" % page_id, 'r') as page_fp :
                page_json = json.loads(page_fp.read())
            with open("static/pages/%s/page.html" % page_id, 'r') as page_fp :
                content = page_fp.read().replace("\n\n","\n").replace(">\n<","><")
            name = page_json["title"]
            return render.page(name, page_id, content)
        except IOError :
            return "Page '%s' not found" % page_id

# Index page displays start page
class index :
    def GET(self):
        return render.main()
