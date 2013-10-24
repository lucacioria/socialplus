socialplus
==========

Social Plus - Google+ for Enterprise

Install on Ubuntu
------

sudo add-apt-repository ppa:chris-lea/node.js
sudo apt-get install nodejs

sudo npm install -g coffee-script

sudo npm install -g jade

sudo apt-get install ruby1.9.1
sudo gem install sass

Deploy
------

1. you need to compile the GUI files, all .jade .coffee and .scss files in the /public directory. Simply output the compiled version in the same directory as the source file. Compiled versions are already gitignored

2. run the appengine server, from the DJANGO_GAE directory:
    
    dev_appserver.py --port=8080 ./

3. open the GUI at the address:

    http://localhost:8080/public/html/main.html

4. in the sync tab, click "reset domain" and then run the first four tasks one after the other, in the order they're displayed.

To create and view reports, specify a query in the activities->advanced tab, then create a report with a new name. To update the report, go to the sync tab and use the relevant task. Only after having updated it you can view it from the reports tab.

### Api Access ###

The api access information are in the api.py file, currently there are the two test domains (appseveryday.com and managemybudget.net). Chose which one two use commenting out the relevant lines.