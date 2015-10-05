This is a simple example of a blog application using Flask / MongoDB with easy deployment in Openshift.
How do I get set up?

Prereq: Create an Openshift account and install rhc tools

Then run: rhc app create myflaskapp python-2.7 --from-code https://fsauch@bitbucket.org/fsauch/simpleblogengine.git

rhc cartridge-add mongodb-2.4 --app myflaskapp

Voila! The application should be running on Openshift