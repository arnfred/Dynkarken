#!/usr/bin/python

import os
import json
from subprocess import call
from dateutil import parser
from datetime import datetime
from time import strftime
from PIL import Image
import urllib
import sys
import traceback


def main(prog_name, argv) :

    # Check that a command is given
    if len(argv) > 0:
        command = argv[0]

        # Check that the command is one of the commands we support
        if command == 'init' :
            init_page(prog_name, argv[1:])
            sys.exit(0)
        elif command == 'publish' :
            publish_page(prog_name, argv[1:])
            sys.exit(0)

    print("""You need to specify a command:
          %{0} init [args]
          %{0} publish [args]""".format(prog_name))
    sys.exit(2)


def init_page(prog_name, argv) :

    # Is name specified
    if len(argv) == 0 :
        print("No configuration name specified. Use:")
        print("%s init your_name.conf" % prog_name)
        sys.exit(2)

    # We accept both "some_page" and "some_page.conf"
    conf_name = " ".join(argv).replace(".conf", "")
    conf_path = ("%s.conf" % conf_name).replace(" ", "_").lower()

    # Does name already exist?
    if os.path.exists(conf_path) :
        # Return errorinit_album("Trip to Bako", "data/2013-07-26 Kuching/")
        print("'%s' already exists" % (conf_path))
        sys.exit(2)

    conf_url = urllib.quote_plus(conf_name.lower().replace(" ","-"))
    init_conf = """Title :: {0}
Subtitle ::
Abstract ::
URL :: {1}
Listed :: True
Published :: {2}
Cover ::
Files :: []
================
Placeholder text here...
""".format(conf_name, conf_url, strftime("%Y-%m-%d"))

    # Create album.conf file
    with open(conf_path, 'w') as f:
        f.write(init_conf)



def publish_page(prog_name, argv, temp_root = "tmp") :

    if len(argv) == 0 :
        print("No configuration path specified. Use:")
        print("%s publish your_name.conf")
        sys.exit(2)

    # We accept both "some_page" and "some_page.conf"
    conf_path = "%s.conf" % "_".join(argv).replace(".conf", "")
    info = fetch_conf(conf_path)

    # Write info but make sure page directory exists
    temp_dir = write_json(info, temp_root)

    # Write cover or fetch from ifany.org
    prepare_cover(info.get("cover",""), temp_dir, info["title"].replace(" ",""))

    # Find file and if they are images then resize them
    for file_name in info.get('files', []) :
        save_file(file_name, info, temp_dir)

    # Translate markdown to html
    translate_to_markdown(info.get("text",""), temp_dir)

    # Remove the text part of the json
    del info["text"]

    # Push it to the server and remove tmp dir
    push(temp_dir)
    print("removing temp dir")
    call(["rm","-r", temp_root])


def fetch_conf(conf_path):
    # Check that file exists
    if not os.path.exists(conf_path) :
        print("'%s' doesn't exist" % (conf_path))
        sys.exit(2)

    # Gather information about page except if it's a malformed conf file
    try :
        info = read_conf(conf_path)
    except Exception as e :
        print("Error: %s (%s)" % (e, conf_path))
        print(traceback.format_exc())
        sys.exit(2)
    return info


def write_json(info, temp_root) :
    if not os.path.exists(temp_root) : os.mkdir(temp_root)
    temp_dir = "%s/%s" % (temp_root, info['url'])
    if not os.path.exists(temp_dir) : os.mkdir(temp_dir)
    with open("%s/%s" % (temp_dir, "page.json"), 'w') as fp:
        json.dump(info, fp, cls=DateTimeEncoder)
    return temp_dir

def get_random_cover(keyword, cover_name) :
    url = "http://www.ifany.org/cover/%s/2000/" % keyword.replace(" ","")
    call(["wget","-O",cover_name,url])


def translate_to_markdown(text, temp_dir):
    markdown_path = os.path.join(temp_dir, "page.md")
    html_path = os.path.join(temp_dir, "page.html")
    with open(markdown_path, 'a') as markdown_fp :
        markdown_fp.write(text)
    call(["pandoc","-f","markdown","-t","html", markdown_path, "-o", html_path])
    call(["rm","-r", markdown_path])


