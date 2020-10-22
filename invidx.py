import argparse
import os
from bs4 import BeautifulSoup
import re
from nltk.corpus import stopwords

def main():
	# Command Line argument parsing
	parser = argparse.ArgumentParser()
	parser.add_argument("coll_path")
	parser.add_argument("indexfile")
	args = parser.parse_args()

	# Get all copus files
	coll = [os.path.join(args.coll_path, file) for file in os.listdir(args.coll_path)]

	# Indexing procedure start
	labelled_term = re.compile(r"<(?P<tag_name>[A-Z]+)>\s*(?P<tag_content>[\w._-]+)\s*</(?P=tag_name)>|(?P<simple_text>[\w._-]+)")

	stop_words = set(stopwords.words("english"))
	additional_stop_words = ["n't", "ll"]
	stop_words.update(additional_stop_words)
	inverted_indexes = {}

	for filename in coll:
		file = open(filename, 'r')
		soup = BeautifulSoup(file.read(), "lxml-xml")
		for doc in soup.find_all("DOC"):
			doc_inv_ind = {}
			doc_no = doc.DOCNO.text.strip(' ')
			full_text = str(doc.TEXT)[6:-7]
			labelled_terms = labelled_term.findall(full_text)

			# Proccessing per word labels
			last_tag = ''
			current_tag = ''
			last_term_was_tag = False
			current_term_is_tag = False
			accumulated_word = ""
			for term in labelled_terms:
				if term[0] == '':
					current_term_is_tag = False
					word_text = term[2].lower()
					if word_text != '' and word_text not in stop_words:
						if word_text in doc_inv_ind:
							doc_inv_ind[word_text] += 1
						else:
							doc_inv_ind[word_text] = 1
				else:
					current_term_is_tag = True
					word_text = term[1].lower()
					word_tag = term[0]
					current_tag = word_tag[0]
					if last_term_was_tag:
						if last_tag == current_tag:
							accumulated_word += " " + word_text
						else:
							accumulated_word = word_text
							constructed_term = last_tag + ':' + accumulated_word
							if constructed_term in doc_inv_ind:
								doc_inv_ind[constructed_term] += 1
							else:
								doc_inv_ind[constructed_term] = 1

							named_term =  'N:' + accumulated_word
							if named_term in doc_inv_ind:
								doc_inv_ind[named_term] += 1
							else:
								doc_inv_ind[named_term] = 1
					else:
						accumulated_word = word_text
				
				if (not current_term_is_tag and last_term_was_tag):
					constructed_term = last_tag + ':' + accumulated_word
					if constructed_term in doc_inv_ind:
						doc_inv_ind[constructed_term] += 1
					else:
						doc_inv_ind[constructed_term] = 1

					named_term =  'N:' + accumulated_word
					if named_term in doc_inv_ind:
						doc_inv_ind[named_term] += 1
					else:
						doc_inv_ind[named_term] = 1

				last_tag = current_tag
				last_term_was_tag = current_term_is_tag
			
			for term in doc_inv_ind:
				if term in inverted_indexes:
					inverted_indexes[term][doc_no] = doc_inv_ind[term]
				else:
					inverted_indexes[term] = {doc_no: doc_inv_ind[term]}

	print(inverted_indexes)

			

if __name__ == "__main__":
	main()