import pgf
from typing import List
from ud_treebank_test import parse_connlu_file
from collections import Counter

def abstract_functions(cnc, graph):
    """Traverses a graph and gives the abstract functions and the head for each node.
    
    Example output: 
    {
        0: {'funs': [], 'head': None},
        1: {'funs': ['tell_from_V3', 'peel_away_from_V2', 'from_Prep',], 'head': 3},
        2: {'funs': [], 'head': 3},
        3: {'funs': [], 'head': 4},
        4: {'funs': ['come_V', 'come_over_V'], 'head': 0},
        5: {'funs': ['this_Quant'], 'head': 6},
        6: {'funs': ['story_N'], 'head': 4},
        7: {'funs': [], 'head': 4}
    }
    """
    def funs(string):
        if string is None: return []
        return frozenset(
            [word for (word,_,_) in cnc.lookupMorpho(string.lower())]
        )

    def funs_dict(node):
        return dict(funs=funs(node['word']), head=node['head'])

    return {address: funs_dict(node) for address, node in graph.nodes.items()}


def to_unigram(abstr_func_dicts):
    """Gives a list of unigram occurences"""
    unigrams = []
    for adr, d in abstr_func_dicts.items():
        funcs = d['funs']
        if len(funcs) > 0:
            unigrams.append(funcs)
    return unigrams


def to_bigram(abstr_func_dicts):
    bigrams = []
    for adr, d in abstr_func_dicts.items():
        if d['head'] is not None:
            funcs = d['funs']
            head_funcs = abstr_func_dicts[d['head']]['funs']
            combinations = [(x,y) for x in funcs for y in head_funcs]
            bigrams.append(frozenset(combinations))
    return bigrams

UD_FILE = 'en-ud-dev.conllu'
if __name__ == "__main__":
    gr = pgf.readPGF('Dictionary.pgf')
    eng = gr.languages['DictionaryEng']
    graphs = parse_connlu_file(UD_FILE)
    g = graphs.__next__()
    print(Counter(to_bigram(abstract_functions(eng, g))))