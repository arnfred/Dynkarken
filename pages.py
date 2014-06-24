import json
from os import listdir
from os.path import isdir, join

class Pages :

    def __init__(self, path = "static/pages") :
        self.path = path
        self.pages = self.update()
        self.cover_url = "http://www.ifany.org/cover/"


    def update(self) :
        # scan base directory
        directories = [ d for d in listdir(self.path) if isdir(join(self.path, d)) ]
        # Try to open all files
        return { d : self.get_info(d) for d in directories }


    def get_info(self, directory) :
        try :
            with open(join(self.path, directory, "page.json")) as page_fp :
                page = json.loads(page_fp.read())
            with open(join(self.path, directory, "page.html")) as page_fp :
                content = page_fp.read().replace("\n\n","\n").replace(">\n<","><")
            if page.get("abstract","") == "":
                page["abstract"] = page["text"].split("\n")[0]
            page["content"] = content
            page["published"] = self.parse_date(page["published"])
            page["cover"] = self.get_cover_fun(directory)
            page["listed"] = page["listed"] == "True"
            page["links"] = self.scroll_down()
        except IOError as e :
            page = self.error_404(directory)
            print("Page not found: %s" % (e))
        # Set cover
        return page

    def get_cover_fun(self, directory):
         return lambda size : self.cover_url + directory + "/" + str(size) + "/"


    def scroll_down(self):
        return [self.cover_link("scroll down", "#content")]


    def home_link(self):
        return [self.cover_link("home", "/")]


    def cover_link(self, name, href):
        return {
            "name" : name,
            "href" : href
        }


    def get(self, url) :
        # Check for special pages
        if url == "":
            return self.home_page()
        elif url.lower() == "notes" :
            return self.list_pages()
        elif url.lower() == "update" :
            self.pages = self.update();
            return self.update_page()

        try :
            page = self.pages[url]
        except KeyError as e :
            page = self.error_404(url)
            print(page)
            print("Page not found: %s" % (e))
            print(self.cover_page("test","subtest"))
        return page


    def home_page(self):
        links = [self.cover_link("photos","http://www.ifany.org"),
                 self.cover_link("knitwit", "http://knitwit.dynkarken.com"),
                 self.cover_link("about", "/about/")]
        page =  self.cover_page("Dynkarken",
                                "The personal web page of Jonas Arnfred",
                                links = links)
        page["page_title"] = "Dynkarken unlimited"
        return page




    def list_pages(self) :
        pages = { k : p for k,p in self.pages.items() if p["listed"] }
        title = "Writings"
        subtitle = "A compilation of notes and thoughts"
        content = "<hr/>\n".join([self.write_page(k,p) for k,p in pages.items()])
        return self.cover_page(title, subtitle, content, self.scroll_down())


    def write_page(self, url, page) :
        header = "<a class='header' href='/%s/'><h2>%s</h2></a>" % (url, page["title"])
        content = "<p>%s</p>" % page["abstract"]
        posted = "<p class='read-more'>Posted on %s. " % page["published"]
        footer = "<a href='/%s/' title='%s'>Read more</a>.</p>" % (url, page["title"])
        return "\n".join([header, content, posted, footer])


    def cover_page(self, title, subtitle, content = "", links = None):
        links = links if links != None else self.home_link()
        return {
            "title" : title,
            "subtitle" : subtitle,
            "abstract" : "",
            "published" : "",
            "parent" : False,
            "listed" : False,
            "links" : links,
            "cover" : self.get_cover_fun(title),
            "content" : content
         }

    def error_404(self, directory) :
        title = "404"
        subtitle = "Page not found: %s" % directory
        return self.cover_page(title, subtitle)


    def update_page(self) :
        title = "Updating"
        subtitle = "Changes should be online soon"
        return self.cover_page(title, subtitle)


    def parse_date(self, date_string) :
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
