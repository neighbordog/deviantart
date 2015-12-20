"""
    deviantart.message
    ^^^^^^^^^^^^^^^^^^
    
    Data model of the message object
    
    :copyright: (c) 2015 by Kevin Eichhorn
"""

from .user import User
from .deviation import Deviation
from .status import Status
from .comment import Comment

class Message(object):

	def __init__(self):
		self.messageid = None
		self.messagetype = None
		self.orphaned = None
		self.ts = None
		self.stackid = None
		self.stack_count = None
		self.originator = None
		self.subject = None
		self.html = None	
		self.profile = None
		self.deviation = None
		self.status = None
		self.comment = None
		self.collection = None
		self.template = None
		self.template_items = None

		
	def from_dict(self, m):
	
		self.messageid = m['messageid']
		
		self.messagetype = m['type']
		
		self.orphaned = m['orphaned']
		
		if 'ts' in m:
		    self.ts = m['ts']
		    
		if 'stackid' in m:
		    self.stackid = m['stackid']
		    
		if 'stack_count' in m:
		    self.stack_count = m['stack_count']
		    
		if 'originator' in m:
		    self.originator = User()
		    self.originator.from_dict(m['originator'])
		    
		if 'subject' in m:
		    self.subject = {}
		    
		    if "profile" in m['subject']:
		        self.subject['profile'] = User()
		        self.subject['profile'].from_dict(m['subject']['profile'])
		    
		    if "deviation" in m['subject']:
		        self.subject['deviation'] = Deviation()
		        self.subject['deviation'].from_dict(m['subject']['deviation'])
		    
		    if "status" in m['subject']:
		        self.subject['status'] = Status()
		        self.subject['status'].from_dict(m['subject']['status'])
		    
		    if "comment" in m['subject']:
		        self.subject['comment'] = Status()
		        self.subject['comment'].from_dict(m['subject']['comment'])
		    
		    if "collection" in m['subject']:
		        self.subject['collection'] = m['subject']['collection']
		    
		    if "gallery" in m['subject']:
		        self.subject['gallery'] = m['subject']['gallery']
		        		        		        		        		        		    
		if 'html' in m:
		    self.html = m['html']
		    
		if 'profile' in m:
		    self.profile = User()
		    self.profile.from_dict(m['profile'])
		    
		if 'deviation' in m:
		    self.deviation = Deviation()
		    self.deviation.from_dict(m['deviation'])
		    
		if 'status' in m:
		    self.status = Status()
		    self.status.from_dict(m['status'])
		    
		if 'comment' in m:
		    self.comment = Comment()
		    self.comment.from_dict(m['comment'])
		    
		if 'collection' in m:
		    self.collection = m['collection']
		    
		if 'template' in m:
		    self.template = m['template']
		    
		if 'template_items' in m:
		    self.template_items = template_items
	
	def __repr__(self):		
		return self.messageid