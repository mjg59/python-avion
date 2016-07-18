Python control for Avion bluetooth dimmers
==========================================

A simple Python API for controlling [Avi-on](http://www.avi-on.com/) Bluetooth dimmers. This code makes use of the PyBT2 branch of Mike Ryan's [PyBT](http://github.com/mikeryan/PyBT) and depends on [csrmesh](https://github.com/nkaminski/csrmesh/).

Example use
-----------

This will connect and set the dimmer output to 50%. The second argument to the constructor is the network key which can be obtained by running:

```
curl -X POST -H "Content-Type: application/json" -d '{"email": "fakename@example.com", "password": "password"}' https://admin.avi-on.com/api/sessions | jq
```

replacing the email and password fields with your Avion credentials. The "passphrase" field is the network key.

```
import avion

dimmer = avion.avion("00:21:4d:00:00:01", "O5bb9/ab8NvaDMnKYjpTGQ==")
dimmer.connect()
dimmer.set_brightness(0x80)
```
