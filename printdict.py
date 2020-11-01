import pickle
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("indexfile_dict", help="name of the generated index dictionary file")
	args = parser.parse_args()

	indexfile_dict = open(args.indexfile_dict, "rb")
	index_dict = pickle.load(indexfile_dict)
	indexfile_dict.close()

	for indexterm in index_dict:
		val_indexterm = index_dict[indexterm]
		print("\"{}\":{}:{}".format(indexterm, val_indexterm[0], val_indexterm[1]))

if __name__ == "__main__":
	main()