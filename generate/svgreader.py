import os


def to_code(s, pos=0):
	if not s:
		return None

	c = ord(s[pos])
	if 0xD800 <= c < 0xDC00:
		if len(s) <= pos + 1:
			return 0
		n = ord(s[pos + 1])
		if n >= 0xDC00 and c < 0xE000:
			c = 0x10000 + ((c - 0xD800) << 10) + (n - 0xDC00)
	return hex(c)[2:]


def extract_drawings(character):
	match_paths = "<g id=\"kvg:StrokePaths_"
	match_numbers = "<g id=\"kvg:StrokeNumbers_"
	match_path = "<path "
	match_text = "<text "
	match_d = " d=\""
	match_t = " transform=\""
	match_e = "\""

	char_code = to_code(character)

	wd = os.path.dirname(os.path.realpath(__file__))
	data = open(os.path.join(wd, "svg", "0" + char_code + ".svg")).read()
	data = data[data.find("<svg "):]

	data = data[data.find(match_paths):]

	paths = []
	while data.find(match_path) >= 0:
		data = data[data.find(match_path):]
		data = data[data.find(match_d) + len(match_d):]
		item = data[:data.find(match_e)]
		paths.append(item)

	data = data[data.find(match_numbers):]

	labels = []
	while data.find(match_text) >= 0:
		data = data[data.find(match_text):]
		data = data[data.find(match_t) + len(match_t):]
		item = data[:data.find(match_e)]
		data = data[data.find('>') + 1:]
		text = data[:data.find('<')]

		item = item[len('matrix(1 0 0 1 '):]
		item = item[:item.find(')')]
		coord = list(map(float, item.split(' ')))
		coord[1] *= -1  # inverse y
		labels.append((*coord, text))

	return paths, labels
