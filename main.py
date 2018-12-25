import urllib.parse as uparse
from bs4 import BeautifulSoup
from optparse import OptionParser
from os.path import isdir, basename, exists, splitext
from os import system
from sys import maxsize
from random import randint
import time
from colorama import init
init()
from colorama import Fore, Back, Style

import requests

import json

m_url = ""
tdir = "down_imgs"
p_name = ""
cpages = 0
error_file = "error.log"
s_page = True

imgs = set()
furls = set()
purls = set()

http_s = "https:"

def p2url(p, url = None):
	global m_url, tdir, p_name, cpages, imgs, furls, purls, http_s, error_file, s_page

	if not url:
		url = m_url
	return url + p
	
def sslash(url):
	global m_url, tdir, p_name, cpages, imgs, furls, purls, http_s, error_file, s_page

	for i in range(len(url)):
		if not i+1 < len(url):
			return False
		elif url[i] == ' ':
			continue;
		elif url[i] == '/' and url[i+1] == '/':
			return True
		else:
			return False
			
def down_imgs():
	global m_url, tdir, p_name, cpages, imgs, furls, purls, http_s, error_file, s_page
	p_time = time.time()
	
	print(" [*] Downloading Images ... ")

	while isdir(tdir):
		tdir += str(randint(0, maxsize))
	
	system("mkdir " + tdir)
	tdir += '/'
	
	with open(tdir + "urls.log", "w") as f:
		for u in imgs:
			f.write(u + "\n")
		
	try:
		count = 0
		for url in imgs:
			print(" \t[*] Downloading Image (" + str(count) + "/" + str(len(imgs)) + ") ... ")
			try:
				f_name = basename(url)
				while exists(tdir + f_name):
					f_name = str(randint(0, maxsize)) + f_name
				if splitext(f_name)[1] == '':
					f_name += ".png"
				# httplib.urlretrieve(url, tdir + f_name)
				with open(tdir + f_name, "wb") as f:
					f.write(requests.get(url).content)
			except Exception:
				print(Fore.LIGHTRED_EX + " \t[-] URL didn't work out ..." +
				  " Skipping this image! (See Error Log) " + Fore.RESET)
				with open(error_file, "a") as f:
					ct = time.localtime()
					f.write("[%02d.%02d.%04d - %02d:%02d:%02d]: Image download failed! URL: %s\n" % 
					  (ct.tm_mday, ct.tm_mon, ct.tm_year, ct.tm_hour, ct.tm_min, 
					  ct.tm_sec, url))
			count += 1
	except KeyboardInterrupt as e:
		print(" [*] Interrupted downloading process. Quitting now! ")
		
	print(Fore.LIGHTGREEN_EX, "[+] Finished downloading! Exiting now ... ", Fore.RESET)
	
def crawl(pages):
	global m_url, tdir, p_name, cpages, imgs, furls, purls, http_s, error_file, s_page
	p_time = time.time()
	
	try:
		for i in range(pages):
			if furls:
				curl = furls.pop()
			else:
				print(Fore.LIGHTYELLOW_EX + " [.] Crawled through all linked pages ... " +
				Fore.RESET)
				return
			print(" [%04d] Current Crawler-URL: %s ... " % (i, curl))
		
			purls.add(curl)
			try:
				soup = BeautifulSoup(requests.get(curl).text, "html.parser")
		
				for img in soup.find_all("img"):
					if "https://" in img.get("src") or "http://" in img.get("src") or\
					  "data:" in img.get("src"):
						imgs.add(img.get("src"))
					elif sslash(img.get("src")):
						imgs.add(http_s + img.get("src"))
					else: 
						imgs.add(p2url(img.get("src"), curl))
					
					if img.get("data-lazy"):
						if "https://" in img.get("data-lazy") or "http://" in img.get("data-lazy") or\
						  "data:" in img.get("data-lazy"):
							imgs.add(img.get("data-lazy"))
						elif sslash(img.get("data-lazy")):
							imgs.add(http_s + img.get("data-lazy"))
						else: 
							imgs.add(p2url(img.get("data-lazy")))	
				
				for a in soup.find_all("a"):
					if a.get("href"):
						if "https://" in a.get("href") or "http://" in a.get("href"):
							if ((s_page and p_name in a.get("href")) or not s_page)\
							  and not (a.get("href") in purls):
								furls.add(a.get("href"))
						elif sslash(a.get("href")):
							if ((s_page and p_name in a.get("href")) or not s_page)\
							  and not ((http_s + a.get("href"))\
							  in purls):
								furls.add(http_s + a.get("href"))
			except Exception:
				print(Fore.LIGHTRED_EX + " [-] Connecting to URL didn't work." +
				" Skipping it ... (See Error Log)" + Fore.RESET)
				with open(error_file, "a") as f:
					ct = time.localtime()
					f.write("[%02d.%02d.%04d - %02d:%02d:%02d]: Connection to page failed! URL: %s\n" % 
					(ct.tm_mday, ct.tm_mon, ct.tm_year, ct.tm_hour, ct.tm_min, 
					ct.tm_sec, curl))
				
	except KeyboardInterrupt as e:
		print(" [*] Interrupted crawling process. Quitting now!")

