#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import codecs
import csv
import os
import re
import sys
import subprocess
import shutil

# The word breaker involves the following steps:
#
# 1. Text as you find it in the wild.
#    བྲམ་ཟེ་དེས་རྒྱལ་པོ་ལ་འདི་སྐད་ཅེས་སྨྲས་སོ༎
#    རྒྱལ་པོ་ཆེན་པོ་ཁྱོད་ཀྱི་ལུས་ལ་མར་མེ་སྟོང་བཙུགས་ཏེ།
#    མཆོད་པ་བྱེད་ནུས་ན་ཆོས་བསྟན་པར་བྱའོ་ཞེས་སྨྲས་པ་དང་ །
# 2. The word breaker reformats into something suiteable to the Tree Tagger
#    (achieved by replacing ༎ with །། and then adding a space after each ་ and
#    before and after །).
#    བྲམ་ ཟེ་ དེས་ རྒྱལ་ པོ་ ལ་ འདི་ སྐད་ ཅེས་ སྨྲས་ སོ ། །
#    རྒྱལ་ པོ་ ཆེན་ པོ་ ཁྱོད་ ཀྱི་ ལུས་ ལ་ མར་ མེ་ སྟོང་ བཙུགས་ ཏེ །
#    མཆོད་ པ་ བྱེད་ ནུས་ ན་ ཆོས་ བསྟན་ པར་ བྱའོ་ ཞེས་ སྨྲས་ པ་ དང་ །
# 3. Feed this as input to the Tree Tagger which produces output in the form
#    of vertical columns of the script and syllables and then apply the following
#    rule: If a syllable ends with འི་, འོ་, ར་ or ས་ AND the syllable is tagged by the
#    word breaker with ES or SS, then insert a space before the respective འི་, འོ་,
#    ར་ or ས་
# 4. Which transforms the output of the word breaker to this:
#    བྲམ་ཟེ་ དེ ས་ རྒྱལ་པོ་ ལ་ འདི་ སྐད་ ཅེས་ སྨྲས་ སོ ། །
#    རྒྱལ་པོ་ ཆེན་པོ་ ཁྱོད་ ཀྱི་ ལུས་ ལ་ མར་མེ་ སྟོང་ བཙུགས་ ཏེ །
#    མཆོད་པ་ བྱེད་ ནུས་ ན་ ཆོས་ བསྟན་པ ར་ བྱ འོ་ ཞེས་ སྨྲས་པ་ དང་ །

def main():
  # Argument parsing
  script = None

  parser = argparse.ArgumentParser(prog='wordbreaker', description='Word breaker for Tibetan script powered by Tree Tagger.')
  group = parser.add_mutually_exclusive_group(required=sys.stdin.isatty())
  group.add_argument('script', nargs="?", default="")
  group.add_argument('-file')
  args = parser.parse_args()

  script = None
  if not sys.stdin.isatty():
    script = sys.stdin.read()

  if args.script:
    script = args.script

  if args.file and not os.path.exists(args.file):
    print "Error: file '" + args.file + "' does not exist"
    os._exit(1)

  if args.file:
    with codecs.open(args.file, "r", encoding="utf-8") as scriptfile:
      script = scriptfile.read()

  # Replace '༎' with two '།' chars
  newscript = re.sub(r"༎", "།།", script)
  # Replace '་' followed by non-whitespace with '་' followed by whitespace
  newscript = re.sub(r"་(?=\S)", "་ ", newscript)
  # Replace '།' preceded by non-whitespace with '།' preceded by whitespace
  newscript = re.sub(r"(?<=\S)།", " །", newscript)
  # Replace '།' followed by non-whitespace with '།' followed by whitespace
  newscript = re.sub(r"།(?=\S)", "། ", newscript)

  # Run the tree tagger on the newscript
  wordscript = callExternalCommand(treeTaggerCommand(newscript))
  # Break it into a list of strings
  wordscript = wordscript.split("\n")
  # Remove empty lines
  wordscript = filter(None, wordscript)

  newwordscript = ""
  reader = csv.reader(wordscript, delimiter="\t")
  for row in reader:
    script = row[0]
    syllable = row[1]
    # If a syllable ends with འི་, འོ་, ར་ or ས་ AND the syllable is tagged by the
    # word breaker with ES or SS, then insert a space before the respective འི་, འོ་,
    # ར་ or ས་
    if syllable == "ES" or syllable == "SS":
      script = re.sub(r"(འི་|འོ་|ར་|ས་)$", r" \1 ", script)
    elif syllable == "S" or syllable =="E" or syllable == "sent":
      script += " "
    newwordscript += script

  # Replace '།' not followed by '།' with a newline
  newwordscript = re.sub(r"། (?!།)", "།\n", newwordscript)
  # Remove last newline
  newwordscript = re.sub(r"\n$", "", newwordscript)

  print newwordscript

def treeTaggerCommand(script):
  dir = os.path.dirname(os.path.realpath(__file__))
  return "echo \"" + script + "\" | " + dir + "/../cmd/tree-tagger-tibetan-syllables"

def callExternalCommand(command):
  process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = process.communicate()
  return out

main()
