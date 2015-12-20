"""
    deviantart.status
    ^^^^^^^^^^^^^^^^^
    
    Data model of the status object
    
    :copyright: (c) 2015 by Kevin Eichhorn
"""

from .user import User
from .deviation import Deviation

class Status(object):

	def __init__(self):
		self.statusid = None
		self.body = None
		self.ts = None
		self.url = None
		self.comments_count = None
		self.is_share = None
		self.is_deleted = None
		self.author = None
		self.items = None	
		
	def from_dict(self, s):
		if 'statusid' in s:
			self.statusid = s['statusid']
			
		if 'body' in s:
			self.body = s['body']
			
		if 'ts' in s:
			self.ts = s['ts']
			
		if 'url' in s:
			self.url = s['url']
			
		if 'comments_count' in s:
			self.comments_count = s['comments_count']
			
		if 'is_share' in s:
			self.is_share = s['is_share']
			
		if 'is_deleted' in s:
			self.is_deleted = s['is_deleted']
					
		if 'author' in s:
			self.author = User()
			self.author.from_dict(s['author'])
			
		if 'items' in s:
		
			self.items = ()
			
			for item in s['items']:
				status_item = {}
				status_item['type'] = item['type']
				
				if 'status' in item:
					status_item['status'] = Status()
					status_item['status'].from_dict(item['status'])
				
				if 'deviation' in item:
					status_item['deviation'] = Deviation()
					status_item['deviation'].from_dict(item['deviation'])
					
				self.items.append(status_item)
	
	def __repr__(self):		
		return self.statusid