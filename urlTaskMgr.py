import requests
import urlparse
import re
import sys, getopt

class urlTaskMgr():
	def __init__(self, url, number_of_urls=50, verbose = 0):
		self.verbose = verbose
		#default is to find up to 50 valid URLs, can also specify a different number
		self.max_size = number_of_urls
		
		#self.url_list is a list of validated URLs
		self.url_list = []
		
		#self.url_content is a dictionary, key is a validated URL, item is the URL's content
		#when validating a URL, store its content to the dictionary so there is no need to send request twice
		#..could combine url_list and url_content with one ordered dictionary, but afraid code is less readable
		self.url_content = {}
		
		self.handle_single_link(url)
		if (self.get_size() == 0):
			print "\n!!!Failure: Unrecoveable error, please check the input URL."
			sys.exit(2)
		
		#URLs in self.url_list is accessed one by one, to get href links from the URL's content 
		#next_url_index is the index of the URL to be handled next
		self.next_url_index = 0

		
	#gets the total number of valid URLs collected	
	def get_size(self):
		return len(self.url_list)
		
	#gets the URL whose contents to be handled next
	def get_next_url(self):
		return self.url_list[self.next_url_index]
		
	#gets the URL content which is saved in self.url_content dictionary
	def get_url_content(self, url):
		if self.url_content.has_key(url):
			return self.url_content[url]
		else:
			return ' '
	
	#This function validates URL.
	#	It calls requests.get(url),
	#	handles exception, prints error message to command line,
	#	returns with None at failure and response object at success 
	def validate_url(self, url):
		try:
			resp = requests.get(url)
			if resp.ok != True:
				resp.raise_for_status()
			return resp
		except Exception as e:
			print "\t\tInvalid URL [%s], accessing failed with [%s]." %(url, e.message)
			return None

	#This function adds eligible URL to url_list.		
	#	Firstly function checks if the URL is valid, then checks if URL is already in self.url_list, if not in the list, then 
	#   add the URL to self.url_list and the URL's content to self.url_content
	def handle_single_link(self, url):
		if url in self.url_list:
			return
		resp = self.validate_url(url)
		if resp != None:
			#use url from requests response object, to make sure there is only one URL from the same webpage
			formated_url = resp.url
			if formated_url not in self.url_list:
				self.url_list.append(formated_url)
				self.url_content[formated_url]=resp.content
			else:
				if self.verbose:					
					print "\t\tNot Added new URL: [%s] already in list\n" %(formated_url)		
			if self.verbose:
				if formated_url != url:
					print "\t\tThe url can be furthur formatted to %s" %(formated_url)
				print "\t\tAdded new URL: #%d %s\n" %(self.get_size(), formated_url)
			
	#This function handles href links from URL content.
	#   Function first parses URL(base url) content to get all href links, and skips those links bound through Javascript.
	#	Then for each href link, function generates a new_url, and adds that new_url to url_list if it is eligible.
	def handle_links_in_page(self, url):
		#parsing to get href links in content
		links = re.findall('''href=[\n]*[\s]*["'](.[^"' ]+)["']''', self.get_url_content(url))
		if self.verbose:
			print "Under URL %s %d links (including duplicate links) found " %(url, len(links))		
		#links as a list may have dumplicates, turn it into set to take out dumplicates
		links = set(links)
		if self.verbose:
			print "\tTaking out duplidate href links left with %d: " %(len(links))
			cnt = 1
			for i in links:
				print "\t\thref #%d %s" %(cnt, i)
				cnt +=1
			print "\n"

		for link in links:
			if link.startswith("javascript:"):
				#skip because this is javascript generated link
				if self.verbose:					
					print "\tSkip href link [%s] because it is bound through Javascript\n" %(link)				
				continue
				
			#urlparse.urljoin(base_url, absolute_or_relative_href) handles absolute or relative link and 
			# returns with a new URL that may be eligile for url_list
			new_url = urlparse.urljoin(url, link)
			if self.verbose:		
				print "\tAccessing href [%s] from [%s], bringing us to [%s], handling this new url" %(link, url, new_url)			
			
			#adds new_url to url_list if it is eligible
			self.handle_single_link(new_url)

			#return to upper function if we have enough URLs
			if self.get_size() >= self.max_size:
				return			
		
	#This is the main task function.
	#	In a while loop, url_list is growing until it reaches self.max_size or until no URLs to be found.
	#	At the end, URLs is printed one by one.
	def run(self):	
		while self.next_url_index < self.get_size() and self.get_size() < self.max_size:
			current_url = self.get_next_url()
			self.handle_links_in_page(current_url)
			self.next_url_index += 1
			
		print "\nPrinting all valid URLs of up to %d URLs" %(self.max_size)
		if self.get_size() < self.max_size:
			print "Note that we only could find %d URLs" %(self.get_size())
		for i in range (0, self.get_size()):
			print "\t%d %s" %(i+1, self.url_list[i])

def usage():
	print "Usage: <python> %s -u <URL> [-n <number_of_urls_to_list, default is 50, minimal is 1>] [-v verbose]" %(__file__)
	print "Usage: Enter URL and number of URLs to find, an example below"
	print "       <python> %s -u google.com [-n 50] [-v 0|<nonzero number>]" %(__file__)

def main(argv):
	number_of_urls = 50
	url = None
	verbose = 0

	try:
		opts, args = getopt.getopt(argv,"hu:n:v:",["help", "url", "number", "verbose"])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h"):
			usage()
			sys.exit()
		elif opt in ("-u"):
			url = arg
		elif opt in ("-n"):
			number_of_urls = int(arg)
			number_of_urls = max(1, number_of_urls)
		elif opt in ("-v"):
			verbose = int(arg)

	if url == None:
		usage()
		sys.exit(2)
	print "Starting from accessing URL [%s], find a total of %d valid URLs or until none is left to find.\n" %(url, number_of_urls)	
	urlTaskMgr(url, number_of_urls, verbose).run()
    
if __name__ == "__main__":
   main(sys.argv[1:])	
	