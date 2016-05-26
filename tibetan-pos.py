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

# The tibetan pos tool involves the following steps:
#
# 1. Text as you find it in the wild.
#    བྲམ་ཟེ་དེས་རྒྱལ་པོ་ལ་འདི་སྐད་ཅེས་སྨྲས་སོ༎
#    རྒྱལ་པོ་ཆེན་པོ་ཁྱོད་ཀྱི་ལུས་ལ་མར་མེ་སྟོང་བཙུགས་ཏེ།
#    མཆོད་པ་བྱེད་ནུས་ན་ཆོས་བསྟན་པར་བྱའོ་ཞེས་སྨྲས་པ་དང་ །
# 2. The tool reformats into something suiteable to the Tree Tagger
#    (achieved by replacing ༎ with །། and then adding a space after each ་ and
#    before and after །).
#    བྲམ་ ཟེ་ དེས་ རྒྱལ་ པོ་ ལ་ འདི་ སྐད་ ཅེས་ སྨྲས་ སོ ། །
#    རྒྱལ་ པོ་ ཆེན་ པོ་ ཁྱོད་ ཀྱི་ ལུས་ ལ་ མར་ མེ་ སྟོང་ བཙུགས་ ཏེ །
#    མཆོད་ པ་ བྱེད་ ནུས་ ན་ ཆོས་ བསྟན་ པར་ བྱའོ་ ཞེས་ སྨྲས་ པ་ དང་ །
# 3. Feed this as input to the Tree Tagger which produces output in the form
#    of vertical columns of the script and syllables
# 4. If we are in syllables mode we output the syllables now and stop and if not
#    we...
# 5. Apply the following rule: If a syllable ends with འི་, འོ་, ར་ or ས་ AND the
#    syllable is tagged by the word breaker with ES or SS, then insert a space
#    before the respective འི་, འོ་, ར་ or ས་ (note: we also apply the rule to the
#    form without the '་' character
# 5. Which transforms the output to this:
#    བྲམ་ཟེ་ དེ ས་ རྒྱལ་པོ་ ལ་ འདི་ སྐད་ ཅེས་ སྨྲས་ སོ ། །
#    རྒྱལ་པོ་ ཆེན་པོ་ ཁྱོད་ ཀྱི་ ལུས་ ལ་ མར་མེ་ སྟོང་ བཙུགས་ ཏེ །
#    མཆོད་པ་ བྱེད་ ནུས་ ན་ ཆོས་ བསྟན་པ ར་ བྱ འོ་ ཞེས་ སྨྲས་པ་ དང་ །
# 6. If we are in words mode we output the words now and stop and if not we...
# 7. Feed this as input to the Tree Tagger which produces output in the form of
#    vertical columns of the script and POS tags

def main():
  # Argument parsing
  script = None

  parser = argparse.ArgumentParser(prog="tibetan-pos-tool", description="Part of speech tool for Tibetan script powered by Tree Tagger.")
  group = parser.add_mutually_exclusive_group(required=sys.stdin.isatty())
  group.add_argument("script", nargs="?", default="")
  group.add_argument("-f", "--file")
  parser.add_argument("-s", "--syllables", help="Output tagged syllables only", action="store_true")
  parser.add_argument("-w", "--words", help="Output word break of input only", action="store_true")
  parser.add_argument("-p", "--pos", help="Output tagged part of speech only", action="store_true")
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
    with open(args.file, "r") as scriptfile:
      script = scriptfile.read()

  all = not args.syllables and not args.words and not args.pos

  if all:
    print "Original script..."
    print re.sub(r"\n$", "", script) + "\n"

  # Replace '༎' with two '།' chars
  newscript = re.sub(r"༎", "།།", script)
  # Replace '་' followed by non-whitespace with '་' followed by whitespace
  newscript = re.sub(r"་(?=\S)", "་ ", newscript)
  # Replace '།' preceded by non-whitespace with '།' preceded by whitespace
  newscript = re.sub(r"(?<=\S)།", " །", newscript)
  # Replace '།' followed by non-whitespace with '།' followed by whitespace
  newscript = re.sub(r"།(?=\S)", "། ", newscript)

  if all:
    print "Pre-formatted script..."
    print re.sub(r"\n$", "", newscript) + "\n"

  # Run the tree tagger on the newscript
  wordscript = callExternalCommand(treeTaggerSyllableCommand(newscript))
  # Remove last newline
  wordscript = re.sub(r"\n$", "", wordscript)

  if all:
    print "Syllable tags..."
    print re.sub(r"\n$", "", wordscript) + "\n"
  elif args.syllables:
    print wordscript
    os._exit(0)

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
      script = re.sub(r"(འི་|འོ་|ར་|ས་|འི|འོ|ར|ས)$", r" \1 ", script)
    elif syllable == "S" or syllable =="E" or syllable == "sent":
      script += " "
    newwordscript += script

  # Replace '།' not followed by '།' with a newline
  newwordscript = re.sub(r"། (?!།)", "།\n", newwordscript)
  # Remove last newline
  newwordscript = re.sub(r"\n$", "", newwordscript)

  if all:
    print "Word and sentence breaker..."
    print re.sub(r"\n$", "", newwordscript) + "\n"
  elif args.words:
      print newwordscript
      os._exit(0)

  # Run the tree tagger on the newwordscript
  newwordscript = callExternalCommand(treeTaggerPOSCommand(newwordscript))
  # Remove last newline
  newwordscript = re.sub(r"\n$", "", newwordscript)

  if all:
    print "Part of speech tags..."
    print re.sub(r"\n$", "", newwordscript)
  elif args.pos:
    print newwordscript

def treeTaggerSyllableCommand(script):
  dir = os.path.dirname(os.path.realpath(__file__))
  return "echo \"" + script + "\" | " + dir + "/scripts/tree-tagger-tibetan-syllables"

def treeTaggerPOSCommand(script):
  dir = os.path.dirname(os.path.realpath(__file__))
  return "echo \"" + script + "\" | " + dir + "/scripts/tree-tagger-tibetan"

def callExternalCommand(command):
  process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = process.communicate()
  return out

main()
