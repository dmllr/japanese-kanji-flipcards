import os
import re
from typing import List

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as RLC
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib.pagesizes import A4

from generate.svgreader import extract_drawings
from generate.palette import palette
from generate.svgutils import convert_path
from generate.kanji import Kanji

from textwrap import wrap


font_jp = "HeiseiMin-W3"
fontH = UnicodeCIDFont(font_jp, isVertical=False)
pdfmetrics.registerFont(fontH)

font_jp_v = font_jp + "-V"
fontV = UnicodeCIDFont(font_jp, isVertical=True)
fontV.name = font_jp_v
fontV.fontName = font_jp_v
pdfmetrics.registerFont(fontV)

size = A4
card_width, card_height = size[0] / 2, size[1] / 5


def T(y):
	return size[1] - y


def draw_marks(canvas: RLC.Canvas):
	mark_len = 2*mm

	canvas.setStrokeColorRGB(0.5, 0.5, 0.5)
	canvas.setLineWidth(0.01)

	canvas.line(0,                     0,               mark_len,   0)
	canvas.line(card_width - mark_len, 0,               card_width, 0)
	canvas.line(0,                     -card_height,    mark_len,   -card_height)
	canvas.line(card_width - mark_len, -card_height,    card_width, -card_height)

	canvas.line(0,                     0,               0,   -mark_len)
	canvas.line(0,                     -card_height,    0,   -card_height + mark_len)


def draw_card(canvas: RLC.Canvas, X, Y, character):
	canvas.saveState()
	canvas.translate(X, Y)

	font_size_title = 16
	font_size_content = 8
	font_size_annotation = 5
	font_size_furigana = 6
	font_size_words = 9
	font_to_mm = 0.5*mm
	margin_drawing = 6*mm
	margin_left = 2*mm
	margin_bottom = 2*mm
	margin_text = 48*mm
	margin_top = -font_size_furigana * font_to_mm
	len_vertical_text_bound = 12
	max_words_count = 6

	paths, hints = extract_drawings(character.char)

	canvas.translate(margin_drawing, -margin_drawing)
	canvas.setLineWidth(7)
	canvas.setLineCap(1)
	canvas.setLineJoin(1)
	for i, path in enumerate(paths):
		canvas.setStrokeColorRGB(*palette["strokes"][i])
		canvas.drawPath(convert_path(path, canvas))
	canvas.setLineWidth(1)
	canvas.setLineCap(0)
	canvas.setLineJoin(0)

	canvas.setFont('Helvetica', 5)
	canvas.setFillColorRGB(*palette["default"])
	for i, hint in enumerate(hints):
		canvas.drawString(*hint)

	canvas.translate(-margin_drawing, margin_drawing)

	canvas.setFont(font_jp, font_size_title)
	canvas.setFillColorRGB(*palette["default"])
	canvas.drawString(margin_left, -font_size_title * font_to_mm, character.char)

	x_ = margin_text
	canvas.setFont(font_jp_v, font_size_annotation)
	canvas.setFillColorRGB(*palette["readings_kun"])
	canvas.drawString(x_, margin_top, "kun")
	x_ = margin_text + font_size_annotation * 0.5 * mm
	canvas.setFont(font_jp_v, font_size_content)
	canvas.setFillColorRGB(*palette["readings_kun"])
	rest = character.readings_kun
	while rest:
		if len(rest) <= len_vertical_text_bound:
			text, rest = rest.strip(), ''
		else:
			dlm = len_vertical_text_bound
			while rest[dlm] != ' ':
				dlm -= 1
			text, rest = rest[:dlm], rest[dlm:].lstrip()
		canvas.drawString(x_, margin_top, text)
		x_ += font_size_content * 0.4 * mm

	x_ += 1 * mm
	canvas.setFont(font_jp_v, font_size_annotation)
	canvas.setFillColorRGB(*palette["readings_on"])
	canvas.drawString(x_, margin_top, "on")
	x_ += font_size_annotation * font_to_mm
	canvas.setFont(font_jp_v, font_size_content)
	canvas.setFillColorRGB(*palette["readings_on"])
	canvas.drawString(x_, margin_top, character.readings_on)

	x_ += font_size_words * font_to_mm + 2 * mm
	canvas.setFont(font_jp_v, font_size_annotation)
	canvas.setFillColorRGB(*palette["default"])
	canvas.drawString(x_, margin_top, "words")
	x_ += font_size_annotation * font_to_mm
	words = character.words.split('<br/>')[:max_words_count]
	y_ = -margin_top - (font_size_words + font_size_furigana * 2.5) * font_to_mm
	rightmost = 0
	for word in words:
		xl = x_
		wparts = re.split(r'[{}]', word)
		for wpart in wparts:
			if wpart and ':' in wpart:
				part, furi_part = wpart.split(':')
			else:
				part, furi_part = wpart, ''
			width_part = fontH.stringWidth(part, font_size_words)
			width_furi = fontH.stringWidth(furi_part, font_size_furigana)
			width = max(width_furi, width_part)
			canvas.setFont(font_jp, font_size_words)
			canvas.drawString(xl + width / 2 - width_part / 2, y_, part)
			canvas.setFont(font_jp, font_size_furigana)
			canvas.drawString(xl + width / 2 - width_furi / 2, y_ + font_size_furigana * font_to_mm + 1*mm, furi_part)
			xl += width
			rightmost = max(rightmost, xl)
		y_ -= font_size_words * font_to_mm + font_size_furigana * font_to_mm
	x_ += rightmost

	x_ = margin_left
	canvas.setFillColorRGB(*palette["secondary"])
	canvas.setFont(font_jp, font_size_annotation)
	canvas.drawString(x_, -card_height + margin_bottom, "components")
	canvas.setFont(font_jp, font_size_content)
	canvas.drawString(x_, -card_height + margin_bottom + font_size_annotation * font_to_mm, character.parts)

	x_ += margin_left + 12 * mm + fontH.stringWidth(character.parts, font_size_content)
	canvas.setFont(font_jp, font_size_annotation)
	canvas.drawString(x_, -card_height + margin_bottom, "radical")
	canvas.setFont(font_jp, font_size_content)
	canvas.drawString(x_, -card_height + margin_bottom + font_size_annotation * font_to_mm, character.radicals)

	canvas.setFont(font_jp, font_size_annotation)
	text = f"JLPT {character.jlpt or '-'}      #{character.frequency}"
	canvas.drawString(card_width - 5*mm - fontH.stringWidth(text, font_size_annotation), -card_height + margin_bottom, text)

	draw_marks(canvas)

	canvas.restoreState()

	print(character.char)


