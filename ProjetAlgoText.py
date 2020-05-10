import glob, os
from urllib.request import urlopen
import requests
import re
import shutil, sys
import pathlib
from collections import Counter
import math

from nltk import corpus

src = "/home/nouara/orgTP2/pages_web/"
dir_path = os.path.dirname(os.path.realpath(__file__))
WORD_REGEXP = re.compile(r"[\w']+")

#Remove html tags from a string
def removeTags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def ConvTextToVect(text):
    word = WORD_REGEXP.findall(text)
    return Counter(word)

def getFileList():
	fileList = []
	broken = []
	lst = os.listdir(src)
	for root, dirs, files in os.walk(src):
		for filename in files:
			path = os.path.join(root,filename)
			if os.path.islink(path):
				target_path = os.readlink(path)
				# Resolve relative symlinks
				if not os.path.isabs(target_path):
					target_path = os.path.join(os.path.dirname(path),target_path)
				if not os.path.exists(target_path):
					broken.append(path)
				else:
					fileList.append('file://'+path)
			else:
				fileList.append('file://'+path)
				continue
	return fileList


def readFile(url):
	text =''
	try:
		text = urlopen(url).read()
	except urllib.URLError as e:
		print("An error ")
	finally:
		return removeTags(str(text).replace('\\n', ''))


def deleteSimilarPage(UrlList):
    for i in range(len(UrlList)):
        for j in range(i + 1, len(UrlList)):
             try:
                A = ConvTextToVect(readFile(UrlList[i]))
                B = ConvTextToVect(readFile(UrlList[j]))
                res = get_cosine(A,B)
                if(res>0.95):
                    UrlList.remove(UrlList[i])
             except IndexError:
                pass

#######################################
######### APPLICATION TESTS ###########
#######################################

fileList = getFileList()
deleteSimilarPage(fileList)


#Pour déterminer la page  la plus proche d'une requête donnée (le plus pertinent sémantiquement sur cette requête)

from gensim import corpora, similarities
# corpus is your text, tokenized
dictionary = corpora.Dictionary(corpus)
# transform the corpus into vectors
# Bag of words (BOW) is an algorithm like word2vec, to transform words into vectors
vectors_corpus = [dictionary.doc2bow(text) for text in corpus]
# Build your similarity matrix
matrix = similarities.MatrixSimilarity(vectors_corpus)
# Query is your search query
query = "Does it work"
vector_query = dictionary.doc2bow(query.lower.split())
similarity = matrix[vector_query]
# Now we see which document is closer to the search query
print(list(enumerate(similarity)))



