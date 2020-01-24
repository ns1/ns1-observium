# NS1 Observium API Python Library
> This project is [inactive](https://github.com/ns1/community/blob/master/project_status/INACTIVE.md).

A python library for interacting with the Observium API: http://docs.observium.org/api/

# Installing

```
$ pip install NsoneObservium
```

Examples
========
[see more]http://docs.observium.org/api/#get-endpoints
```
from NsoneObservium.NsoneObservium import NsoneObservium

observium = NsoneObservium('https://observium01.example.com', 'myuser', 'mypassword', ssl_verify=False)
observium.get_devices({'hostname': "mpr.myrouter"})

observium.get_devices()
observium.get_devices({'device_id': "34"})

observium.get_alerts()
observium.get_alerts({'alert_id': "234"})


```

Contributing
============
Pull Requests and issues are welcome. See the [NS1 Contribution Guidelines](https://github.com/ns1/community) for more information.

# LICENSE

GNU GPL v3 - see the included LICENSE file for more information


