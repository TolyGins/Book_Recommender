import jinja2
import pymysql
import os


class GenerateRecommendations:
    """ After passing user's dict of books we generate recommendations on Aurora DB """
    def __init__(self, user_books, num_recs):
        self.attributes = [[book,rating] for book, rating  in user_books.iteritems()]
        self.book_numbers = [book[0] for book in user_books.iteritems()]
        self.num_recs = num_recs
        self.user_books = user_books
        try:
            self.conn = pymysql.connect(os.environ['RDS_HOST'], user=os.environ['NAME'],passwd= os.environ['RDS_PASSWORD'], db=os.environ['DB_NAME'], connect_timeout=20)
            self.cur = self.conn.cursor()
            self.conn.autocommit = True
            print 'Connection Obtained'
        except pymysql.MySQLError as e:
            print 'Problem Connecting to DB'
            print e

# Creates SQl based on user input 
# These are most correlated books to the ones the user read
    def handler_template_init(self, min_sample = 50):
        #attributes = [[book,rating] for book, rating  in example.iteritems()]
        param = jinja2.Template(
            """
        {% if attributes|length > 1 %}
            {% for att in attributes[:-1] %} # for everything but last element
            (
            SELECT
                 book_name
                , corr_value
                , {{att[1]}} AS rating
                FROM book_corr_matrix
            WHERE
                book_id = {{att[0]}} # this is the book_number
                AND sample >= {{min_sample}}
            ORDER BY corr_value DESC
            LIMIT {{num_recs}}
            )
            UNION ALL 
           {% endfor %}

              (
            SELECT
                 book_name
                , corr_value
                , {{attributes[-1][1]}} AS rating
                FROM book_corr_matrix
            WHERE
                book_id = {{attributes[-1][0]}} # this is the book_number for last element 
                AND sample >= {{min_sample}}
            ORDER BY corr_value DESC
            LIMIT {{num_recs}}
            )

        {% else %} # else run query for single value

        (SELECT
            book_name
            , corr_value
            , {{attributes[0][1]}} AS rating #rating in single book
            FROM book_corr_matrix
        WHERE
            book_id = {{attributes[0][0]}} # book_id in single book
            AND sample >= {{min_sample}}
        ORDER BY corr_value DESC
        LIMIT {{num_recs}})

        {%endif%}
        """   
        )
        return param.render(attributes = self.attributes, num_recs = self.num_recs, min_sample = min_sample)


    ## Connect and Execute SQl
    def generate_list (self, sql):
    	try :
    	    self.cur.execute(sql)
    	    result = self.cur.fetchall()
    	    if len (result)==0:
    	        print 'Got no Results!'
    	    return result
    	except Exception as e:
            print 'SQL Syntax Error:'
    	    print e

# This creates the second SQL query based on the initial list of correlated books
    def handler_template_final (self,result_from_init_list = None):
        result_from_init_list = self.generate_list(self.handler_template_init())
        book_names = [book_name[0] for book_name in result_from_init_list]
        params = jinja2.Template(
            """
            SELECT
            book_name 
            , SUM(CASE {% for num in book_numbers %} WHEN book_id = {{num}}  THEN corr_value * {{example[num]}} # weight correlation by the rating
                {% endfor %}END ) AS weighted_correlation
            , SUM(corr_value) AS sum_of_correlations
            , SUM(CASE {% for num in book_numbers %} WHEN book_id = {{num}}  THEN corr_value * {{example[num]}} 
                {% endfor %} END ) / SUM(corr_value) AS weighted_Score
            FROM book_corr_matrix
            WHERE
                book_id in  {{book_numbers}} # this will be all the user book ids
                AND  CAST(SUBSTRING(book_name, 5) as UNSIGNED) not in  {{book_numbers}} # converts to int and removes books already read
                AND  book_name in {{book_names}} # these will be all the books from first function
                AND corr_value > 0 # gets rid of nulls and negative correlations
            GROUP BY
                book_name
            ORDER BY weighted_Score DESC
            LIMIT {{num_recs}}
             """
                )
        pre = params.render(book_numbers = self.book_numbers, book_names = book_names, example = self.user_books, 
                            num_recs= self.num_recs) # renders the template
        post = pre.replace('[', '(')
        return post.replace(']', ')')

    def __del__(self):
        self.conn.close()

# Run this using example
#example = {34:4, 14:1, 4:5, 3:5, 2:5, 1:5}

#generate_recommendations = GenerateRecommendations(user_books = example, num_recs = 10)

#print generate_recommendations.generate_list(generate_recommendations.handler_template_final(example = example))

# generate_list(handler_template_init(example)) # generate initial listof correlated books

# handler_template_final (example, _ ,7) # create sql based on first step

# generate_list (_) # generate final list based on sql


#generate_list(handler_template_final(example, generate_list(handler_template_init(example)),7))