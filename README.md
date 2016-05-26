### Homage

```
I pay homage to my Spiritual Heroes:
The Virtuous Teachers,
Practicing the Excellent Path,
Praised by the Wise.
```

### Tibetan Part of Speech Tool based upon Helmut Schmid's Tree Tagger

This repository contains the parameter file and training corpus for Tibetan
language support for the Tree Tagger tool from http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/

The lexicon, corpus, and enumeration of tags are in the training/ directory and
come from http://larkpie.net/tibetancorpus/ courtesy of Dr. Nathan Hill.  These
documents needed to be edited to remove blank lines and add a end-of-sentence
tag to the lexicon of '།'

### Part of Speech Tool

The python script tibetan-pos.py acts as a wrapper/driver for the Tree Tagger
and is invoked like so:

```
./tibetan-pos.py --file test/test.txt
```

The optional flags dictate the form of the output.  With no flags all parts of
speech operations are run and the output displayed to stdout.

Required arguments are:

  script          Specify the tibetan script directly on the command line
OR
  -f --file       Specify the file containing the tibetan script

Optional flags are:

  -s --syllables  Output tagged syllables only
  -w --words      Output word break of input only
  -p --pos        Output tagged part of speech only

### Dedication

```
May whatever merit
Achieved by this task
Accrue to the cause
For the liberation of all.
```

