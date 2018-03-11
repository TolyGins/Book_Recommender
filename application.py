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


class Data:
  """ This loads the book lookups as well as stop words that are used to search through the book dictionary""" 
  book_list = []
  book_dict = {}
  def __init__(self):
    self.pickle_book, self.pickle_words, self.json_image = open("Data/book_dict.pickle","rb"),open("Data/stop_words.pickle","rb"),open("Data/image_dict.txt", "rb") 
    self.books_dict, self.stop_words = pickle.load(self.pickle_book), pickle.load(self.pickle_words)
    #{'8353': [nan, 'The King', 'Author']}
    self.image_dict  = json.load(self.json_image)# this dictionary is based on book number lookup


# this converts book6738 to 6738
class UserInputValid():
  """ validates search of books to make sure its in our dictionary. Searches using first word and close matches algo"""
  num_wrongs = 0
  def convert_to_num (self, book_recs):
      str_book_list = []
      for i in book_recs:
          str_book_list.append (i[0].replace('book', '')) # remove book and leave number
      return str_book_list

  def similar (self, word):
      word = titlecase(word)
      first_word = str (word.partition(' ')[0])
      first_word_matches = [book for book in data.books_dict.iterkeys() if str(titlecase(first_word)) ==  str (book.partition(' ')[0]) 
                            and first_word.lower() not in data.stop_words]
      return ', '.join (first_word_matches), ','.join(difflib.get_close_matches(word, data.books_dict.keys(), n=6, cutoff=.5)) # gets  highest match

  # This validates that book is in dictionary
  def book_return (self, book):
      book = titlecase(book)
      if book in data.books_dict:
          data.num_wrongs = 0 #resets
          return book, data.books_dict[book][0]
      if len(self.similar(book))>0 and self.num_wrongs <= 3: # allows user to make 3 mistakes
          self.num_wrongs +=1
          return "<span> Copy and paste the exact title without quotes </span> Did you mean {}? ".format(self.similar(book)) 
      else:
          self.num_wrongs = 0 # resets
          return 'Sorry, we don\'t have this title'


# Initialize Objects
data = Data()
user_input = UserInputValid()

application =Flask(__name__)

@application.route("/", methods =['GET', 'POST'])
def index():
    #if user clicks the add button
    if request.method =='POST' and 'add_button' in request.form:
        book=request.form["book_name"]
        rating=request.form["rating"]
        if type (user_input.book_return(book))==tuple:  # return book if found in dictionary
            print user_input.book_return(book)[0]
            data.book_list.append(user_input.book_return(book)[0])
            print data.book_list
            data.book_dict[user_input.book_return(book)[1]] = rating # add book_number and rating to dictionary
            print data.book_list
            return render_template("index_mine.html", text = "Current Books: {}".format(','.join(data.book_list))) # show found book to user
        else: 
            return render_template("index_mine.html", text = user_input.book_return(book)) #if book not found return message from book_return     
    return render_template("index_mine.html")


# if user clicks submit

@application.route("/success", methods=['POST', 'GET'])
def success():
    #global book_list, book_dict
    if request.method=='POST' and 'submit_button' in request.form:
       temp_list = data.book_list
       temp_dict = data.book_dict 
       data.book_list =[] # clear booklist
       data.book_dict = {} # clear book dictionary upon submit
       # if user clicks submit prior to add
       if len(temp_list)== 0:
          return render_template ("index_mine.html", text = "{}".format("Please Click the 'Add Book' Button Prior to Submitting"))
       else:
          # initialize object 
          generate_recommendations = GenerateRecommendations(user_books = temp_dict, num_recs = 10)
          my_recs = user_input.convert_to_num(generate_recommendations.generate_list(generate_recommendations.handler_template_final()))
          print 'recs are', my_recs
          #initializes the object
          amazon_api = Amazon_Api(list_of_numbers = my_recs, some_dict = data.image_dict, number_of_recs = 6)
          urls = amazon_api.generate_images()
          print len (urls)
          return render_template("success.html", value = ','.join(my_recs), urls = urls)
  

if __name__ == '__main__':
    #app.debug=True
    application.run(port=5005)
