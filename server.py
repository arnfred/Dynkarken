import web
import json
#import random, string
#import os
#import re


# Define pages
urls = (
  '/', 'index',
  '/(.+)', 'page'
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
    return render.page(page_id, page_id)


# Index page displays start page
class index :
  def GET(self):
    return render.main()
