from .scraper import Scraper

class CompetitiveCyclist(Scraper):
  def __init__(self):
    super().__init__(base_url='https://www.competitivecyclist.com',
      prod_spec_fname='competitive_prod_specs',
      prod_listing_fname='competitive_prod_listing')
  
  def _fetch_prod_listing_view(self):
    pass
