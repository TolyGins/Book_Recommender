from flask import Flask, render_template, request, redirect, url_for
import jinja2
import difflib
import pandas
import cPickle as pickle
import json
from  recommendation_functions import *
from amazon_api_image import *
from titlecase import titlecase
import time
#import nltk #nlp stopwords
#nltk.download('stopwords')


# add script for data
# add script for validating user_input
# add script for recommendations

# global 
num_wrongs = 0 
book_list = []
book_dict = {}


pickle_book, pickle_words, json_image = open("Data/book_dict.pickle","rb"),open("Data/stop_words.pickle","rb"),open("Data/image_dict.txt", "rb") 

books_dict, stop_words = pickle.load(pickle_book), pickle.load(pickle_words)

#{'8353': [nan, 'The King', 'Author']}
image_dict  = json.load(json_image)# this dictionary is based on book number lookup

# for book_name, value in books_dict.iteritems():
#     image_dict[str (value[0])]= [value[5], book_name, value[7]] 


# this convers book6738 to 6738
def convert_to_num (book_recs):
    book_list = []
    for i in book_recs:
        book_list.append (i[0].replace('book', '')) # remove book and leave number
    return book_list


# def similar (word):
#     return difflib.get_close_matches(word, books_dict.keys(), n=6, cutoff=.5) # gets  highest matches

def similar (word):
    word = titlecase(word)
    first_word = str (word.partition(' ')[0])
    first_word_matches = [book for book in books_dict.iterkeys() if str(titlecase(first_word)) ==  str (book.partition(' ')[0]) 
                          and first_word.lower() not in stop_words]
    return ', '.join (first_word_matches), ','.join(difflib.get_close_matches(word, books_dict.keys(), n=6, cutoff=.5)) # gets  highest match

# This validates that book is in dictionary
def book_return (book):
    global num_wrongs
    book = titlecase(book)
    if book in books_dict:
        num_wrongs = 0 #resets
        return book, books_dict[book][0]
    if len(similar(book))>0 and num_wrongs <= 2: # allows user to make 2 mistakes
        num_wrongs +=1
        return "<span> Copy and paste the exact title without quotes </span> Did you mean {}? ".format(similar(book)) 
    else:
        num_wrongs = 0 # resets
        return 'Sorry, we don\'t have this title'


# create a function that clears global variables upon refresh


application =Flask(__name__)

@application.route("/", methods =['GET', 'POST'])
def index():
    global book_list
    #if user clicks the add button
    if request.method =='POST' and 'add_button' in request.form:
        book=request.form["book_name"]
        rating=request.form["rating"]
        # print 'input is', book
        # print 'return from function is', book_return(book)
        # print num_wrongs
        if type (book_return(book))==tuple:  # return book if found in dictionary
            print book_return(book)[0]
            book_list.append(book_return(book)[0])
            print book_list
            book_dict[book_return(book)[1]] = rating # add book_number and rating to dictionary
            print book_list
            #print book_dict
            #return redirect(url_for('index', value = "Current Books are {}".format(book_list)))
            return render_template("index_mine.html", text = "Current Books: {}".format(','.join(book_list))) # show found book to user
        else: 
            return render_template("index_mine.html", text = book_return(book)) #if book not found return message from book_return     
    return render_template("index_mine.html")


# if user clicks submit

@application.route("/success", methods=['POST', 'GET'])
def success():
    global book_list, book_dict
    if request.method=='POST' and 'submit_button' in request.form:
       temp = book_list
       temp_dict = book_dict 
       book_list =[] # clear booklist
       book_dict = {} # clear book dictionary upon submit
       #time.sleep(5)
       if len(temp)== 0:
          return render_template ("index_mine.html", text = "{}".format("Please Click the 'Add Book' Button Prior to Submitting"))
       else:
          my_recs = convert_to_num (generate_list
                                (handler_template_final(temp_dict, generate_list(handler_template_init(temp_dict)),10)) # provide 7 recommendations
                                )
          print 'recs are', my_recs
          urls = generate_images(my_recs, image_dict)
          print len (urls)
          return render_template("success.html", value = ','.join(my_recs), urls = urls)
       #return redirect(url_for('index'))   


    #return redirect(url_for('success'))

    #"Book List Submitted {}".format(book_list))
    #return render_template("success.html", text = "Book List Submitted{}".format(book_list))
    

	#return render_template("success.html",)
    #return render_template('index_mine.html', text="Seems like we got something from that email once!")
#success([])


if __name__ == '__main__':
    #app.debug=True
    application.run(port=5005)
