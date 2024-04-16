import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk

class Process:
    def __init__(self):
        self.download_nltk_resources()
        self.stop_words = set(stopwords.words('english'))

    def download_nltk_resources(self):
        resources = ['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words', 'stopwords']
        for resource in resources:
            nltk.download(resource, quiet=True)

    def preprocess(self, query: str):
        tokens = word_tokenize(query)
        clean_tokens = [t for t in tokens if t.lower() not in self.stop_words]
        pos_tags = pos_tag(clean_tokens)
        entities = ne_chunk(pos_tags)
        return entities
    
    def simplify(self, parsed_entities):
        """
        Simplifies the preprocessed tree of entities into a readable string.
        It will include all tokens, ensuring that numbers and key terms not recognized as named entities are still included.
        """
        simplified_query = []

        for node in parsed_entities:
            if isinstance(node, nltk.Tree):
                ne = ' '.join(part[0] for part in node.leaves())
                simplified_query.append(ne)
            elif isinstance(node, tuple):
                simplified_query.append(node[0])
        return ' '.join(simplified_query)