def save_file(file_name, info, temp_dir) :
    base_name, extension = os.path.splitext(file_name)
    if len(file_name) > 0 :
        print("processing %s" % (file_name))
        file_path = find_file(".", file_name)
        if file_path != None :
            # Translate url's in text
            url = "/static/pages/%s/%s" % (info['url'], file_name)
            text = info.get("text", "").replace("(%s)" % file_name, "(%s)" % url)
            info["text"] = text
            if extension in ["jpg","png","gif","bmp"] :
                resize_image(file_path, temp_dir, 600, 75)
            else :
                call(["cp", "-f", file_path, temp_dir])
        else :
            raise Exception("File '%s' doesn't exist" % file_name)


def prepare_cover(file_name, temp_dir, keyword, cover_name = "cover.jpg") :
    # Get cover extension
    base_name, extension = os.path.splitext(file_name)

    # If cover doesn't exist, then fetch random image from ifany
    cover_name = "cover%s" % (extension)
    if file_name == "" :
        get_random_cover(keyword, cover_name)
        file_name = cover_name
    # With cover in hand, resize to different sizes
    cover_sizes = [2000, 1600, 1280, 1024, 800]
    print("processing cover %s" % (file_name))
    file_path = find_file(".", file_name)
    if file_path != None :
        if os.path.normpath(file_path) != os.path.normpath(cover_name):
            call(["cp", file_path, cover_name])
        # Translate url's in text
        for width in cover_sizes :
            resize_image(cover_name, temp_dir, width, True, 95)
    else :
        raise Exception("Cover '%s' doesn't exist" % file_name)




def read_conf(conf_path) :
    # Init dictionary
    page = {}
    # Load conf
    with open(conf_path, 'r') as conf_file:
        conf = conf_file.readlines()
    # get page information
    for index, conf_line in enumerate(conf):
        if len(conf_line.split(" ::")) == 2 :
            (name, value) = conf_line.split(" ::")
            value_stripped = value.strip("\n ").strip("\"")
            # Get information from images
            if name.lower() == "files" :
                page['files'] = value_stripped.strip("[ ]").split(", ")
            elif name.lower() == "tags" :
                page['tags'] = value_stripped.strip("[ ]").split(", ")
            elif name.lower() == "public" :
                page['public'] = value_stripped.lower() in ["true", "yes"]
            elif name.lower() == "published" :
                page['published'] = parser.parse(value)

            elif name.lower() == "hide title" :
                page['hide_title'] = value_stripped.lower() in ["true", "yes"]
            else:
                page[name.lower()] = value_stripped
        else :
            break
    # The rest of the lines are markdown
    page['text'] = "".join(conf[index:]).strip("=-_ \t\n")
    return page



def resize_image(image_path, directory, size, with_size = False, quality = 80):
    """ Resize image """

    # Create thumbnails of the following sizes
    thumb_height, thumb_width = size, size

    # Make sure directory exists
    if not os.path.exists(directory):
        os.mkdir(directory)

    # Open original image
    image = Image.open(image_path)
    orientation = 'horizontal' if image.size[0] > image.size[1] else 'vertical'

    # get basename
    base_name, extension = os.path.splitext(image_path.split("/")[-1])

    (width, height) = image.size
    if orientation == 'horizontal':
        new_width = min(width, thumb_width)
        new_height = int(height * (new_width / float(width)))
    else:
        new_height = min(height, thumb_height)
        new_width = int(width * (new_height / float(height)))

    # Resize resulting image and save to directory
    image.thumbnail((new_width, new_height), Image.ANTIALIAS)

    # Save image
    if with_size :
        thumb_path = "%s/%s_%i%s" % (directory, base_name, size, extension)
    else :
        thumb_path = "%s/%s" % (directory, image_path)

    image.save(thumb_path, quality = quality)


def find_file(directory, name):
    """ Returns the first file in subdirectories of directory that matches name """
    # find the exact location of a filename that might reside in the subfolder of the root
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f == name:
                return "%s/%s" % (root, f)

        if '.git' in dirs:
            dirs.remove('.git')  # don't visit git directories
    return None



class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%S")
        return json.JSONEncoder.default(self, obj)


def push(local_dir, host_dir = "pages", host = "dynkarken.com", user = "arnfred"):
    if local_dir[-1] == '/' : local_dir = local_dir[:-1]
    call(["rsync","-av",local_dir, "%s@%s:~/%s" % (user, host, host_dir)])
    call(["cp","-r",local_dir, "/home/arnfred/Workspace/Dynkarken/static/pages/"])



# Run script if executed
if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
