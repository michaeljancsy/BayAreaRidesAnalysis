class Trail:
    def __init__(self, 
                 name, 
                 relative_url, 
                 desc_short, 
                 rating_fun, 
                 rating_scenic,
                 rating_aerobic, 
                 rating_technical, 
                 composition):
        
        # from homepage
        self.name = name
        self.relative_url = relative_url
        self.desc_short = desc_short
        self.rating_fun = rating_fun
        self.rating_scenic = rating_scenic
        self.rating_aerobic = rating_aerobic
        self.rating_technical = rating_technical
        self.composition = composition
        
        # from trail page 
        self.desc_long = None

    def __repr__(self):
        return self.name
        
    def extract_trails_from_soup(soup):
        """Extracts Trail objects from a bs4.BeautifulSoup of the homepage"""
        trails = []
        for snippet_html in Trail._get_snippets_html(soup):
            trails.append(Trail._make_trail(snippet_html))
        return trails
        
    def _get_snippets_html(soup):
        """Finds all the <tr class="even"> and <tr class="odd>
        
        These table rows correspond to snippets
        """
        return soup.find_all(name='tr', attrs=['even', 'odd'])
    
    def _make_trail(snippet_html):
        """Creates a Trail from the snippet_html extracted with `_get_snippets_html(soup)`"""
        name, relative_url, description = Trail._get_name_relurl_and_desc(snippet_html)
        fun_rating = Trail._get_rating(snippet_html, 'fun')
        scenic_rating = Trail._get_rating(snippet_html, 'scenic')
        aerobic_rating = Trail._get_rating(snippet_html, 'aerobic')
        technical_rating = Trail._get_rating(snippet_html, 'technical')
        composition = Trail._get_composition(snippet_html)
        return Trail(name, 
                     relative_url, 
                     description, 
                     fun_rating, 
                     scenic_rating,
                     aerobic_rating,
                     technical_rating, 
                     composition)

    def _get_rating(snippet_html, category):
        """Gets the specified rating from snippet html
        
        The rating <div> looks like this:
        
            <div class="rating-container-fun">
            <div style="WIDTH: 20%;">2</div>
            </div>         
        """
        attr = 'rating-container-{category}'.format(category=category)
        ratings_table_html = snippet_html.find('td', 'listingratings')
        category_html = ratings_table_html.find('div', attr)
        return int(list(list(category_html.children)[1])[0])

    def _get_name_relurl_and_desc(snippet_html):
        
        """Extracts name, relative url, and description from <p class="snippet">
        
        The first (name and url) <p class="snippet"> looks like this:
        
            <p class="snippet">
             <span class="snippettitle">
              <b>
               <a href="rides/alamedacreek">
                Alameda Creek Trail
               </a>
              </b>
             </span>
            </p>
            
        The second (description) <p class="snippet"> looks like this:
        
            <p class="snippet">
             A casual ride on an easy and flat recreational trail that is not too special other than being somewhat more scenic than usual and giving you a choice of paved or dirt riding.
            </p>
        
        """
        name_and_url_part, desc_part = snippet_html.find_all('p', 'snippet')
        name = name_and_url_part.get_text()
        relative_url = name_and_url_part.find('a').get('href')
        desc = desc_part.get_text()
        return name, relative_url, desc
    
    def _get_composition(snippet_html):
        """Extracts the trail composition (% singletrack, etc.)

        Returns:
            dict - e.g. {"SINGLETRACK": .68, ...}

        The trailtype `<span>` looks like this:

            <span class="trailtype">
             <span class="type_singletrack" style="width: 272px;">
              68% SINGLETRACK
             </span>
             <span class="type_fireroad" style="width: 128px;">
              32% FIRE ROAD
             </span>
            </span>    
        """
        composition = {}
        for child in snippet_html.find('span', 'trailtype').find_all('span'):
            text = child.get_text()
            try:
                val, component = text.split(' ', maxsplit=1)
                val = val.strip('%')
                component = component.replace(" ", "_").lower()
                composition[component] = float(val)/100.
            except:
                continue
        if not Trail._composition_is_valid(composition):
            warn("Composition is not valid")
        return composition
    
    def _composition_is_valid(composition):
        total = 0
        for val in composition.values():
            total += val
        return total > .99 and total < 1.01
    
    def set_description(self, trail_page_soup):
        desc_long = ''
        for p in trail_page_soup.find_all('p', attrs=False):
            desc_long += p.get_text() + '\n'
        self.desc_long = desc_long
        
    def to_dict(self):
        """Used for converting each trail to a pandas dataframe row"""

        # base features
        dict_ = {
            'name': self.name,
            'desc_short': self.desc_short,
            'desc_long': self.desc_long,
            'rating_fun': self.rating_fun,
            'rating_scenic': self.rating_scenic,
            'rating_aerobic': self.rating_aerobic,
            'rating_technical': self.rating_technical
        }
        
        # composition features
        for component_name, val in self.composition.items():
            dict_['composition_' + component_name] = val

        return dict_
