# NS1 Observium API Python Library

A python library for interacting with the Observium API: http://docs.observium.org/api/

# Installing

```
$ pip install NsoneObservium
```

Examples
========
[see more]http://docs.observium.org/api/#get-endpoints
```
from NsoneObservium import NsoneObservium

observium = NsoneObservium.NsoneObservium('https://observium01.example.com', 'myuser', 'mypassword', ssl_verify=False)
observium.get_devices({'hostname': "mpr.myrouter"})

observium.get_devices()
observium.get_devices({'device_id': "34"})

observium.get_alerts()
observium.get_alerts({'alert_id': "234"})


```

Contributing
============

Contributions, ideas and criticisms are all welcome.

# LICENSE

GNU GPL v3 - see the included LICENSE file for more information


