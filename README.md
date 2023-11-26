## Commerce
Commerce is an application for simulating a sales conversation with a robot acting in the role of a customer or salesperson. Commerce is published along with a slightly modified version of Sobotify. The user interface and grammar correction tool were adapted. The Sobotify version is derived from hhuebert (https://github.com/hhuebert/sobotify).

## Instructions for installation
Prerequisite: The latest sobotify version is installed  
For more information see also the intructions for Sobotify (https://github.com/hhuebert/sobotify)
* download the commerce repository
* replace your current sobotify installation folder with commerce
* you might have to rename commerce->your_previous_folder_name

Type the following into anaconda prompt:

    conda activate sobotify
    pip install wikipedia-api
    
In .sobotify folder (where all the user files are) add these folders:
* .sobotify\projects\commerce
* .sobotify\projects\commerce\trash
* .sobotify\projects\quiz
* .sobotify\projects\quiz\trash

Do:
* add to all other applications the same folder structure
* copy commerce.xlsx (located in sobotify_extended\sobotify\apps\commerce) into folder .sobotify\projects\commerce
* copy your xlsx files into the corresponding folders

## Instructions for use
There are several different ways to start the Commerce:
* click on start_app.bat and choose the commerce application. You can choose any project which shows up. Projects act as a dummy and do not affect Commerce yet
* click on start_commmerce.bat
* go with anaconda prompt to sobotify\apps\commerce

        conda activate sobotify
        python commerce.py

Beware that commerce.xlsx is just a dummy and changes there do not affect the sales conversation

## Manual changes since Jun 23 2023
.sobotify folder order change:
* .sobotify\projects\quiz (contains data for quiz app)
* .sobotify\projects\commerce (contains data for commerce app)

Changed sobotify files:
* sobotify_app_gui.py
* grammar_checking.py

in sobotify env:     

    pip install wikipedia-api