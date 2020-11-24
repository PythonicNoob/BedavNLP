# from rake_nltk import Rake, Metric
import re
from nltk.stem import PorterStemmer
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
# import bs4 as bs
import json
import pandas

def get_element(var, index, default=None):
    try:
        return var[index]
    except IndexError:
        return default


def get_frequency(phrase, method='inv'):
    frequencies = []
    f_frequency = 0
    for word in phrase.split(' '):
        frequency = 0
        try:
            frequency = frequency_of_words.loc[frequency_of_words['word'] == word]['count'].iloc[0] if method != 'inv' else 1/ frequency_of_words.loc[frequency_of_words['word'] == word]['count'].iloc[0]
            # print("frequency in try:",frequency)
        except IndexError:
            frequency = 0 if method != 'inv' else 1
        frequencies.append(frequency)
    if method == 'mean': f_frequency = sum(frequencies)/len(frequencies)
    elif method == 'min': f_frequency = min(frequencies)
    elif method == 'max': f_frequency = max(frequencies)
    elif method == 'inv': f_frequency = sum(frequencies)
    # f_frequency = sum(frequencies)
    # print(phrase,":",f_frequency)
    # print("Phrase, frequencies, frequency:")
    # print(phrase, frequencies, f_frequency)

    return  f_frequency

# print("sakra freq:", get_frequency("sakra"))

def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return 'n'


def text_cleaner(review):
    '''
    Clean and preprocess a review.

    1. Remove HTML tags
    2. Use regex to remove all special characters (only keep letters)
    3. Make strings to lower case and tokenize / word split reviews
    4. Remove English stopwords
    5. Lemmatize
    5. Rejoin to one string
    '''

    # 1. Remove HTML tags
    # review = bs.BeautifulSoup(review).text

    # 2. Use regex to find emoticons
    emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', review)

    # 3. Remove punctuation
    review = re.sub("[^a-zA-Z0-9]", " ", review)

    # 4. Tokenize into words (all lower case)
    review = review.lower().split()

    # # 5. Remove stopwords
    # eng_stopwords = set(stopwords.words("english")) - {'in','on','at','near', 'around'}
    # review = [w for w in review if not w in eng_stopwords]

    # 6. Join the review to one sentence
    review = ' '.join(review + emoticons)
    # add emoticons to the end
    # 7. Lemmatize
    wnl = WordNetLemmatizer()  # initialize WordNetLemmatize()
    wnl_stems = []
    token_tag = pos_tag(review.split())
    for pair in token_tag:
        if pair[1] not in pos_tags_tbr:
            res = wnl.lemmatize(pair[0], pos=get_wordnet_pos(pair[1]))
            wnl_stems.append(res)
    review = ' '.join(wnl_stems)

    return (review)

def get_id_n_location(tagged_elements):
    # tagged_elements = pos_tag(sentence.split())
    list_of_phrases = []
    curr_word = ''
    location = ''
    last_word_location = False

    id = None

    for i, el in enumerate(tagged_elements):
        # print(i,el)
        if el[1].startswith('J') or el[1].startswith('N') or el[1].startswith('PRP'):
            # print("processing location")
            if i > 0:
                    if get_element(tagged_elements,i - 1,[None])[0] in ['in', 'on', 'at', 'near', 'around', 'of']:
                        # print("Location:", el[0])
                        location += ' '+el[0]
                        last_word_location = True
                        # print(location)
                    else:
                        if last_word_location:
                            location += ' '+el[0]
                        else:
                            if curr_word == '':
                                curr_word = el[0]
                            else:
                                curr_word += ' ' + el[0]
            else: curr_word = el[0] #; print(location)
        elif el[1].startswith("VB") and get_element(tagged_elements,i - 1,[None,None])[1].startswith("TO"):
            location = el[0]
            last_word_location = True
            # pass
        elif el[1].startswith("CD"):
            if get_element(get_element(tagged_elements,i - 1,[None]), 0) in ['in', 'on', 'at', 'near', 'around', 'to', 'id', 'of', 'hospital','clinic','building', 'number'] or get_element(get_element(tagged_elements,i - 1,[None,None]),1) in ['TO','IN'] or get_element(get_element(tagged_elements,i + 1,[None]),0, default=[]) in (['id'] + common_after_words): id = el[0]
        elif "near" in el[0]:
            if last_word_location:
                location += " near"
            else:
                location = "near"
                last_word_location = True
        else:
            if curr_word != '':
                list_of_phrases.append(curr_word)
                curr_word = ''
        if len(tagged_elements) == i+1:
            if curr_word != '': list_of_phrases.append(curr_word)

    # for w in location.split(): if w.isnumeric()

    list_of_phrases = sorted(list_of_phrases, key=get_frequency, reverse=True)
    #
    # print('\n\n')
    # print("Phrases")
    query = list_of_phrases[0]
    query = ' '.join([w for w in query.split(' ') if not w in eng_stopwords])
    id = int(''.join([digit for digit in str(id) if digit.isnumeric() ])) if id is not None else None
    location = None if (len(location) == 0 or location.isspace()) else location
    for wrd in post_processing_remove_words:
        # print(wrd)
        query = query.replace(wrd, '') if query is not None else None
        location = location.replace(wrd, '') if location is not None else None
        # print("A r",location)

    return query.strip(), location.strip(), id.strip()

