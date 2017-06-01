# Project Web Crawler
# This Python program urlTaskMgr.py takes an URL, accessing it and finds more URLs repeatedly and recursively. It reports errors in execution and at the end reports valid URLs found.

# specify URL with -u
## for example, command "python urlTaskMgr.py -u https://veracode.com"

# default is to find up to 50 links, use -n to modify the number.
## for example command "python urlTaskMgr.py -u https://google.com  -n 5" will find up to five links

# use -v <nonzero> to run verbose mode
## for command "python urlTaskMgr.py -u https://veracode.com -v 1" will print more information during execution.

# to get help
## "python urlTaskMgr.py -h"
