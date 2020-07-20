if __name__ == "__main__":
	from generate.gen import generate

	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--jlpt', metavar='jlpt', type=str, default="all")
	args = parser.parse_args()

	generate(jlpt=args.jlpt)
