#!/bin/python

# command line to transform ci.dot in ci.svg :
# dot -Tsvg ci.dot > ci.svg

import sys
import argparse
from CI_list import CI_list
from Translations_manager import Translations_manager
from mylib.Notifier import Notifier

def create_graph_for_language(translations_manager, lang, output_directory, base_name):
    translate = translations_manager.get_translateur(lang).translate
    file_name = output_directory + base_name + '-' + lang + '.dot'
    yaml_file = open(file_name, 'w')
    yaml_file.write(ci_list.to_graphviz(translate))
    yaml_file.close()

parser = argparse.ArgumentParser(description='Create a graph of ci in a dot file(graphviz).')
parser.add_argument('input_file', help='the xml file of CI')
parser.add_argument('output_directory', help='the directory where the dot file produced will go')
parser.add_argument('-lf', '--lang_file', help='file with a list of the languages', default='languages.yml')
parser.add_argument('-d', '--yaml_directory', help='the directory where to read yaml files for translations', default='translations')
parser.add_argument('-l', '--lang', help='Languages in which the graphs are created, "all" for all languages', default='all')
parser.add_argument('-n', '--base_name', help='The name in use to create the files, "base_name-lang.dot"', default='ci')

args = parser.parse_args()

ci_list = CI_list([])
ci_list.load_xml(args.input_file)

translations_manager = Translations_manager(args.lang_file, args.yaml_directory)
translations_manager.load_yaml_file()



if(args.lang != 'all'):
    if(args.lang in translations_manager.get_languages()):
        create_graph_for_language(translations_manager, args.lang, args.output_directory, args.base_name)
    else:
        print(args.lang + ' unknown, look at the ' + args.yaml_directory + ' file')
else:
    for lang in translations_manager.get_languages():
        create_graph_for_language(translations_manager, lang, args.output_directory, args.base_name)
