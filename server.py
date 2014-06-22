import web
from pages import Pages
#import random, string
#import os
#import re


# Define urls
urls = (
    '/()', 'page',
    '/(.[a-z0-9.\-_!?]+)/', 'page'
)

# Define template
render = web.template.render('templates/', base='base')

# Define pages
pages = Pages()

# Run the app
if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

# Index page displays start page
class page :
    def GET(self, page_id):
        page = pages.get(str(page_id))
        return render.page(page, page_id)

# Index page displays start page
class index :
    def GET(self):
        return render.main()

