# flickr-dump

Download your original size photos from Flickr.

This app is free and very simple to use.

## Let me let you know how to use this

**WARNING**: Most Linux/OS X users probably have python 2.7 installed, whereas this app requires python 3.4 or higher to run.

**Prerequisite**: Please get your [Flickr API Key here](https://www.flickr.com/services/apps/create/).

1. clone this repo on your local workstation.

` $ git clone https://github.com/beaufour/flickr-download.git`

2. install requirements.

` $ pip install -r requirements.txt`

3. evaluate script.

```
 $ ./flickr-dump
usage: flickr-dump [-h] -A API_KEY -S API_SECRET -U USER_ID [-P PATH]

Flickr Dump

optional arguments:
  -h, --help            show this help message and exit
  -A API_KEY, --api-key API_KEY
                        An API-key for accessing the Flickr API.
  -S API_SECRET, --api-secret API_SECRET
                        An API-secret for accessing the Flickr API.
  -U USER_ID, --user-id USER_ID
                        Your Flickr UserID, Can be found at
                        http://idgettr.com/
  -P PATH, --path PATH  The target path to download photos
```

## License

Flickr-dump is licensed under the GNU General Public License (GPL) version 2.0, which provides legal permission to copy, charge, distribute and/or modify the software.

Please check the LICENSE file for more details.

