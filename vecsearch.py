import argparse
import pickle
import re
import heapq
import math

inv_index = {}
index_file = None
term_dict = None
doc_norms = None

def vec_search(query, cutoff):
	global inv_index, index_file, term_dict, doc_norms
	query_terms = [term.lower() for term in query.strip(" ").split(" ")]

	doc_dot_products = {}
	for term in query_terms:
		if term not in inv_index:
			if term in term_dict:
				index_file.seek(term_dict[term][1])
				inv_index[term] = pickle.load(index_file)
			else:
				continue
		
		docs_posting = inv_index[term]

		for doc in docs_posting:
			tf = 0.5+0.5*float(inv_index[term][doc])/doc_norms[doc]
			idf = math.log2(1+term_dict[term][0])
			if doc in doc_dot_products:
				doc_dot_products[doc] += tf*idf
			else:
				doc_dot_products[doc] = tf*idf
	
	top_cutoff_docs = []

	for doc in doc_dot_products:
		if len(top_cutoff_docs) < cutoff:
			heapq.heappush(top_cutoff_docs, (-1.0*doc_dot_products[doc], doc))
			continue

		if top_cutoff_docs[0][0] < doc_dot_products[doc]:
			heapq.heappushpop(top_cutoff_docs, (-1.0*doc_dot_products[doc], doc))

	return top_cutoff_docs
			

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--query", type=str, metavar="queryfile", help="a file containing keyword queries, with each line corresponding to a query ")
	parser.add_argument("--cutoff", type=int, default=10, metavar="k", help="the number k (default 10) which specifies how many top-scoring results have to be returned for each query")
	parser.add_argument("--output", type=str, metavar="resultfile", help="the output file named resultfile which is generated by your program, which the document ids of all documents that have top-k (k as specified) highest-scores and their scores in each line (note that the output could contain more than k documents). Results for each query have to be separated by 2 newlines.")
	parser.add_argument("--index", type=str, metavar="indexfile", help="the index file generated by invidx cons program above")
	parser.add_argument("--dict", type=str, metavar="dictfile", help="the dictionary file generated by the invidx cons program above")
	args = parser.parse_args()

	if args.query is None or args.output is None or args.index is None or args.dict is None:
		print("Not all of the arguments query, output, index or dict were specified in the command")
		exit()

	global index_file, term_dict, doc_norms
	index_file = open(args.index, "rb")
	doc_norms = pickle.load(index_file)

	with open(args.dict, "rb") as dict_file:
		term_dict = pickle.load(dict_file)

	output_file = open(args.output, "w+")
	query_file = open(args.query, "r")
	query_file_text = query_file.read()

	top_pat = re.compile(r"<top>(?P<top_content>[\s\S]*?)</top>")
	query_no_pat = re.compile(r"Number:[ ]*(?P<query_no>[0-9]+)")
	query_pat = re.compile(r"Topic:[ ]*(?P<query>[\s\S]+?)\n")

	for top in top_pat.findall(query_file_text):
		query_no = query_no_pat.findall(top)[0]
		query = query_pat.findall(top)[0]
		relevant_docs = vec_search(query, args.cutoff)
		for _ in range(len(relevant_docs)):
			relevant_doc_id = heapq.heappop(relevant_docs)[1]
			output_file.write("{} 0 {} 1\n".format(query_no, relevant_doc_id))
	
	index_file.close()
	query_file.close()
	output_file.close()

if __name__ == "__main__":
	main()