def get_pronoun_n_location(tagged_elements):
    # tagged_elements = pos_tag(sentence.split())
    list_of_phrases = []
    curr_word = ''
    location = ''
    last_word_location = False
    for i, el in enumerate(tagged_elements):
        if el[1].startswith('J') or el[1].startswith('N') or el[1].startswith('PRP'):
            if i > 0:
                    if get_element(tagged_elements,i - 1,[None])[0] in ['in', 'on', 'at', 'near', 'around', 'of']:
                        # print("Location:", el[0])
                        location += ' '+el[0]
                        last_word_location = True
                    else:
                        if last_word_location:
                            location += ' '+el[0]
                        else:
                            if curr_word == '':
                                curr_word = el[0]
                            else:
                                curr_word += ' ' + el[0]
            else: curr_word = el[0]

        else:
            if curr_word != '':
                list_of_phrases.append(curr_word)
                curr_word = ''
        if len(tagged_elements) == i+1:
            if curr_word != '': list_of_phrases.append(curr_word)
    list_of_phrases = sorted(list_of_phrases, key=get_frequency, reverse=True)
    #
    # print('\n\n')
    # print("Phrases")
    query = list_of_phrases[0]
    query = ' '.join([w for w in query.split(' ') if not w in eng_stopwords+post_processing_remove_words])

    for wrd in post_processing_remove_words:
        query = query.replace(wrd, '') if query is not None else None
        location = location.replace(wrd, '') if location is not None else None
        # print("A r",location)
    return query.strip(), location.strip()

# sentence = input("String:\n")
sentences = []
# sentences += ["please help me message me the detail about sakra hospital in bangalore karnataka","I need help to find a hospital with ventilators in bangalore", "Please search for appollo hospital in bangalore","Please give me details about the fortis hospital in delhi","search for columbia hospital near sarjapur road", "please tell me details of the appollo clinic near me","can you search for manipal hospitals in pune?","search for xyz near sarjapur road","search for a hospital in pune","Please find a hospital near me", ]
# sentence =
# sentences += ["Please give me directions to a hospital near me","Please give me directions to appollo hospital","Please give me directions to 29 hospital", "please give me direction to hospital with 29 id", "Please give me direction to 29th hospital", "Please give direction to hospital 29", "Please give me direction to 29 hospital", "please give direction of 29 hospital", "Please give me location for the 29th hospital","Please give direction to appollo hospital 29", "Pass directions to 21", "tell the directions to 31", "tell 32 hospital location", "give location of sakra hopital at 36 id"]
# sentences += ["are give me the location of the nearest hospital"]

sentences += ["search sakra in bangalore"]
pos_tags_tbr = ['DT'] #Position tags to be removed while cleaning text

frequency_of_words = pandas.read_csv('unigram_freq.csv')

dir_words = ["direction","way","path","location","position","spot","place",]#"directions","positions","paths"
dir_words.extend([word+"s" for word in dir_words])
# near_words = ""
common_after_words = ["id","hospital","clinic", "informary", 'dispensary','building', 'number']
# eng_stopwords = set(stopwords.words("english")) - {'in','on','at','near', 'around'}
eng_stopwords = stopwords.words("english")
post_processing_remove_words = dir_words+common_after_words
with open("post_processing_words_tbr.txt","r") as file:
    post_processing_remove_words += [line.strip() for line in file.readlines()]

def main():
    for sentence in sentences:
        print(sentence)
        sentence = text_cleaner(sentence)
        print("Cleaned sentence:",sentence)
        tagged_elements = pos_tag(sentence.split())
        asking_direction = False
        for word, tp in tagged_elements:
            print("pos_tag:",word, tp)
            if tp.startswith("N"):
                for trgt in dir_words:
                    if word in trgt and len(word)>2: asking_direction = True  # make it so it matches words rather trying to find a word
        if asking_direction:
            qry, location, id = get_id_n_location(tagged_elements)
            print("Query:", qry, "location:", location, "id:", id)
        else:
            qry, location = get_pronoun_n_location(tagged_elements)
            print("Query:", qry, "location:", location)
        print()

def process_sentence(text):
    sentence = text_cleaner(text)
    # print("cleaned sentence:",sentence)
    tagged_elements = pos_tag(sentence.split())
    asking_direction = False

    for word, tp in tagged_elements:
        # print("pos_tag:",word, tp)
        if tp.startswith("N"):
            for trgt in dir_words:
                if word in trgt and len(
                    word) > 2: asking_direction = True  # make it so it matches words rather trying to find a word
    if asking_direction:
        qry, location, id = get_id_n_location(tagged_elements)
        data = {
            "location": location,
            "id": id
        }
        return data
    else:
        qry, location = get_pronoun_n_location(tagged_elements)
        data = {
            "keyword" : qry,
            "location": location
        }
        return data

if __name__ == '__main__': main()