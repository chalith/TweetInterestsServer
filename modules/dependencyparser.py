import requests,sys

from xml.etree import ElementTree as ET

from modules.stanfordcorenlp import StanfordCoreNLP
from modules.processtring import *
nlp = StanfordCoreNLP()

def parse(text):
    return parse_results(nlp.parse(text))

def parse_results(text):
    xml = generate_xml_tring(text)
    root = ET.fromstring(xml)
    sentences = {"sentences": []}
    for sentence in root.find("document").find("sentences"):
        cursentence = {'words':[], 'parsetree':[], 'dependencies':{}}
        cursentence["parsetree"] = sentence.find("parse").text
        for token in sentence.find("tokens"):
            word = token.find("word").text
            lemma = token.find("lemma").text
            pos = token.find("POS").text
            ner = token.find("NER").text
            cursentence["words"].append(tuple([word, {"lemma": lemma, "pos": pos, "ner": ner}]))
        for dependencies in sentence.findall("dependencies"):
            key = dependencies.attrib["type"]
            pardip = []
            for dependency in dependencies:
                pardip.append(tuple([dependency.attrib["type"],dependency.find("governor").text,dependency.find("dependent").text]))
            cursentence["dependencies"][key] = pardip
        sentences["sentences"].append(cursentence)
    return sentences