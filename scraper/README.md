# fake_news
Fake news work

This scraper is "semi-automatic". It does not scrape data automatically from a specific facebook page, but goes through already downloaded HTML of a post that should be scrapped. Reason for this is mainly because we wanted to use only data gathered from specific posts and not all of them.

scraper_comments: scrapes data about a post and it's comments (users, text, date...)
* input: HTML
* output: json file {'page': page_name,'post_content': post_content, 'post_udate': post_udate,'reactions_link': post_reactions_link, 'shares_link': post_shares_link, 'comments': comments}
 
scraper_reactions:  scrapes data about reactions to a post (users, reactions)
* input: HTML
* output: json file {'reactions_link': reactions_link, 'reactions': reactions} 

html_to_json: main function, calls methods of both scrapers and connects reactions to posts

Data for testing this code could be found here:
https://drive.google.com/drive/folders/1X2sNYPzqI86OGLZEi9BldR6Za0wesFaO?usp=sharing
