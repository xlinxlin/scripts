#!/usr/bin/python

import os
import sys
import getopt
import shutil
import glob
import argparse
import csv

def get_arguments():
  parser = argparse.ArgumentParser(description = "",
                                      add_help = False)
  main_group = parser.add_argument_group('Main options')
  main_group.add_argument("-d", "--directory", required = True,
                          help = "The diretory to the project.")
  main_group.add_argument("-c", "--csv", required = True,
                          help = "The CSV file.")
  main_group.add_argument("-h", "--help", action = "help", default = argparse.SUPPRESS,
                          help = "Show this help message and exit")
  args = parser.parse_args()
  return args

#show the short guideline before run the command
def guideline_replace_barcodes(arr_old_barcodes, arr_new_barcodes):
  s = ""
  for old_barcode, new_barcode in zip(arr_old_barcodes, arr_new_barcodes):
    s = s + old_barcode + " -> " + new_barcode + "\n" 
  return s

#user input to confirm the run
def yes_or_no(question):
  print question
  reply = raw_input().lower()
  if reply == 'y':
    return 1
  elif reply == 'n':
    sys.exit(0)
  else:
    return yes_or_no("Are you sure? (y/n)")

#check if the directory to the barcodes exists
def check_directory_exists(arr_path_ont_barcodes):
  check_result = 1
  for path in arr_path_ont_barcodes:
    if os.path.isdir(path) == False:
      print "Directory " + path + " not exists.\n"
      check_result = 0
  return check_result

#get full path to barcodes
def get_full_path_to_barcodes(arr_path_headers, arr_ont_barcodes):
  arr_path_ont_barcodes = [] 
  for path in arr_path_headers:
    for barcode in arr_ont_barcodes:
      arr_path_ont_barcodes.append(path + '/' + barcode)
  return arr_path_ont_barcodes

#get full path to headers
def get_full_path_to_headers(directory, arr_directory_headers):
  arr_path_headers = []
  for header in arr_directory_headers:
    arr_path_headers.append(directory + header)
  return arr_path_headers

def main():
  args = get_arguments()
  #check if the projecjt directory correct
  if os.path.isdir(args.directory) == True:
    directory = args.directory
  else:
    print "Directory: " + args.directory + " not exists."
    sys.exit(1)
  #check if the CSV file path correct
  if os.path.isfile(args.csv) == True:
    csv_file = args.csv
  else:
    print "CSV file: " + args.csv + " not exists."
    sys.exit(1)

  arr_ont_barcodes = []
  arr_qbic_barcodes = []   
  with open(csv_file) as f:
    spamreader = csv.reader(f, delimiter = ',')
    for row in spamreader:
      arr_ont_barcodes.append(row[0])
      arr_qbic_barcodes.append(row[1])
 
  if len(arr_ont_barcodes) == len(arr_qbic_barcodes):
    while True:
      print "The following barcode(s) will be replaced in the subfolders " + directory + "{fastq_pass, fastq_fail, fast5_pass, fast5_fail}:\n" 
      print guideline_replace_barcodes(arr_ont_barcodes, arr_qbic_barcodes)
      print "All other files will be moved into /unclassified directory."
      if (yes_or_no("Are you sure? (y/n)")):
        break

    arr_directory_headers = ["fast5_pass", "fast5_fail", "fastq_pass", "fastq_fail"]
    
    arr_path_headers = get_full_path_to_headers(directory, arr_directory_headers)
    
    arr_path_ont_barcodes = get_full_path_to_barcodes(arr_path_headers, arr_ont_barcodes)
    
    if check_directory_exists(arr_path_ont_barcodes) == False:
      sys.exit(1)
    else:
      #rename the barcodes
      for old_barcode,new_barcode in zip(arr_ont_barcodes, arr_qbic_barcodes):
        for path in arr_path_headers:
          try:
            os.rename(path + '/' + old_barcode, path + '/' + new_barcode)
          except:
            print "Can not rename the folder: " + path + '/' + old_barcode, path + '/' + new_barcode
            sys.exit(1)
      #move files to unclassified
      for path in arr_path_headers:
        for data in glob.glob(path + "/barcode*/*"):
          try:
            shutil.move(data, path + "/unclassified")
          except:
            print "Can not move the data: " + path + '/' + data
            sys.exit(1)
      #remove empty folders
      for path in arr_path_headers:
        arr_empty_folders = glob.glob(path + "/barcode*/")
        for empty_folder in arr_empty_folders:
          try:
            shutil.rmtree(empty_folder)
          except:
            print "Can not remove the folder: " + empty_folder
            sys.exit(1)
  else:
    print "The number of ont-barcodes does NOT match to the number of qbic-barcodes."
    sys.exit(1)

if __name__ == "__main__":
  main()