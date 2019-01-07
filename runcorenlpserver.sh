#!/bin/bash

cd /home/fcmeng/PycharmProjects/stanford/stanford-corenlp-full-2018-10-05/
java edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 600000 -annotators tokenize, ssplit, pos, lemma, ner, parse
