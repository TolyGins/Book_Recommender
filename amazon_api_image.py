# Amazon API
# Need to add credentials file to the base directory. Make sure the file name is hidden ".amazon-something"
from amazonproduct import API # needs module lxml

api = API(locale='us', )

def format_response (resp, image_url):
    for item in resp.Items.Item:
        try:
            image_url.append({'title':item.ItemAttributes.Title, 'page_url':item.DetailPageURL, 'image_url':item.LargeImage.URL,'price':item.OfferSummary.LowestNewPrice.FormattedPrice}
                            )
            break
        except AttributeError as at:
            continue

# This function handles values where ISBN is missing
def handle_null_isbn (some_dict, book_number, image_url):
	try:
	    response =  api.item_search('Books', Title = some_dict[book_number][1], Author = some_dict[book_number][2], Limit = 1)
	    for i in response:
	        current_asin = str(i.ASIN.values.im_self)
	        #print current_asin
	        break
	    resp = api.item_lookup(ItemId = current_asin, ResponseGroup='Images,OfferSummary,Small', IdType ='ASIN')
	    format_response(resp, image_url)
	except:
		pass
	return 'ok'

# format_of_response = {'title':image.ItemAttributes.Title, 'page_url':image.DetailPageURL, 'image_url':image.LargeImage.URL,'price':image.OfferSummary.LowestNewPrice.FormattedPrice
#                      }
def generate_images (list_of_numbers, some_dict): 
    image_url = []
    book_numbers = [book for book in list_of_numbers if book in some_dict]
    isbns = [ (10 - len(i))*'0'+i if type(i) != float else i for i in  [some_dict[book_number][0] for book_number in list_of_numbers if book_number in some_dict]
              ] # append zeros to bad data and keep nulls
    print isbns
    for book_number,isbn in zip (book_numbers, isbns): # book_number over all recommendations
        while len(image_url)< 6:
            #print 'booknumber is', book_number
            try:
                if type (some_dict[book_number][0]) == float: # skip over nulls for now. Could do an item search by title and author for these
                    print 'null is', book_number
                    handle_null_isbn(some_dict, book_number, image_url)
                    break
                else :  
                    try:
                        print 'isbn is',isbn, 'book is', some_dict[book_number][1]
                        response = api.item_lookup(ItemId = isbn, ResponseGroup='Images,OfferSummary,Small', IdType ='ISBN', SearchIndex='Books')
                        format_response(response,image_url)
                        break
                        #print image_url
                    except :
                        handle_null_isbn (some_dict, book_number, image_url) # run this if ISBN doesn't work
                        break
            except :
                pass
            #image_url.append(some_dict[book_number][1])
            else:
                break
    return image_url
 