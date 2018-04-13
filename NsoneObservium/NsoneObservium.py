#
# (c) 2018, Brian Cavanagh <bcavanagh@ns1.com>
#

# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License v3
# If not, see <http://www.gnu.org/licenses/>.

import requests

class NsoneObservium:
    """A class for wrapping the Observium API."""

    def __init__(self, observium_base_url, observium_user, observium_pass, additional_endpoints=[], ssl_verify=True, timeout=10, observium_api_version=0):

        if(not ssl_verify):
            requests.packages.urllib3.disable_warnings()
        
        self._observium_api_base_url = '%s/api/v%s' % (observium_base_url, observium_api_version)
        
        (
            self._observium_user,
            self._observium_pass,
            self._observium_api_version,
            self._ssl_verify,
            self._timeout
        ) = (observium_user, observium_pass, observium_api_version, ssl_verify, timeout)
        
        
        self._api_endpoints = [
            {'name': 'devices', 'singular_form': 'device', 'actions': ['get', 'create', 'delete']},
            {'name': 'alerts', 'singular_form': 'alert', 'actions': ['get', 'update']},
            {'name': 'alert_checks', 'singular_form': 'alert_check', 'actions': ['get']},
            {'name': 'ports', 'singular_form': 'port', 'actions': ['get']},
            {'name': 'sensors', 'singular_form': 'sensor',  'actions': ['get']},
            {'name': 'status', 'singular_form': 'status', 'actions': ['get']}
        ]
        
        # This should let us extend the class on-the-fly if needed.  Not sure if needed, but cheap to have for now.
        if(additional_endpoints):
            self._api_endpoints.extend(additional_endpoints)
        
        self._nsone_observium_generate_methods()

    def _nsone_observium_generate_methods(self):
        maps = {
            'action_map' : {
                'get'   : 'get',
                'create': 'post',
                'update': 'put',
                'delete': 'delete'
            },        
            'params_map' : {
                'get'   : 'params',
                'create': 'json',
                'update': 'json',
                'delete': 'json'
            }
        }
         
        for endpoint in self._api_endpoints:
            for action in endpoint['actions']:
                setattr(NsoneObservium, "%s_%s" % (action, endpoint['name']), _nsone_observium_make_method(endpoint, action, maps))

def _nsone_observium_make_method(endpoint, action, maps):

    def _method(self, param_dict={}):
        results = {}
        errors = []
    
        try:
            id_key = "%s_id" % endpoint['singular_form']
            id = ''
            
            # not using .get() because we need to delete the key/value pair if it exists anyway. (We'll put it back later.)
            if(id_key in param_dict):
                id = param_dict[id_key]
                del param_dict[id_key]  #  The *_id might not have been passed in, but we should delete it if it was so that we avoid unintended query behaviour

            request_method = getattr(requests, maps['action_map'][action])  # This and the next line could be condensed, but this is way more readable.

            response = request_method('%s/%s/%s' % (self._observium_api_base_url, endpoint['name'], id), **{
                'auth': (self._observium_user, self._observium_pass),
                maps['params_map'][action]: param_dict,
                'timeout': self._timeout,
                'verify': self._ssl_verify
            })
           
            # Restore what we deleted a moment ago because the caller probably didn't expect us to play with actual dict passed in as the method parameters.
            # This set after the previous delete should still be cheaper than doing something like a copy or deep copy at the start of the method.
            if(id):
                param_dict[id_key] = id

            if(response.ok): #  Checking just ok here might not be enough.  We might need to specifically check for status_code == 200
                results = response.json()
                
                # Trying to make the resulting dict for single-item and multi-item search results uniform.
                # (A) If you search by a query term, you get something like "devices" with each id being a sub-key to the device(s).
                # (B) If you search with a specific ID, you get something like "device" with the details of the device in it.
                # The block below is trying to give the option of always finding results that look like (A) above.
                # It's just a tiny bit of memory to hold the extra reference to the same object, so very cheap in the grand scheme of this module.
                if(endpoint['singular_form'] in results):
                    results[endpoint['name']] = {
                        results[endpoint['singular_form']][id_key] : results[endpoint['singular_form']]
                    }
                    results['count'] = results.get('count', 1) 
            else:
                # If there is no response.text, then this was probably an error before observium, such as a connection error or a true 404.
                if(not response.text):
                    response.raise_for_status()
                # Otherwise, we want to return the response that observium gave.
                else:
                    # The observium API responds with an http 404 error if you search for a device ID that doesn't exist.
                    # My opinion is that a search for something that doesn't exist should simply return no results.
                    # We don't want things like ansible to fail because it searched for a device that doesn't exist.
                    # If we made it here, it likely means that we reached observium but that the query found nothing.
                    
                    errors.append("Observium error response: %s" % response.text)
        except BaseException as e:
            errors.append(e)
        return(results, errors)
    return(_method)
