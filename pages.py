import json
from os import listdir
from os.path import isdir, join

class Pages :

    def __init__(self, path = "static/pages") :
        self.path = path
        self.pages = self.update()


    def update(self) :
        # scan base directory
        directories = [ d for d in listdir(self.path) if isdir(join(self.path, d)) ]
        # Try to open all files
        return { d : self.get_info(d) for d in directories }


    def get_info(self, directory) :
        try :
            with open(join(self.path, directory, "page.json")) as page_fp :
                page_json = json.loads(page_fp.read())
            with open(join(self.path, directory, "page.html")) as page_fp :
                content = page_fp.read().replace("\n\n","\n").replace(">\n<","><")
            page = {
                "title" : page_json["title"],
                "published" : self.parse_date(page_json["published"]),
                "abstract" : page_json.get("abstract",""),
                "listed" : page_json["listed"],
                "parent" : page_json.get("parent","frontpage"),
                "content" : content }
        except IOError as e :
            page = self.error_404(directory)
            print("Page not found: %s" % (e))
        return page


    def get(self, url) :
        # Check for special pages
        if url.lower() == "writings" :
            return self.list_pages()
        elif url.lower() == "update" :
            self.update();
            return self.update_page()

        try :
            page = self.pages[url]
        except KeyError as e :
            page = self.error_404(url)
            print("Page not found: %s" % (e))
        return page


    def list_pages(self) :
        pages = { k : p for k,p in self.pages.items() if p["listed"] }
        return {
            "title" : "Writings",
            "abstract" : "These are miscellaneous writings mostly used for me to as place to pin down thoughts and take notes of things I'd like to remember.",
            "published" : "",
            "parent" : "frontpage",
            "listed" : False,
            "content" : "<hr/>\n".join([self.write_page(k,p) for k,p in pages.items()]) }


    def write_page(self, url, page) :
        header = "<a class='header' href='/%s/'><h2>%s</h2></a>" % (url, page["title"])
        content = "<p>%s</p>" % page["abstract"]
        posted = "<p class='read-more'>Posted on %s. " % page["published"]
        footer = "<a href='/%s/' title='%s'>Read more</a>.</p>" % (url, page["title"])
        return "\n".join([header, content, posted, footer])


    def error_404(self, directory) :
        return {
            "title" : "404 - Page not found",
            "abstract" : "The page you are looking for, '%s' did not match any pages on the server." % directory,
            "published" : "",
            "parent" : False,
            "listed" : False,
            "content" : "" }

    def update_page(self) :
        return {
            "title" : "Updating ...",
            "abstract" : "Currently updating pages",
            "published" : "",
            "parent" : False,
            "listed" : False,
            "content" : "" }

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
