from collections import Counter, Iterable, defaultdict
import pgf


def parse_conllu_file(file_path: str):
    '''
    Reads a conllu_file and gives an iterator of all graphs in the file, each graph is
    given as a list of its nodes sorted by id.
    :param file_path:
    :return:
    '''
    with open(file_path, encoding='utf-8') as f:
        current = []
        for line in f:
            if line == "\n":
                yield [UDNode(node_line) for node_line in current]
                current = []
            elif not line.startswith('#'):
                current.append(line)


def count_features(graphs, *feature_generators):
    '''
    This function takes an iterable of UD-graphs and a set of occurrence generators. An occurrence generator is a
    function accepting one graph and returning a list of occurrences for this graph. One occurrence typically consist of
    a set of features describing one node in the graph so that each node in the graph will result in one
    occurrence. The feature sets making up each occurrence must be hashable. For each occurrence generator this method
    will return a Counter giving the total counts over all graphs for each unique feature set given by
    that occurrence generator.
    :param graphs:
    :param graph2features: a function taking a graph and returning a list of hashable objects
    :return:
    '''
    counters = [Counter() for _ in feature_generators]
    for graph in graphs:
        for counter, feature_generator in zip(counters, feature_generators):
            counter.update(feature_generator.generate_features(graph))
    return counters if len(counters) > 1 else counters[0]


#CONLLU_FIELD_NAMES = ['ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
class UDNode:
    def __init__(self, conllu_node_line):
        field_values = conllu_node_line.split('\t')
        self.id = int(field_values[0]) - 1
        self.form = field_values[1]
        self.lemma = field_values[2]
        self.upostag = field_values[3]
        self.xpostag = field_values[4]
        self.feats = field_values[5].split('|')
        self.head = int(field_values[6]) - 1
        self.deprel = field_values[7]
        self.deps = field_values[8]
        self.misc = field_values[9]

    def __str__(self):
        return 'UDNode ' + self.form + ' (' + str(self.head) + ')'

    def __repr__(self):
        return self.__str__()


class FeatureGenerator:
    def __init__(self, gf_language, gf_grammar, use_bigrams=False, use_deprel=False, filter_possible_functions=True,
                 oov_fallback=True, use_gf_cats_for_fallback=False, filter_node_categories=None):
        self.gf_language = gf_language
        self.gf_grammar = gf_grammar
        self.use_bigrams = use_bigrams
        self.use_deprel = use_deprel
        self.filter_possible_functions = filter_possible_functions
        self.oov_fallback = oov_fallback
        self.use_gf_cats_for_fallback = use_gf_cats_for_fallback
        self.filter_node_categories = filter_node_categories
        # Generated by script in extract-ud2gf-cat-labels.py and data from the ud2gf UDTranslate.labels
        self.POSSIBLE_GF_CATS_BY_UD_CAT = defaultdict(list, {'NOUN': ['N'],
                                         'PROPN': ['PN'],
                                         'ADJ': ['A', 'AdA'],
                                         'VERB': ['V', 'V2', 'V3', 'VV', 'VA', 'VS', 'VQ', 'V2V', 'V2A', 'V2S', 'V2Q'],
                                         'AUX': ['VV'],
                                         'ADV': ['AdA', 'AdN', 'AdV', 'Adv', 'IAdv', 'Subj'],
                                         'CONJ': ['Conj'],
                                         'PRON': ['Pron', 'NP', 'Det', 'IP'],
                                         'DET': ['Predet', 'Det', 'IDet', 'Quant', 'IQuant'],
                                         'INTJ': ['Interj'],
                                         'ADP': ['Prep'],
                                         'SCONJ': ['Subj']})

    def _possible_functions(self, node):
        '''
        Gives all possible GF-functions for a node given its FORM and a given concrete grammar.
        :param node:
        :param gf_language:
        :param oov_fallback:
        :return:
        '''
        possible_categories = self.POSSIBLE_GF_CATS_BY_UD_CAT[node.upostag]
        possible_functions = [gf_function
                              for gf_function, _, _
                              in self.gf_language.lookupMorpho(node.form.lower())]
        if self.filter_possible_functions:
            possible_functions = [gf_function for gf_function in possible_functions
                                  if self.gf_grammar.functionType(gf_function).cat in possible_categories]
        if len(possible_functions) == 0 and self.oov_fallback:
            if self.use_gf_cats_for_fallback:
                return ['OOV_' + gf_cat for gf_cat in possible_categories]
            else:
                return ['OOV_' + node.upostag]
        else:
            return possible_functions

    def generate_features(self, graph):
        for node in graph:

            if self.filter_node_categories and (node.upostag not in self.filter_node_categories):
                continue

            node_possible_functions = self._possible_functions(node)

            if self.use_bigrams:
                if node.head != -1:
                    head_possible_functions = self._possible_functions(graph[node.head])
                else:
                    head_possible_functions = ['ROOT']
                possible_features = [[x, y] for x in node_possible_functions for y in head_possible_functions]
            else:
                possible_features = [[x] for x in node_possible_functions]

            if self.use_deprel:
                for feature in possible_features:
                    feature.append(node.deprel)
            yield frozenset([tuple(x) for x in possible_features])


class TestFeatureGenerator:
    def __init__(self, use_bigrams=False):
        self.use_bigrams=use_bigrams

    def generate_features(self, graph):
        for node in graph:
            node_lemma = node.lemma
            head_lemma = graph[node.head] if node.head != 0 else "ROOT"
            if self.use_bigrams:
                yield node_lemma, head_lemma
            else:
                yield node_lemma


def write_function_list(grammar, out_path):
    '''
    Writes a file with all GF abstract functions.
    :param grammar: pgf.PGF
    :param out_path: str
    :return:
    '''

    funs_tuples = []
    # Generate tuples with functions names and category
    funs = ((fun, cat) for cat in grammar.categories
            for fun in grammar.functionsByCat(cat))

    with open(out_path, 'w+') as f:
        for fun, cat in funs_tuples:
            f.write('{}\t{}\n'.format(fun, cat))


def read_function_list(path):
    """
    Read the GF abstract functions file
    :param path:
    :return:
    """
    for line in open(path, encoding='utf8'):
        fun, cat = line.strip().split('\t')
        yield (fun, cat)
