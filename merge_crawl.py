#!/usr/bin/env python

import os, sys, getopt, subprocess, time


print "Starting crawl data merge..."

#for handling command line arguement
def main(argv):
	remote_dir='remote_data'
	crawldb_dir='crawldb'
	try:
		opts, args = getopt.getopt(argv, "ht:d:", ["rdir=","ldir="])
	except getopt.GetoptError:
		print 'merge_crawl.py -t <directory_for_data_from_remote> -d <crawldb_directory>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'merge_crawl.py -t <directory_for_data_from_remote> -d <crawldb_directory>'
			sys.exit()
		elif opt in ('-d', '--ldir'):
			crawldb_dir = arg
		elif opt in ('-t', '--rdir'):
			remote_dir = arg

#for checking/making remote crawl data dirtectory
	if not os.path.exists( crawldb_dir):
		os.makedirs( crawldb_dir )
	crawldb_file = crawldb_dir + '/crawldb.json'

#	merging logic TODO



if __name__ == '__main__':
	main(sys.argv[1:])

print "Crawl data merge completed..."
