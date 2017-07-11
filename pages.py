import json
from os import listdir
from os.path import isdir, join, splitext

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


    def get(self, url) :
        # Check for special pages
        if url == "":
            return self.home_page()
        elif url.lower() == "notes" :
            return self.list_pages()
        elif url.lower() == "update" :
            self.pages = self.update();
            return self.pages[url]

        try :
            page = self.pages[url]
        except KeyError as e :
            print("Page not found: %s" % (e))
            return self.pages["404"]
        return page


    def get_info(self, directory) :
        try :
            with open(join(self.path, directory, "page.json")) as page_fp :
                page = json.loads(page_fp.read())
            with open(join(self.path, directory, "page.html")) as page_fp :
                content = page_fp.read().replace("\n\n","\n").replace(">\n<","><").strip("\n \t")
            if page.get("abstract","") == "":
                page["abstract"] = page["text"].split("\n")[0]
            base_name, extension = splitext(page.get("cover", "cover.jpg"))
            page["content"] = content
            page["sort"] = page["published"]
            page["published"] = self.parse_date(page["published"])
            page["cover"] = self.get_cover_fun(directory, extension)
            page["cover_extension"] = extension
            page["listed"] = page["listed"] == "True"
            page["links"] =  self.home_link() if content == "" else self.scroll_down()
        except IOError as e :
            page = None
            print("Page not found: %s" % (e))
        # Set cover
        return page


    def get_cover_fun(self, directory, extension):
        dir_path = "/static/pages/%s" % directory
        return lambda size : "%s/cover_%i%s" % (dir_path, size, extension)


    def scroll_down(self):
        return [self.cover_link("scroll down", "#content")]


    def home_link(self):
        return [self.cover_link("home", "/")]


    def cover_link(self, name, href):
        return {
            "name" : name,
            "href" : href
        }


    def home_page(self):
        page = self.get("frontpage")
        links = [self.cover_link("photos","http://www.ifany.org"),
                 self.cover_link("writings", "/notes/"),
                 self.cover_link("projects", "/projects/"),
                 self.cover_link("about", "/about/")]
        page["links"] = links
        page["page_title"] = "Dynkarken Unlimited"
        return page


    def list_pages(self) :
        page = self.get("writings")
        pages = [ (p["sort"], k ,p) for k,p in self.pages.items() if p["listed"] ]
        pages = reversed([(k,p) for (s, k ,p) in sorted(pages)])
        page["content"] = "<hr/>\n".join([self.write_page(k,p) for k,p in pages])
        return page


    def write_page(self, url, page) :
        header = "<a class='header' href='/%s/'><h2>%s</h2></a>" % (url, page["title"])
        content = "<p>%s</p>" % page["abstract"]
        posted = "<p class='read-more'>Posted on %s. " % page["published"]
        footer = "<a href='/%s/' title='%s'>Read more</a>.</p>" % (url, page["title"])
        return "\n".join([header, content, posted, footer])


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
