import subprocess
import sys
import copy
from nltk.stem.wordnet import WordNetLemmatizer
import dictionary_reader as dr
import cPickle as pickle
import spell_checker as s

POSTAGGER_PATH = './ark-tweet-nlp-0.3.2'
PREPROCESSED_PATH = './preprocessed'
lmtzr = WordNetLemmatizer()

def clean_bin(filename):
	out = open(filename+'.clean','w+')
	with open(filename,'r') as f:
		for line in f:
			out.write(line[12:])
	out.close()

def pos_tag(filename):
	"""
	Return a list of pos-tagged tweets in the format of [tokens, pos]
	"""
	l = []
	output = subprocess.check_output(POSTAGGER_PATH+'/runTagger.sh '+filename,
			shell=True)
	for tweet in output.split('\n'):
		elements = tweet.split('\t')
		if len(elements)<2:
			print elements
			continue
		tokens = elements[0].split()
		pos = elements[1].split()
		l.append([tokens,pos])
	return l

def spell_check(l):
	"""
	Return a list of spell-checked, pos-tagged tweets in the format of [tokens, pos]
	"""
	ret = []
	for tweet in l:
		tokens = []
		for t in tweet[0]:
			tokens.append(s.correct(t))
		ret.append([tokens, tweet[1]])
	return ret


def reduce_form(l):
	""" Stemming/lemmatizing + drop hashtag and handles
	"""
	ret = copy.deepcopy(l)
	for tok, pos in ret:
		for idx, val in enumerate(tok):
			if (val[0]=='@' or val[0]=='#') and len(val)>1:
				val = val[1:]
				tok[idx] = val

			tag = pos[idx]
			if tag in dr.twitter2wordnet_tbl:
				tag = dr.twitter2wordnet_tbl[tag]
			else:
				continue
			
			tok[idx] = lmtzr.lemmatize(val, tag)
	return ret

if __name__ == "__main__":
	if len(sys.argv)==1:
		print 'usage: python preprocessor.py file1 file2 ...'
		sys.exit(0)
	
	arg = sys.argv[1:]
	# process every tweet file
	for filename in arg:
		clean_bin(filename)
		l = pos_tag(filename+'.clean')
		l = spell_check(l)
		print 'done spellchecking'
		l = reduce_form(l)
		pickle.dump(l, open(filename+'.pkl', 'wb+'))

