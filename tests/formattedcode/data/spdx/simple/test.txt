import unittest
import download_repo_run_scan
from os import path, remove
import shutil	

#This tests a method that runs through the whole scanning process.
#Since it calls a few other methods, it will fail also if those methods fail.
class wholeScanTestCase(unittest.TestCase):
	url = 'https://github.com/abuhman/test_webhooks/archive/master.zip'
	spdx_file_name = ''
	def setUp(self):
		self.spdx_file_name = download_repo_run_scan.download_repo_run_scan(self.url)
	def tearDown(self):
		remove(self.spdx_file_name)
	def testWholeScan(self):
		assert path.isfile(self.spdx_file_name)

#Test that when given a valid zip file url,
#the download_github_zip will result in the creation
#of a local file at the returned location
class downloadFileTestCase(unittest.TestCase):
	file_location = ''
	url = 'https://github.com/abuhman/test_webhooks/archive/master.zip'
	def setUp(self):
		self.file_location = download_repo_run_scan.download_github_zip(self.url)

	def tearDown(self):
		remove(self.file_location)

	def testDownload(self):
		assert path.isfile(self.file_location)

#Test that we can unzip a zip file.
class unzipFileTestCase(unittest.TestCase):
	file_location = 'test.zip'
	extracted_directory = ''
	def setUp(self):
		self.extracted_directory = download_repo_run_scan.unzip_file(self.file_location)
	
	def tearDown(self):
		#Remove the unzipped directory
		shutil.rmtree(self.extracted_directory)
	
	def testUnzip(self):
		assert 	path.isdir(self.extracted_directory)

#This tests whether a file output is produced from calling the scan method.
class scanTestCase(unittest.TestCase):
	directory = 'test2/'
	spdx_file_name = ''
	def setUp(self):
		#Set output file name to the directory name .SPDX
		self.spdx_file_name = self.directory[:-1] + '.SPDX'

		#scan the extracted directory and put results in a named file
		download_repo_run_scan.scan(self.directory, self.spdx_file_name, 'scancode', 'tag-value')
	def tearDown(self):
		#Remove the scan results file
		remove(self.spdx_file_name)

	def testScan(self):
		assert path.isfile(self.spdx_file_name)

#This checks whether the check_valid_url method correctly determines
#whether a url results in an error (400 or 500 code)
class checkURLTestCase(unittest.TestCase):
	good_url = 'https://www.google.com/'
	bad_url = 'https://www.google.com/fail'
	
	def testGoodURL(self):
		assert download_repo_run_scan.check_valid_url(self.good_url) == True

	def testBadURL(self):
		assert download_repo_run_scan.check_valid_url(self.bad_url) == False
	


if __name__ == "__main__":
	unittest.main()
	
