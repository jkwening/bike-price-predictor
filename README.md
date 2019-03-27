# Objective
Build upon data engineer expertise by incorporating machine learning to build a web app train a predictive model that can effectively analyze the price of a given bike based on specifications to assess whether the quoted price is fair, bargain, steal, or overpriced.

# Project Scope
* Used web scraping to collect dataset of bikes, price, and specifications
* Transform scraped data from multiple web sites into standardized and consistent structure and load into postgres database.
* Exploratory data analysis for additional insights and assess whether additional data cleaning is needed for preprocessing for machine learning tasks.
    * Interested in determining whether my preconceived ideas of pertinent specifications aligns to model’s notion of feature importance
* Employ scikit-learn, keras, and tensorflow for model building, including train, validation, and test sampling splits, defining preprocessing pipeline, models evaluations, and then cross-validation for fine-tuning hyperparameters for selected viable models.
* Deploy web app that utilizes trained model to provide quantitative analysis of user provide bike specification along with confidence of assessment.
* Time permitting: Setup automated system for continuously updating and expanding dateset to improve model result or factor in pricing due seasonal price changes.

# Status
After some preliminary data munging and then EDA idenfitified some data integrity issues and need for more data. Need to review data collection and transformation process to collect more data and also ensure all data is scraped correctly and exclude useless data.
