from google.appengine.ext import ndb
import webapp2
import json

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('OAuth2.0')

# [START app]
app = webapp2.WSGIApplication([

    ('/', MainPage)

], debug=True)
# [END app]