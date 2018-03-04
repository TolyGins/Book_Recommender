
# Book Recommender

This project aims to build a recommender system using the Good Reads sample dataset. The project uses item-item Collaborative Filtering to provide book recommendations to the user that are available on Amazon. The final product, which is a web application, uses AWS Aurora to store the data and compute recommendation via Python. The final images and links are provided by connecting to the Amazon Product API.    

## Contents

* **Data** : This is the Goodreads dataset found here (https://github.com/zygmuntz/goodbooks-10k) along with processed correlation Matrix. 
* **Recommendendation_functions.py** : The collaborative filtering computation is is mostly implemented in Mysql for optimization using Python's Jinja2 text formatting 
* **Application.py** : This is the main file that processes user input data using Flask
* ** Amazon_API_image.py** : This file pulls urls and images from the Amazon API 
* ** Templates**: These are html files for the input and output pages of the application
* ** Static**: This is the main CSS script that builds HTML formatting as well as screenshots.
* ** Virtual_env**: This folder contains the python environment necessery for this application to run
* **Requirements.txt**: These are the necessery packages to run the application


## Deployment

The application is deployed on AWS Elastic Beanstalk using AWS Aurora as the primary database. Since this is a personal project and to save on costs, the database may be shutdown temporarily.

## Application 

The application URL is http://bookrecommender.us-west-1.elasticbeanstalk.com. I have attached the below screenshots since the application is sometimes inactive to save on database costs. 

### Input

![Input](https://github.com/TolyGins/Book_Recommender/tree/master/static/Book_Recommender_Input.png)

### Output

![Output](https://github.com/TolyGins/Book_Recommender/tree/master/static/Book_Recommender_Output.png)