def main():
	parser = OptionParser()
	parser.add_option("-u", "--url", dest="url", help="Target URL.")
	parser.add_option("-d", "--dir", dest="dir", help="Target Directory.", 
		default="down_imgs")
	parser.add_option("-p", "--page", dest="page", help="Target page's name.")
	parser.add_option("-c", "--crawl", type="int", dest="crawl", help="Amount of pages that" +
	" should be crawled.")
	parser.add_option("-l", "--log", dest="elog", help="Error log destination.", 
		default="error.log")
	parser.add_option("-s", "--spage", dest="spage", action='store_true', help="Stay on same page?")
	(options, args) = parser.parse_args()
	
	global m_url, tdir, p_name, cpages, imgs, furls, purls, http_s, error_file, s_page
	
	print(Fore.LIGHTCYAN_EX + "{:^78}".format(" -- ImageGrabber (Python 3.6) -- ") + Fore.RESET)
	print(Fore.LIGHTBLUE_EX + "{:^78}".format("by MattMoony") + Fore.RESET)
	print("\n")
	
	if options.url:
		m_url = options.url
	else:
		m_url = input(" [*] Please enter the target URL: ")
	if options.page:
		p_name = options.page
	else:
		p = uparse.urlparse(m_url)
		d = p.netloc.split('.')
		
		if len(d) > 2:
			p_name = '.'.join(d[1:2])
		else:
			p_name = '.'.join(d)
	s_page = options.spage
	if options.crawl:
		cpages = options.crawl
	else:
		while True:
			try:
				cpages = int(input(" [*] Enter the amount of pages that should be crawled: "))
				if cpages >= 0:
					break
				else:
					print(Fore.LIGHTRED_EX + " [-] Error, please enter an integer greater or equal to zero. " + Fore.RESET)
			except ValueError as e:
				print(Fore.LIGHTRED_EX + " [-] Error, please enter a valid integer. " + Fore.RESET)
	tdir = (options.dir).strip('/')
	error_file = options.elog
	
	if "https://" in m_url:
		http_s = "https:"
	elif "http://" in m_url:
		http_s = "http:"
	else:
		print("%s [-] Error: Connection is neither 'https' nor 'http'. (%s) Please make sure you entered the complete URL. %s" % (Fore.LIGHTRED_EX, m_url, Fore.RESET))
		exit()
	
	soup = BeautifulSoup(requests.get(m_url).text, "html.parser")
	
	for img in soup.find_all("img"):
		if "https://" in img.get("src") or "http://" in img.get("src") or\
		  "data:" in img.get("src"):
			imgs.add(img.get("src"))
		elif sslash(img.get("src")):
			imgs.add(http_s + img.get("src"))
		else: 
			imgs.add(p2url(img.get("src")))
			
		if img.get("data-lazy"):
			if "https://" in img.get("data-lazy") or "http://" in img.get("data-lazy") or\
			  "data:" in img.get("data-lazy"):
				imgs.add(img.get("data-lazy"))
			elif sslash(img.get("data-lazy")):
				imgs.add(http_s + img.get("data-lazy"))
			else: 
				imgs.add(p2url(img.get("data-lazy")))	
		
	for a in soup.find_all("a"):
		if a.get("href"):
			if "https://" in a.get("href") or "http://" in a.get("href"):
				if ((s_page and p_name in a.get("href")) or not s_page):
					furls.add(a.get("href"))
			elif sslash(a.get("href")):
				if ((s_page and p_name in a.get("href")) or not s_page):
					furls.add(http_s + a.get("href"))
			else:
				furls.add(p2url(a.get("href")))
	crawl(cpages)
		
	print(Fore.LIGHTYELLOW_EX, end="")
	yn = input(" [.] Found " + str(len(imgs)) + 
	  " Images. Download now? [y/n] ")
	print(Fore.RESET, end="")
	if yn in "yY":
		s_time = time.time()
		down_imgs()
		print(" [.] Total downloading time: %.2f s ... " % (time.time() - s_time))
	else:
		print(" [.] Okay! Exiting now ... ")

if __name__ == '__main__':
	main()