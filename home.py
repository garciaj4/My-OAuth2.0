from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
import webapp2
import json
import os
import base64
import uuid
from webapp2_extras import sessions
import urllib

#https://gist.github.com/jgeewax/2942374
config = {}
config['webapp2_extras.sessions'] = {
	'secret_key': 'superSecret',
}

myClientId = '208594160583-i4mk1mt5ncvm41u7hai6t475eskcm8mi.apps.googleusercontent.com'
myClientSecret = '4tJLjBuT5JCeNkUJ1Gj8cN3u'
myClientURL = 'https://myoauth-211216.appspot.com'

#http://webapp2.readthedocs.io/en/latest/api/webapp2_extras/sessions.html
class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

class MainPage(BaseHandler):
	def get(self):

		home_values = {
			'redirectURL': myClientURL + '/OAuth'
		}

		path = os.path.join(os.path.dirname(__file__), 'home.html')
		self.response.out.write(template.render(path, home_values))

class googleRedirect(BaseHandler):
	def get(self):
		#if we already have a token stored
		if(self.session.get('token')):

			#build an http get request to get the users data
			googleDataURL = 'https://www.googleapis.com/plus/v1/people/me'
			token = 'Bearer ' + self.session.get('token')
			headers = {'authorization': token}
			result = urlfetch.fetch(url=googleDataURL, headers=headers)

			result_data = json.loads(result.content)

			display_values = {
				'fname': result_data['name']['givenName'],
				'lname': result_data['name']['familyName'],
				'URL': result_data['url'],
				'state': self.session.get('state')
			}

			path = os.path.join(os.path.dirname(__file__), 'display.html')
			self.response.out.write(template.render(path, display_values))
			#self.response.write(result_data)
		
		elif(self.request.get('state')):
			if(self.session.get('state') == self.request.get('state')):
				googleURL = 'https://www.googleapis.com/oauth2/v4/token'
				payload = urllib.urlencode({
					'code':self.request.get('code'),
					'client_id': myClientId,
					'client_secret': myClientSecret,
					'redirect_uri': myClientURL + '/OAuth',
					'grant_type': 'authorization_code'
				})

				result = urlfetch.fetch(googleURL, method=urlfetch.POST, payload=payload)
				result_data = json.loads(result.content)

				self.session['token'] = result_data['access_token']

				self.redirect(myClientURL + '/OAuth')
				#self.response.write(result_data)
			else:
				self.response.write('Invalid State Returned')

		else:
			myState = base64.urlsafe_b64encode(uuid.uuid4().bytes)
			myState = myState.replace('=', '')

			self.session['state'] = myState

			googleURL = 'https://accounts.google.com/o/oauth2/v2/auth'
			googleURL += '?response_type=code'
			googleURL += '&client_id=' + myClientId
			googleURL += '&redirect_uri=' + myClientURL + '/OAuth'
			googleURL += '&scope=email'
			googleURL += '&state=' + myState

			self.redirect(googleURL, 302)

# [START app]
app = webapp2.WSGIApplication([

    ('/', MainPage),
    ('/googleRedirect', googleRedirect),
    ('/OAuth', googleRedirect)

], config=config, debug=True)
# [END app]