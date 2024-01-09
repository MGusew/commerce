## Commerce
Commerce is an application for simulating a sales conversation with a robot acting in the role of a customer or salesperson. Commerce is published along with a slightly modified version of Sobotify. The user interface and grammar correction tool were adapted. The Sobotify version is derived from hhuebert (https://github.com/hhuebert/sobotify).

## Instructions for installation
Prerequisite: The latest sobotify version is installed
For more information see also the intructions for Sobotify (https://github.com/hhuebert/sobotify)
* download the commerce repository here: https://github.com/MGusew/commerce/archive/refs/heads/main.zip
* Unzip the commerce-main.zip file 
* find your current sobotify installation folder (usually named "sobotify", NOT ".sobotify")
* copy the contents of the commerce-main folder and replace the contents in your sobotify installation folder
* it is important that the name of your sobotify installation folder stays the same 
* copy the contents of the folder "projects" from commer-main and paste it to .sobotify\projects

Open a command line which you can find by searching for "anaconda prompt" in Windows Search.
Type the following into anaconda prompt:

    conda activate sobotify
    pip install wikipedia-api

## Instructions for use
There are several different ways to start the commerce app:
* click on start_app.bat and choose the commerce app. You can choose any project which shows up. A Project acts as a dummy for commerce app. Changes in the project have no effect.
* click on start_commmerce.bat
* go with anaconda prompt to sobotify\apps\commerce

        conda activate sobotify
        python commerce.py

Beware that commerce.xlsx is just a dummy and changes there do not affect the sales conversation. The scenario in Commerce app can be adapted in commerce.py. This can require some basic Python knowledge.