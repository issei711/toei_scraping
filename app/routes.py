from flask import jsonify, Blueprint, render_template
from app.scraper import toei_scraping_main

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Flask App is running!"

@main.route('/scraping', methods=['GET'])
def scraping():
    toei_scraping_main()
    return render_template('scraping.html')
