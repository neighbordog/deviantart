"""
    deviantart.deviation
    ^^^^^^^^^^^^^^^^^^^^
    
    Data model of the deviation object
    
    :copyright: (c) 2015 by Kevin Eichhorn
"""

from .user import User

class Deviation(object):
	
	def __init__(self):
		self.deviationid = None
		self.printid = None
		self.url = None
		self.title = None
		self.category = None
		self.category_path = None
		self.is_favourited = None
		self.is_deleted = None
		self.author = None
		self.stats = None
		self.published_time = None
		self.allows_comments = None
		self.preview = None
		self.content = None
		self.thumbs = None
		self.videos = None
		self.flash = None
		self.daily_deviation = None
		self.excerpt = None
		self.is_mature = None
		self.is_downloadable = None
		self.download_filesize = None
		self.challenge = None
		self.challenge_entry = None
		self.motion_book = None
		self.tier_access = None
		self.html = None
		self.css = None
	
	def __repr__(self):
		return self.deviationid
					
	def from_dict(self, d):
	
		self.deviationid = d['deviationid']
		self.printid = d['printid']
		
		if 'url' in d:
			self.url = d['url']
		
		if 'title' in d:
			self.title = d['title']
		
		if 'category' in d:
			self.category = d['category']
		
		if 'category_path' in d:
			self.category_path = d['category_path']
		
		if 'is_favourited' in d:
			self.is_downloadable = d['is_downloadable']

		if 'is_deleted' in d:
			self.is_deleted = d['is_deleted']

		if 'author' in d:
			self.author = User()
			self.author.from_dict(d['author'])
			
		if 'stats' in d:
			self.stats = d['stats']
			
		if 'published_time' in d:
			self.published_time = d['published_time']
			
		if 'allows_comments' in d:
			self.allows_comments = d['allows_comments']
			
		if 'preview' in d:
			self.preview = d['preview']
			
		if 'content' in d:
			self.content = d['content']
			
		if 'thumbs' in d:
			self.thumbs = d['thumbs']
			
		if 'videos' in d:
			self.videos = d['videos']
			
		if 'flash' in d:
			self.flash = d['flash']
			
		if 'daily_deviation' in d:
			self.daily_deviation = d['daily_deviation']
			
		if 'excerpt' in d:
			self.excerpt = d['excerpt']
			
		if 'is_mature' in d:
			self.is_mature = d['is_mature']
			
		if 'is_downloadable' in d:
			self.is_downloadable = d['is_downloadable']
			
		if 'download_filesize' in d:
			self.download_filesize = d['download_filesize']
			
		if 'challenge' in d:
			self.challenge = d['challenge']
			
		if 'challenge_entry' in d:
			self.challenge_entry = d['challenge_entry']
			
		if 'motion_book' in d:
			self.motion_book = d['motion_book']

		if 'tier_access' in d:
			self.tier_access = d['tier_access']
		
		if 'html' in d:
			self.html = d['html']
			
		if 'css' in d:
			self.css = d['css']
	