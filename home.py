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
	'secret_key': 'Im_an_alien',
}

myClientId = '208594160583-shpbueepu59cb3fjslli3bp91il9q6h0.apps.googleusercontent.com'
myClientSecret = 'RXWI-WbIkD3x9SDrESewjj8D'
myClientURL = 'http://localhost:8080'

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
		token = ''
		if(token):
			self.response.write('Display Info')

		elif(self.request.get('state')):
			if(self.session.get('state') == self.request.get('state')):
				googleURL = 'https://www.googleapis.com/oauth2/v4/token'
				payload = urllib.urlencode({
					'code':self.request.get('code'),
					'client_id': myClientId,
					'client_secret': myClientSecret,
					'redirect_uri': myClientURL,
					'grant_type': 'authorization_code'
				})

				result = urlfetch.fetch(googleURL, method=urlfetch.POST, payload=payload)

				self.response.write(result.content)
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
    ('/OAuth', googleRedirect)

], config=config, debug=True)
# [END app]
