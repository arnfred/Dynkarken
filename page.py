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
          %{0} update [args]""".format(prog_name))
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
Listed :: True
URL :: {1}
Published :: {2}
Images :: []
Tags :: []
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

    # Check that file exists
    if not os.path.exists(conf_path) :
        # Return errorinit_album("Trip to Bako", "data/2013-07-26 Kuching/")
        print("'%s' doesn't exist" % (conf_path))
        sys.exit(2)

    # Gather information about album except if it's a malformed conf file
    try :
        info = read_conf(conf_path)
    except Exception as e :
        print("Error: %s (%s)" % (e, conf_path))
        print(traceback.format_exc())
        sys.exit(2)

    # Write info but make sure album directory exists
    if not os.path.exists(temp_root) : os.mkdir(temp_root)
    temp_dir = "%s/%s" % (temp_root, info['url'])
    if not os.path.exists(temp_dir) : os.mkdir(temp_dir)
    with open("%s/%s" % (temp_dir, "page.json"), 'w') as fp:
        json.dump(info, fp, cls=DateTimeEncoder)

    # Find images and resize them
    for im_file in info.get('images', []) :
        if len(im_file) > 0 :
            print("processing %s" % (im_file))
            image_path = find_image(".", im_file)
            if image_path != None :
                resize_image(image_path, temp_dir)
            else :
                raise Exception("Image %s doesn't exist" % image_path)

    # Translate markdown to html
    markdown_path = os.path.join(temp_dir, "page.md")
    html_path = os.path.join(temp_dir, "page.html")
    with open(markdown_path, 'a') as markdown_fp :
        markdown_fp.write(info.get('text', ""))
    call(["pandoc","-f","markdown","-t","html", markdown_path, "-o", html_path])
    call(["rm","-r", markdown_path])

    # Push it to the server
    push(temp_dir)
    print("removing temp dir")
    call(["rm","-r", temp_dir])


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
            if name.lower() == "images" :
                page['images'] = value_stripped.strip("[ ]").split(", ")
            elif name.lower() == "tags" :
                page['tags'] = value_stripped.strip("[ ]").split(", ")
            elif name.lower() == "public" :
                page['public'] = value_stripped.lower() in ["true", "yes"]
            elif name.lower() == "published" :
                page['published'] = parser.parse(value)
            else:
                page[name.lower()] = value_stripped
        else :
            break
    # The rest of the lines are markdown
    page['text'] = "\n".join(conf[index:]).strip("=-_ \t\n")
    return page



def resize_image(image_path, directory):
    """ Resize image """

    # Create thumbnails of the following sizes
    thumb_height, thumb_width = (800, 600)

    # Make sure directory exists
    if not os.path.exists(directory):
        os.mkdir(directory)

    # Open original image
    image_orig = Image.open(image_path)
    image = image_orig.copy()
    orientation = 'horizontal' if image_orig.size[0] > image_orig.size[1] else 'vertical'

    # Crop the square thumbnails
    if thumb_width == thumb_height:
        (width, height) = image.size
        if orientation == 'horizontal':
            margin = (width - height) / 2
            image = image.crop((margin, 0, width - margin, height))
        else:
            margin = (height - width) / 2
            image = image.crop((0, margin, width, height - margin))

    # Resize resulting image and save to directory
    image.thumbnail((thumb_width, thumb_height), Image.ANTIALIAS)

    # Save image
    thumb_path = "%s/%s" % (directory, image_path, thumb_width, thumb_height)
    image.save(thumb_path)



def find_image(directory, name):
    """ Returns the first image in subdirectories of directory that matches name """
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
    # So, put this together with publish. Collect the directories created
    # and for each, push the photos
    # finally delete directories



# Run script if executed
if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
