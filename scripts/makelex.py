#!/usr/bin/env python

import argparse
import os
import codecs
import csv

def main():
  # Argument parsing
  parser = argparse.ArgumentParser(prog='makelex', description='Quick script to reformat the syllable lexicon.')
  parser.add_argument('path')
  args = parser.parse_args()

  if not os.path.exists(args.path):
    print "Error: path '" + args.path + "' does not exist"
    os._exit(1)

  lexfile = args.path
  if not os.path.exists(lexfile):
    print "Error: path '" + lexfile + "' does not exist"
    os._exit(1)

  dic = {};
  with open(lexfile) as lexfile:
    reader = csv.reader(lexfile, delimiter='\t')
    for row in reader:
      if row[0] in dic:
        dic[row[0]] = dic[row[0]] + '\t' + row[1] + " -"
      else:
        dic[row[0]] = row[1] + " -"

  for key, value in dic.iteritems():
    print key + '\t' + value
main()