import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
from keras.models import load_model
import json
import random
from web_scraping import scrape_product_details  # Import the web scraping function

lemmatizer = WordNetLemmatizer()

# Load intents data from JSON
intents = json.loads(open('intents.json').read())

# Load pre-trained model
model = load_model('chatbot_model.h5')

# Load words and classes from pickled files
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


def predict_class(sentence, model):
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result


def chatbot_response(msg):
    res = ""
    ints = predict_class(msg, model)

    if ints[0]['intent'] == 'product_info':
        stopwords = ['product', 'can', 'you', 'tell', 'me', 'about', 'information', 'details', 'I',
                     'wanna', 'know', 'about', 'info', 'give', 'please']
        querywords = msg.split()
        resultwords = [word for word in querywords if word.lower() not in stopwords]
        product_name = ' '.join(resultwords)  # Extract product name from user input

        if product_name:
            scraped_details = scrape_product_details(product_name)  # Scrape product details
            res = "Your requested product information\n\n" + scraped_details.to_string()  # Convert DataFrame to string for response
        else:
            res = "I couldn't find information about that product. Please try again."
    
    elif msg.startswith("get order by") or msg.startswith("my order id is ") or msg.startswith("my order id is "):
        # Implement order retrieval logic if needed
        res = "Order retrieval functionality is not implemented yet."
    
    else:
        res = getResponse(ints, intents)

    return res
