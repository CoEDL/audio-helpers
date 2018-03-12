#!/usr/bin/env python

import sys, os, re
from collections import defaultdict
from argparse import ArgumentParser

RE_WAV = re.compile(ur"^[^.].*?_[\d\.]+_[\d\.]+[ct]\.wav$")

def sortKey(path):
	return float(os.path.basename(path).split("_")[1])

def groupWavs(paths):
	groups = defaultdict(list)

	for path in paths:
		file = os.path.basename(path)

		if file.lower().endswith("c.wav"):
			group = file.split("_")[0] + "_careful.wav"

		elif file.lower().endswith("t.wav"):
			group = file.split("_")[0] + "_translation.wav"

		else:
			raise Exception()

		groups[group].append(path)

	for group in groups:
		groups[group] = sorted(groups[group], key = sortKey)

	return groups

def mergeWavs(outPath, wavPaths):
	lastTs = 0.000
	tmpPath = os.path.join(os.path.dirname(outPath), "_tmp_" + os.path.basename(outPath))
	tmpPath2 = os.path.join(os.path.dirname(outPath), "_tmp2_" + os.path.basename(outPath))

	for wavPath in wavPaths:
		_, f, t = os.path.basename(wavPath).split("_")
		t = t[: t.lower().find(".wav") - 1]
		fromTs, toTs = float(f), float(t)
		padStart = fromTs - lastTs

		# Write the first file.
		if lastTs == 0.000:
			os.system("sox \"%s\" \"%s\" pad %s 0" % (wavPath, outPath, padStart))

		# Write other files.
		else:
			os.system("sox \"%s\" \"%s\" pad %s 0" % (wavPath, tmpPath, padStart))
			os.system("sox \"%s\" \"%s\" \"%s\"" % (outPath, tmpPath, tmpPath2))
			os.remove(tmpPath)
			os.rename(tmpPath2, outPath)

		lastTs = toTs

def main():
	parser = ArgumentParser(description = __doc__)
	parser.add_argument("-i", "--input-wav-dir", required = True, help = "input WAV file directory")
	parser.add_argument("-o", "--output-wav-dir", required = True, help = "output (merged) WAV file directory")

	args = parser.parse_args()
	wavPaths = []

	for root, dirs, files in os.walk(args.input_wav_dir):
		for file in files:
			if RE_WAV.search(file.lower()):
				wavPaths.append(os.path.join(os.path.abspath(root), file))

	wavPaths = groupWavs(wavPaths)

	for group in wavPaths:
		mergeWavs(os.path.join(args.output_wav_dir, group), wavPaths[group])

if __name__ == "__main__":
	main()
