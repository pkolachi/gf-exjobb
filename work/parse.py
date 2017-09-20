from collections import Counter

def write_function_list(grammar, out_path):
    """Writes a file with all GF abstract functions."""

    funs_tuples = []
    # Generate tuples with functions names and category
    funs = ((fun, cat) for cat in grammar.categories
                       for fun in grammar.functionsByCat(cat))
    
    with open(out_path, 'w+') as f:
        for fun, cat in funs_tuples:
            f.write('{}\t{}\n'.format(fun, cat))


def read_function_list(path):
    """Read the GF abstract functions file"""
    for line in open(path, encoding='utf8'):
        fun, cat = line.strip().split('\t')
        yield (fun, cat)


GF2UD_CATS = {
    "N": "NOUN",
    "N": "PROPN",
    "PN": "PROPN",
    "A": "ADJ",
    "V": "VERB",
    "V2": "VERB",
    "V3": "VERB",
    "VV": "VERB",
    "VA": "VERB",
    "VV": "AUX",
    "VS": "VERB",
    "VQ": "VERB",
    "V2V": "VERB",
    "V2A": "VERB",
    "V2S": "VERB",
    "V2Q": "VERB",
    "VP": "VERB",
    "AdA": "ADV",
    "AdN": "ADV",
    "AdV": "ADV",
    "Adv": "ADV",
    "CAdv": "ADV",
    "IAdv": "ADV"
}

field_names = ['ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']


def parse_conllu_node(conllu_node_line):
    node_dict = dict(zip(field_names, conllu_node_line.split('\t')))
    node_dict['ID'] = int(node_dict['ID']) - 1
    node_dict['HEAD'] = int(node_dict['HEAD']) - 1
    node_dict['FEATS'] = node_dict['FEATS'].split('|')
    return node_dict


def parse_conllu_graph(conllu_graph_lines):
    return [parse_conllu_node(node_line) for node_line in conllu_graph_lines]


def parse_conllu_file(file_path):
    with open(file_path, encoding='utf-8') as f:
        current = []
        for line in f:
            if line == "\n":
                yield parse_conllu_graph(current)
                current = []
            elif not line.startswith('#'):
                current.append(line)


def generate_bigrams(graph):
    for node in graph:
        head = graph[node['HEAD']] if node['HEAD'] != -1 else None
        yield node, head


def lookupmorpho_possible_functions(node, gf_language, oov_fallback=True):
    possible_functions = [gf_function for gf_function, _, _ in gf_language.lookupMorpho(node['FORM'].lower())]
    if len(possible_functions)==0 and oov_fallback:
        possible_functions = ['OOV_' + node['UPOSTAG']]
    return possible_functions


def test_unigram_feature_generator(graph):
    for node in graph:
        yield node['LEMMA']


def test_bigram_feature_generator(graph):
    for node, head in generate_bigrams(graph):
        node_lemma = node["LEMMA"]
        head_lemma = head['LEMMA'] if head else "ROOT"
        yield node_lemma, head_lemma


def lookupmorpho_unigram_feature_generator(graph, gf_language):
    for node in graph:
        yield frozenset(lookupmorpho_possible_functions(node, gf_language))


def lookupmorpho_bigram_feature_generator(graph, gf_language):
    for node, head in generate_bigrams(graph):
        node_possible_functions = lookupmorpho_possible_functions(node, gf_language)
        head_possible_functions = lookupmorpho_possible_functions(head, gf_language) if head else ['ROOT']
        combinations = [(x, y) for x in node_possible_functions for y in head_possible_functions]
        yield frozenset(combinations)


def count_features(graphs, *graph2features):
    counters = [Counter() for _ in graph2features]
    for graph in graphs:
        for counter, graph2feature in zip(counters, graph2features):
            counter.update(graph2feature(graph))
    return counters if len(counters)>1 else counters[0]