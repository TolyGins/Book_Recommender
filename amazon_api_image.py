# Amazon API
# Need to add credentials file to the base directory. Make sure the file name is hidden ".amazon-something"
from amazonproduct import API # needs module lxml

class Amazon_Api :
    """ This class connects to Amazon Product API and Pulls images, links and price into the application"""
    def __init__(self, some_dict, list_of_numbers, number_of_recs):
        self.api = API(locale='us', )
        self.image_url =[]
        self.book_numbers = [book for book in list_of_numbers if book in some_dict]
        self.isbns = [ (10 - len(i))*'0'+i if type(i) != float else i for i in  [some_dict[book_number][0] for book_number in list_of_numbers if book_number in some_dict]
        ]
        self.some_dict = some_dict
        self.list_of_numbers =list_of_numbers
        self.number_of_recs = number_of_recs

    def format_response (self, resp):
        for item in resp.Items.Item:
            try:
                self.image_url.append({'title':item.ItemAttributes.Title, 'page_url':item.DetailPageURL, 'image_url':item.LargeImage.URL,'price':item.OfferSummary.LowestNewPrice.FormattedPrice}
                                )
                break
            except AttributeError as at:
                continue

    # This function handles values where ISBN is missing
    def handle_null_isbn (self, book_number):
    	try:
    	    response =  self.api.item_search('Books', Title = self.some_dict[book_number][1], Author = self.some_dict[book_number][2], Limit = 1)
    	    for i in response:
    	        current_asin = str(i.ASIN.values.im_self)
    	        #print current_asin
    	        break
    	    resp = self.api.item_lookup(ItemId = current_asin, ResponseGroup='Images,OfferSummary,Small', IdType ='ASIN')
    	    format_response(resp)
    	except:
    		pass
    	return 'ok'

    # need breaks here due to multiple images returned
    def generate_images (self): 
        print self.isbns
        for book_number,isbn in zip (self.book_numbers, self.isbns): # book_number over all recommendations
            while len(self.image_url)< self.number_of_recs:
                #print 'booknumber is', book_number
                try:
                    if type (self.some_dict[book_number][0]) == float: # handle nulls
                        print 'null is', book_number
                        self.handle_null_isbn(book_number)
                        break
                    else :  
                        try:
                            print 'isbn is',isbn, 'book is', self.some_dict[book_number][1]
                            response = self.api.item_lookup(ItemId = isbn, ResponseGroup='Images,OfferSummary,Small', IdType ='ISBN', SearchIndex='Books')
                            self.format_response(response)
                            break
                        except :
                            self.handle_null_isbn (book_number) # run this if ISBN doesn't work
                            break
                except :
                    pass
        return self.image_url
 