def draw_back(canvas: RLC.Canvas, X, Y, character):
	font_to_mm = 0.5*mm
	font_size_meanings = 10
	margin_top = 8*mm
	margin_text = 6*mm
	margin_between = 2*mm
	meanings_width = 60
	compounds_width = 58

	canvas.saveState()
	canvas.translate(X, Y)

	canvas.setFont(font_jp, font_size_meanings)

	y = -margin_top
	text = canvas.beginText(margin_text, y)
	text.setFont(font_jp, font_size_meanings)
	wraps = wrap(character.meanings, meanings_width)
	wraped_text = "\n".join(wraps)
	text.textLines(wraped_text)
	canvas.drawText(text)

	y -= margin_between + font_size_meanings * font_to_mm * len(wraps)

	def bizip(seq1, seq2):
		it1 = iter(seq1)
		it2 = iter(seq2)
		while True:
			v1 = next(it1, None)
			if v1:
				yield v1
			v2 = next(it2, None)
			if v2:
				yield v2
			if not v1 and not v2:
				break

	tsource = []
	for sentence in bizip(character.compounds_kun.split('<br/>'), character.compounds_on.split('<br/>')):
		if not sentence or sentence[0] != '{':
			continue
		jp, trans = sentence[1:].split('} ')
		if len(trans) > 300:
			# too long translation, some descriptions there
			continue
		word, furi = jp.split(':')
		if len(word) > 4:
			# too long for sample, waste of card space
			continue
		trans = ', '.join(trans.split(', ')[:4])
		trans = '\n'.join(wrap(trans, compounds_width))
		tsource.append([word, furi, trans])
	tsource = tsource[:7]

	if tsource:
		t = Table(tsource)

		font_size_compounds_kanji = 10
		font_size_compounds_readings = 6
		font_size_compounds_translation = 8
		t.setStyle(TableStyle([
			('FONT', (0, 0), (0, -1), font_jp, font_size_compounds_kanji),
			('FONT', (1, 0), (1, -1), font_jp, font_size_compounds_readings),
			('FONT', (2, 0), (2, -1), font_jp, font_size_compounds_translation),
			('LEFTPADDING', (0, 0), (-1, -1), 3),
			('RIGHTPADDING', (0, 0), (-1, -1), 3),
			('BOTTOMPADDING', (0, 0), (-1, -1), 1),
			('TOPPADDING', (0, 0), (-1, -1), 1),
			('VALIGN', (0, 0), (-1, -1), "MIDDLE"),
		]))
		t.wrapOn(canvas, card_width, card_height + y)
		t.drawOn(canvas, 0, -card_height + 1*mm)

	draw_marks(canvas)

	canvas.restoreState()


def draw_backwards(canvas: RLC.Canvas, backwards):
	canvas.showPage()

	if len(backwards) % 2 == 1:
		backwards.append(Kanji())
	L = len(backwards) & -2
	backwards[1:L:2], backwards[:L:2] = backwards[:L:2], backwards[1:L:2]

	y = T(0)
	for i, character in enumerate(backwards):
		draw_back(canvas, 0 if i % 2 == 0 else card_width, y, character)
		draw_marks(canvas)
		y -= 0 if i % 2 == 0 else card_height

	canvas.showPage()


def generate(jlpt):
	characters = []
	wd = os.path.dirname(os.path.realpath(__file__))
	with open(f'{wd}/in/kanji.tsv', 'r') as f:
		f.readline()
		for line in f:
			c = Kanji()
			c.char, c.strokes, c.frequency, c.jlpt, c.grade, c.radicals, c.parts, c.meanings, \
			c.readings_kun, c.readings_on, c.compounds_kun, c.compounds_on, c.words \
				= line.split('\t')
			c.readings_kun = c.readings_kun.replace(', ', ' ') or 'ー'
			c.readings_on = c.readings_on.replace(', ', ' ') or 'ー'
			c.words = c.words.rstrip()

			if c.jlpt == jlpt or jlpt == 'all':
				characters.append(c)

	wd = os.path.dirname(os.path.realpath(__file__))
	canvas = RLC.Canvas(f'{wd}/pdf/printable_A4_{jlpt or "extra"}.pdf')
	canvas.setPageSize(size=size)

	y = T(0)
	backwards: List[Kanji] = []
	for i, character in enumerate(characters):
		x = 0 if i % 2 == 0 else card_width
		draw_card(canvas, x, y, character)
		backwards.append(character)

		y -= 0 if i % 2 == 0 else card_height

		if y <= 0:
			draw_backwards(canvas, backwards)
			y = T(0)
			backwards = []

	draw_backwards(canvas, backwards)

	canvas.save()
