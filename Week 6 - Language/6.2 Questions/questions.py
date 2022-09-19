import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = dict()

    # extract content
    for filename in os.listdir(directory):
        if not filename.endswith(".txt"):
            continue
        with open(os.path.join(directory, filename), encoding="utf8") as f: # default encoding results in UnicodeDecodeError
            contents = f.read()
            files[filename] = contents

    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    # tokenize
    tokens = nltk.word_tokenize(document)
    # convert to lowercase and remove punctuation
    s = [w.lower() for w in tokens if ((w not in string.punctuation) and (w.lower() not in nltk.corpus.stopwords.words('english')))] 
    return s

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # get set of words
    words = get_words(documents)

    # calculate IDFs
    idfs = dict()
    for word in words:
        # natural logarithm of the number of documents divided by the number of documents in which the word appears
        f = sum(word in documents[filename] for filename in documents) 
        idf = math.log(len(documents) / f) 
        idfs[word] = idf

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # get a dictionary mapping names of files to the sum of tf-idf values
    sum_tfidfs = compute_sum_tfidfs(query, files, idfs)
    # create list sorted by tf-idf value
    filenames = [k for k, v in sorted(sum_tfidfs.items(), key=lambda item: item[1], reverse=True)]

    # return a slice of size n
    return filenames[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # get matching word measures (a dictionary mapping sentences to the sum of idf values) and
    # query term densities (the proportion of words in the sentence that are also words in the query)
    mwm_qtd = compute_mwm_qtd(query, sentences, idfs)
    # create list sorted by matching word measures first then by query term density
    s = [k for k, v in sorted(mwm_qtd.items(), key=lambda item: (item[1][0], item[1][1]), reverse=True)]

    # return a slice of size n
    return s[:n]


def get_words(documents):
    """
    Returns set of words that appear at least once in any of the documents.

    @param documents    dictionary that maps names of documents to a list of words
    """
    words = set()
    for filename in documents:
        words.update(documents[filename])
    return words


def compute_sum_tfidfs(query, files, idfs):
    """
    Calculates sum of tf-idfs (number of times the term appears in the document * the IDF value for that term).

    @param query    set of words
    @param files    dictionary mapping names of files to a list of their words
    @param idfs     dictionary mapping words to their IDF values
    @ return        dictionary mapping names of files to the sum of tf-idf values for any word in the query 
                    that appears in the file
    """
    sum_tfidfs = {}
    for filename, words in files.items():
        sum_tfidf = sum([words.count(term) * idfs[term] for term in query if term in words])
        sum_tfidfs[filename] = sum_tfidf
    return sum_tfidfs


def compute_mwm_qtd(query, sentences, idfs):
    """
    Calculates matching word measures (sum of idfs) and 
    query term densities (proportion of words in the sentence that are also words in the query).

    @param query        set of words
    @param sentences    dictionary mapping sentences to a list of their words
    @param idfs         dictionary mapping words to their IDF values
    @ return            dictionary mapping sentences to tuple(matching word measure, query term density)
    """
    mwm_qtd = {}
    for sentence, words in sentences.items():
        # calculate matching word measure
        mwm = sum([idfs[term] for term in query if term in words])
        # calculate query term density
        total_words_in_sentence = float(len(words))
        sentence_words_in_query = float(sum([1 for term in query if term in words]))
        qtd = sentence_words_in_query / total_words_in_sentence
        # add to dictionary
        mwm_qtd[sentence] = (mwm, qtd)
    return mwm_qtd

if __name__ == "__main__":
    main()
