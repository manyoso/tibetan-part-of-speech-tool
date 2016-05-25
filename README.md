### Homage

```
I pay homage to my Spiritual Heroes:
The Virtuous Teachers,
Practicing the Excellent Path,
Praised by the Wise.
```

### Tibetan support for Helmut Schmid's Tree Tagger

This repository contains the paramater file and training corpus for Tibetan language support for the
Tree Tagger tool from http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/

The lexicon, corpus, and enumeration of tags are in the tibetan/ directory and come from
http://larkpie.net/tibetancorpus/ courtesy of Dr. Nathan Hill.  These documents needed to be edited
to remove blank lines and add a end-of-sentence tag to the lexicon of '།'

### Syllable Tagger
The resultant tibetan-syllable-utf8.par parameter file was generated with this command:

```
bin/train-tree-tagger -st sent -utf8 tibetan/2016-04-30-syllables-lexicon.txt tibetan/tibetan-syllables-tags.txt tibetan/2016-04-30-syllables-training.txt lib/tibetan-syllables-utf8.par
```

To test:

```
cat tibetan/test/syllables.txt | cmd/tree-tagger-tibetan-syllables
```

### POS Tagger
The resultant tibetan-utf8.par parameter file was generated with this command:

```
bin/train-tree-tagger -st sent -utf8 tibetan/2016-04-30-pos-lexicon.txt tibetan/tibetan-pos-tags.txt tibetan/2016-04-30-pos-training.txt lib/tibetan-utf8.par
```

To test:

```
cat tibetan/test/pos.txt | cmd/tree-tagger-tibetan
```

### Dedication

```
May whatever merit
Achieved by this task
Accrue to the cause
For the liberation of all.
```

