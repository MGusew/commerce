from signal import signal, SIGINT
from sys import exit
import time
import argparse
from sobotify import sobotify
import ast
from random import seed
from random import choice
import wikipediaapi
# from deepmultilingualpunctuation import PunctuationModel

##################data which can be later in Excel#################################
# Portfolio (order has to fit-> TopicArray-TraitsArray)
TopicArray = ["clothes","colour","material","size top","size bottom wide","size bottom length","size footwear"] # order relevant for determine_block()
TopicGerman=["kleidung","farbe","material","größe","weite","länge","schuhgröße"]
TraitsArray = [["hose", "jacke", "bluse"],["rot","gelb","blau"],["kaschmir","baumwolle","leinen"],["XS","S","M","L","XL"],[26,50],[30,40],[19,50]]
Topics_include_matrix = [[1,1,1,0,1,1,0],[1,1,1,1,0,0,0],[1,1,1,1,0,0,0]] # for each cloth it says which topics need to be set to choose the cloth
Offset_size = 3 # size is always last, tells from where to look for size in TopicArray
Pricetable=[[120,200,100],[60,80,40],[50,60,30]] # one list for every material
# for Wikipedia Info
Wikipath = [[[], []],[[],[],[]],[["Kaschmirwolle","Eigenschaften"],["Baumwolle","Baumwollfaser","Eigenschaften der Faser"],["Flachsfaser","Eigenschaften","Textilfaser"]]]
Filterkeywords_include = ["natur","widerstandsfähig","langlebig","positiv","hautfreundlich","edel","wertvoll","qualität"]

# only for second roleplay
# pay attention that goal makes sense (not "shoe and size=S M XL" ...)
# goal has to be in order of TraitsArray
# ["","",...] for no goal, or "" for no set trait
Goal = ["","","","M","","",""]

# Consultation
Consult_material_keywords=[[["natur","hautfreundlich","weich","wärme","warm","leicht"],["grün","kleiderschrank","siegel","ökologisch","sozial"],["nein","schritt","färben","nähen"]],[["natur","hautfreundlich","pflegeleicht","widerstandsfähig","saugfähig"],["grün","kleiderschrank","siegel","ökologisch","sozial"],["nein","schritt","färben","nähen"]],[["natur","hautfreundlich","pflegeleicht","atmungsaktiv","kühl"],["grün","kleiderschrank","siegel","ökologisch","sozial"],["nein","schritt","färben","nähen"]]]
Consult_material_questions=[["Welche Vorteile bietet mir Kaschmir?","Ich lege wert darauf, dass die Kleidung nachhaltig ist. Wie sieht das bei euch aus?","Ist der Gewinn von Kaschmir selbst ökologisch? Garantiert das Siegel auch gute Haltungsbedingungen?"],["Welche Vorteile habe ich von Baumwolle?","Ich lege wert darauf, dass Kleidung aus Baumwolle nachhaltig ist. Wie sieht das bei euch aus?","Ist auch der Anbau selbst ökologisch? Werden keine chemischen Pestizide verwendet?"],["Welche Vorteile bietet mir denn Kleidung aus Leinen?","Ich lege wert darauf, dass Kleidung aus Leinen nachhaltig ist. Wie sieht das bei euch aus?","Ist auch der Anbau von Leinen ökologisch? Werden keine chemischen Pestizide verwendet?"]]
####################################################################################

emotion_detection=True
grammar_correction=False # enables better language for speech
guided_listening=False
class commerce:

    def __init__(self,robot_name,robot_ip,language,sound_device,mosquitto_ip,project_file):
        # for keywords in text_scenario : no material as name here,  no endings in keys with _angry _disgust ...
        self.text_scenario={
            # general scenario #
            "clothes_name":"Kleidung",
            "generalIntro":"Hallo, schön dass du da bist. Wir wollen heute für ein Verkaufsgespräch im Einzelhandel üben. Dazu machen wir zusammen ein Rollenspiel.",
            "makeChoice":"Möchtest du zuerst der Kunde sein und ich bin der Assistent? Wir werden die Rollen danach tauschen",
            "mentionGlad":"Super, ich freue mich",
            "doneScenario":"Super, wir sind dann soweit fertig. Danke für die Teilnahme an der Übung und bis zum nächsten Mal.",
            "noAnswer":"Leider konnte ich dich nicht hören. Kannst du es bitte noch einmal wiederholen? ",
            "problemTerminate":"Leider scheint hier ein ernsthaftes Problem vorzuliegen. Ich beende.",
            "okay":["Alles klar","Okay","In Ordnung"],
            "size":"Größe",
            "yes":["ja", "okay", "in ordnung", "klingt gut"],
            "no":["nein","gar nichts", "nichts"],
            # first roleplay #
            "introduction_first_roleplay":"Du bist der Kunde und ich bin der Assistent. Lass uns anfangen. Du kommst in das Geschäft herein.",
            "welcomeQuestion":"Hallo, willkommen im Sobotik Modegeschäft. Wie kann ich dir weiterhelfen?",
            "currentlyOffer_part1":"Wir können dir derzeit",
            "currentlyOffer_part2":"anbieten.",
            "askForYou":"Wäre da vielleicht etwas für dich dabei? Wenn ja, was?",
            "goodChoice":["Das ist eine gute Wahl","Wundervoll","Hervorragend","Super","Das ist eine super Wahl"],
            "emphasizeChoice":"Leider haben wir nur die eben erwähnte Auswahl.",
            "goodOpportunity":"Dies ist eine super Gelegenheit.",
            "whatTryOn":". Was möchtest du gerne anprobieren?",
            "sadNothingThere":"Es ist sehr schade, dass nichts für dich infrage kommt.",
            "offer_part1":"Darf ich dir eine ",
            "offer_part2":" anbieten?",
            "maybeTryOn":"Vielleicht überzeugt es dich, wenn du es einfach mal anprobierst",
            "motivate2try":"Komm schon, ich bin sicher es wird toll aussehen. Lass es uns probieren.",
            "thereIs_part1":"Die ",
            "thereIs_part2":" gibt es in",
            "askColourLikemost":"Welche Farbe davon magst du am liebsten?",
            "colourFits_part1":"Ich denke die Farbe ",
            "colourFits_part2":"steht dir ganz gut. Möchtest du es mal damit probieren?",
            "likeNoColour":"Es ist schade, dass dir die Farbe nicht gefällt. Mehr Farben als die erwähnten haben wir leider nicht mehr verfügbar.",
            "tryOtherMaybe":"Vielleicht überlegst du es dir anders? Nenne mir gerne die Farbe, wenn dem so ist.",
            "canNotDoAnything":"Nagut, da kann ich wohl leider nichts machen.",
            "letJustTry":"Lass es uns einfach mal probieren.",
            "goodChoice_end_part":"ist eine gute Wahl.",
            "materialOffer_part1":"Darf ich dir die ",
            "materialOffer_part2":" aus ",
            "materialOffer_part3":" anbieten?",
            "foundWikiInfo":"Ich habe folgende Informationen auf Wikipedia gefunden:",
            "offer2_part1":"Wäre ",
            "offer2_part2":" etwas für dich?",
            "weHave":"Wir haben noch",
            "askIfMoreWiki":"Möchtest du dass ich dir zu einem weiteren Material Informationen aus Wikipedia raussuche? Wenn ja. Zu welchem?",
            "soWhatMaterial":"Welches Material würdest du also bevorzugen?",
            "offer3_part1":" lass es uns mal mit ",
            "offer3_part2":" probieren.",
            "changeSize_part1":"Du könntest eine ",
            "changeSize_part2":" kleiner oder größer ausprobieren.  Welche ",
            "changeSize_part3":" möchtest du stattdessen anprobieren?",
            "askwhatneeded_part1":"Welche ",
            "askwhatneeded_part2":" brauchst du denn?",
            "changeSize2_part1":"Du könntest eine größere oder kleinere ",
            "changeSize2_part2":" oder ",
            "changeSize2_part3":" ausprobieren. Welche ",
            "changeSize2_part4":" und ",
            "changeSize2_part5":" möchtest du stattdessen anprobieren?",
            "askwhatneeded2_part1":"Welche ",
            "askwhatneeded2_part2":" und ",
            "askwhatneeded2_part3":" brauchst du denn?",
            "bringCloth":"Einen Moment, ich bringe dir die ",
            "tryItOn":"Bittesehr, probiere es in Ruhe an.",
            "askSizeFit":"Und? Passt denn die Größe?",
            "bringClothAgain_part1":"Einen Moment, ich bringe dir die ",
            "bringClothAgain_part2":" in anderer Größe nochmal.",
            "askFitBetter":"Passt es diesmal besser?",
            "nothingFits":"Schade, dann passt dir wohl keins der Größen.",
            "robotHappy":"Super, das freut mich.",
            "tellPrice":"Das wäre dann ",
            "currency":"Euro",
            "tellPriceReduction_part1":"Du hast außerdem einen Rabatt von ",
            "tellPriceReduction_part2":" Damit macht es nur noch ",
            "askPayment":"Wie möchtest du bezahlen?",
            "paymentCompleted":"Okay, die Zahlung ist abgeschlossen",
            "farewell_first_roleplay_positive1":"Danke für deinen Einkauf.",
            "farewell_first_roleplay_positive2":"Ich wünsche dir noch einen schönen Tag.",
            "inviteToNextTime":"Nächste Woche bekommen wir die nächste Kollektion. Schaue gerne das nächste Mal vorbei. Wir finden dann bestimmt etwas passendes.",
            "farewell_first_roleplay_negative":"Es ist toll, dass du da warst. Ich bin sicher, wir finden für dich das nächste Mal etwas passendes. Ich wünsche dir trotzdem noch einen schönen Tag.",
            "firstRoleplayDone":". Das Rollenspiel mit dir als Kunden haben wir jetzt abgeschlossen.",
            "foundSpecificWiki_part1":"Zu ",
            "foundSpecificWiki_part2":" habe ich folgende Informationen auf Wikipedia gefunden: ",
            "askIfMoreWiki2":"Möchtest du noch zu einem weiteren Material Informationen haben? Wenn ja, welchem?",
            "normalOffer_part1":"Heute hast du Glück, wir haben eine Aktion. Du bekommst einen Rabatt von ",
            "normalOffer_part2":" auf ",
            "normalOffer_part3":"n.",
            "firstTimeCustomerPrice":"Da du das erste mal bei uns bist, ist es für mich besonders wichtig, dass du nicht wieder enttäuscht gehst. Ich biete dir daher auf deinen heutigen Kauf eines Artikels einen Rabatt von ",
            "repeatedOfferPrice":"Mir ist deine Zufriedenheit wichtig. Ich biete dir daher außnahmsweise einen weiteren Rabatt von ",
            # second roleplay #
            "introduction_second_roleplay1":"Diesmal bist du der Assistent und ich bin der Kunde. Lege dir das Portfolio zurecht.",
            "introduction_second_roleplay2":"Ich betrete jetzt dein Geschäft. Du beginnst.",
            "answer_greeting":["Hallo","Guten Tag"],
            "answer_welcome":["willkommen"],
            "answer_brand":["modegeschäft","geschäft"],
            "answer_help":["weiterhelfen","helfen"],
            "hint_greeting":"Verwende eine passende Grußformel um den Kunden angzusprechen.",
            "hint_welcome":"Es ist wichtig, den Kunden bei der Begrüßung willkommen zu heißen.",
            "hint_brand":"Du solltest den Namen des Geschäfts erwähnen, damit der Kunde es nach dem Einkauf besser im Kopf behalten kann.",
            "hint_help":"Vergiss nicht den Kunden zu fragen, wie du weiterhelfen kannst. Damit senkst du die Hemmschwelle, die entsteht, wenn der Kunde selber um Hilfe bitten muss.",
            "repeatWelcome":"Das kannst du besser machen. Lass es uns noch einmal versuchen. Ich komme in dein Geschäft.",
            "notPerfectMoveOn":"Das war noch nicht perfekt, aber fahren wir fort.",
            "spontaneousArrival":"Guten Tag. Mein Freund Nao hat mir gesagt, hier gebe es tolle Sachen zu kaufen. Also bin ich einfach so mal hier hergekommen.",
            "hint_topicOrder":"Bei der Kundenberatung geht man vom allgemeinen zum feinen vor und nährt sich so schrittweise dem Kundenwunsch. Zuerst wäre es also sinnvoll auf das Sortiment einzugehen, was sich in die Kleidungsstücke unterteilt. In unserem Szenario gibt es eine handvoll Kleidungsstücke, du kannst sie also alle erwähnen.",
            "hint_forgot2Mention_part1":"Du hast unter Umständen vergessen",
            "hint_forgot2Mention_part2":"zu erwähnen.",
            "repeat_request":"Lass es uns noch einmal versuchen.",
            "wantHave_part1":"Ich würde gerne eine ",
            "wantHave_part2":" haben.",
            "wantHaveInstead_part1":"Ich würde dann lieber eine ",
            "wantHaveInstead_part2":" wählen.",
            "whatcolours":"Welche Farben habt ihr denn verfügbar?",
            "thinkGoodColour_part1":"Ich denke, dass mir ",
            "thinkGoodColour_part2":" ganz gut steht. Mir gefällt die Farbe",
            "wantThat_part1":"Wow, ",
            "wantThat_part2":" passt perfekt. Ich möchte die ",
            "wantThat_part3":" in",
            "wantThat_part4":" haben.",
            "noColour_part1":"Oh. ",
            "noColour_part2":" ist meine Lieblingsfarbe. Habt ihr die Farbe garnicht?",
            "IChoose":"Ah, wunderbar. Dann wähle ich ",
            "notThereTryInstead_part1":"Oh, schade. Ja gut, dann würde ich es gerne mit ",
            "notThereTryInstead_part2":" probieren.",
            "whatMaterial_part1":"Aus welchem Material könnt ihr denn die ",
            "whatMaterial_part2":" anbieten?",
            "insteadMaterial_part1":"Habt ihr denn das Kleidungsstück auch aus ",
            "insteadMaterial_part2":" verfügbar?",
            "hint_assortment_part1":"Huch, du musst dich wohl geirrt haben. ",
            "hint_assortment_part2":" befindet sich ja in eurem Sortiment.",
            "iThink":"Ich bin gerade am überlegen.",
            "wantChoose-part1":" ich würde gerne dann ",
            "wantChoose-part2":" auswählen",
            "hint_proceedNoMaterial":"Leider habe ich kein einziges Material heraushören können. Ich nehme mal an, dass ich die Auswahl gehört habe.",
            "ineed":"Ich bräuchte die ",
            "hint_tryOn":"Wenn du feststellst, dass alle notwendigen Aspekte für das Kleidungsstück geklärt sind, solltest du das Kleidungsstück bringen, damit der Kunde dies anprobieren und anschauen kann. Dazu bittest du um einen Moment.",
            "instructionProceed":"Nehmen wir an, ich habe es anprobiert und begutachtet. Du kommst nach einer Weile wieder auf mich zu.",
            "hint_youLikeIt_part1":"Jetzt muss man nachfragen, ob dem Kunden das Kleidungsstück gefallen hat oder nicht.",
            "hint_youLikeIt_part2":" Du kommst auf den Kunden zu.",
            "want2buy_part1":"Ja, die ",
            "want2buy_part2":" finde ich super. Ich möchte die ",
            "want2buy_part3":" gerne kaufen.",
            "hint_payment_part1":"An diesem Punkt könntest du dem Kunden den Preis nennen und zur Bezahlung übergehen. ",
            "hint_payment_part2":"Ich möchte das Kleidungsstück kaufen.",
            "hint_paymentMethod":"Heutzutage gibt es unterschiedliche Wege zu bezahlen. Du solltest den Kunden fragen, welche Bezahlform gewünscht ist, damit du dich darauf einstellen kannst.",
            "want2pay":"Ich möchte gerne in Bar bezahlen.",
            "paymentCompleted2":" die Zahlung ist nun abgeschlossen.",
            "hint_sayBye":"Vergiss nicht, dich mit einer ansprechenden Schlussformel zu verabschieden.",
            "hint_positiveWords":"Du könntest dem Kunden etwas positives auf dem Weg geben. Zum Beispiel einen schönen Tag wünschen oder etwas wie ich freue mich dich das nächste mal wiederzusehen.",
            "hint_sayThank":"Es ist wichtig, dich für den Einkauf zu bedanken.",
            "sayBye":"Danke wünsche ich ebenfalls, Auf wiedersehen.",
            "farewell_second_roleplay":" das war es dann mit dem Rollenspiel mit dir als Assistenten.",
            "hint_consult_part1":"Du hättest beispielsweise auf die Begriffe",
            "hint_consult_part2":"eingehen können. Lass uns fortfahren.",
            "understand":["Ich verstehe. ","Ja, in Ordnung. ","Alles klar. ","Okay. ","aha, ja. "],
            "askPreciseAnswer":["Könntest du mir noch mehr dazu erzählen?","Das überzeugt mich noch nicht so ganz. Was kannst du mir dazu noch sagen?","Ich würde gerne noch mehr dazu wissen"],
            "whatYouRecommend_part1":"Welche ",
            "whatYouRecommend_part2":" könntest du mir denn empfehlen?",
            "canNotDecide":"Ich kann mich nicht entscheiden. ",
            "hint_OfferRight":"Bist du sicher, dass du mir das richtige angeboten hast?",
            "proceedConsult_part1":"Leider konntest du mir keine richtige Empfehlung der Eigenschaft ",
            "proceedConsult_part2":" geben. Wir fahren fort.",
            "hint_friendlyFail":"Du könntest etwas freundlicher wirken. Bei der Kundenberatung ist ein freundlicher Gesichtsausdruck wichtig. Das gehört zu der Erfahrung dazu, die der Kunde nach dem Einkauf aus dem Geschäft mitnimmt. Fahren wir fort",
            "evaluateFriendlySucces":"Das hast du super gemacht. Du hast die meiste Zeit freundlichen Gesichtsausdruck gehabt, während ich der Kunde war.",
            "evaluateFriendlyFail":"Das hast du super gemacht. Aber du könntest dem Kunden mit etwas freundlicherem Gesichtsausdruck begegnen.",
            "askEmotionData":"Möchtest du eine genaue Auflistung meiner Erkennung zu deinem Gesichtsausdruck haben?",
            "emotionAdditionalInfo":"Die Ergebnisse beziehen sich nur auf das zweite Rollenspiel mit dir als Assistenten. Als freundlich zählen die Emotionen neutral und glücklich.",
            "tellemotion":" Prozent war dein Gesichtsausdruck ",
            "angry":"wütend",
            "disgust":"ekelnd",
            "fear":"ängstlich",
            "happy":"glücklich",
            "sad":"traurig",
            "surprise":"überrascht",
            "neutral":"neutral",
        }
        # emotions=["angry","disgust","fear","happy","sad","surprised","neutral"]
        # reactions are ordered in that way, "" for no reaction
        self.emotion_scenario={
            # general scenario #
            "afraid_begin":["Ich bin mir sicher, von unser gegenseitigen Interaktion können wir beide profitieren","Ich habe heute erst meine Systeme von Staub befreit. Ist irgendetwas dreckig? Naja, gut.","Keine Sorge, es ist nur eine Übung. Wenn nicht alles glatt geht, ist es auch in Ordnung.","Mit guter Laune die Übung anzugehen ist eine tolle Einstellung.","Ich hoffe bei mir ist heute keine Schraube locker","Keine Sorge, wenn du nicht vorbereitet bist sag zuerst einfach, dass du zufällig in meinen Laden gekommen bist. Ich werde dir dann weiterhelfen.",""],
            # first roleplay #
            "first-time_customer_price_reduction":["Dieser Rabatt ist einmalig. Mehr können wir dir leider nicht bieten.","Es ist ja nur zu deinem Gunsten.","","Deine Zufriedenheit liegt uns sehr am Herzen.","Du kannst ja trotzdem deine Meinung ändern, falls es beim Anprobieren doch nicht passen sollte.","Deine Zufriedenheit liegt uns sehr am Herzen.",""],
            "Choice_by_robot":["Sei mir nicht böse. Es kann auch sein, dass ich dich nicht optimal verstanden habe.","","Ich bin zuversichtlich, dass es dir gefallen wird.","","Ich bin zuversichtlich, dass es dir gefallen wird.","",""],
            "colour_no":["Es tut mir leid, wenn ich deinen Geschmack nicht getroffen habe.","Es tut mir leid, wenn ich deinen Geschmack nicht getroffen habe.","","","","",""],
            "colour_lets_try":["Ich bin mir sicher, du wirst die Farbe nicht bereuen.","Manchmal muss man etwas ungewohntes probieren, um Neues für sich zu entdecken","Keine Sorge, die Farbe wird bestimmt super aussehen.","","Vertrau mir, die Farbe wird bestimmt super aussehen.","",""],
            "try_on_observe":["Du scheinst nicht sehr begeistert zu sein.","Du scheinst nicht sehr begeistert zu sein.","Ich finde es steht dir hervorragend.","Es sieht perfekt aus!","Du siehst nicht zufrieden aus.","Toll oder? Man kann sich immer wieder neu erfinden. Kleider machen Leute.","Ich finde es sieht gut aus."],
            "try_on_observe2":["","","Du scheinst etwas verunsichert zu sein. Wir können nochmal eine andere Größe probieren.","Wow, eine andere Größe kann einen großen Unterschied machen, oder?","","Ich finde es sieht viel besser aus.",""],
            "after_payment":["Wir haben immer wieder neue tolle Looks im Sortiment. Das nächste Mal wenn du da bist findest du bestimmt noch viel bessere Sachen.","Wir haben immer wieder neue tolle Looks im Sortiment. Das nächste Mal wenn du da bist findest du bestimmt noch viel bessere Sachen.","Wir haben immer wieder neue tolle Looks im Sortiment. Das nächste Mal wenn du da bist findest du bestimmt noch viel bessere Sachen.","Es freut mich dich als glücklichen Kunden im Sobotik Modegeschäft bedient zu haben und bis zum nächsten Mal.","Wir haben immer wieder neue tolle Looks im Sortiment. Das nächste Mal wenn du da bist findest du bestimmt noch viel bessere Sachen.","Ich freue mich dich das nächste Mal im Sobotik Modegeschäft begrüßen zu dürfen.","Ich freue mich dich das nächste Mal im Sobotik Modegeschäft begrüßen zu dürfen."],
            "end_consult_material":["Es ist für mich leider aktuell nicht möglich, genauere Informationen zu geben oder auf konkrete Aspekte einzugehen.","","","","Es ist für mich leider aktuell nicht möglich, detailliertere Informationen zu geben oder auf konkrete Aspekte einzugehen.","",""],
            # second roleplay #
            "start_second_roleplay":["Wir haben die Hälfte bereits hinter uns.","","Keine Sorge, falls du nicht weiter weißt, werde ich dir weiterhelfen. Es ist nur eine Übung.","Dir scheint unsere Übung Spaß zu machen. Das freut mich.","Komm schon, ich bin sicher du kannst ein toller Assistent sein.","Dir scheint unsere Übung Spaß zu machen. Das freut mich.",""]
        }

        print ("init commerce training ...")
        self.language=language
        self.sobot=sobotify.sobotify(app_name="commerce-training",debug=True,log=False)
        self.sobot.start_robotcontroller(robot_name=robot_name,robot_ip=robot_ip, language=self.language)
        self.sobot.start_listener(language=self.language,sound_device=sound_device)
        if grammar_correction==True:
            self.sobot.start_grammar_checking(language=self.language)
        if emotion_detection==True:
            self.sobot.start_emotion_detection(robot_name=robot_name,robot_ip=robot_ip)
        self.sobot.log("Starting Commerce app","app_info")

        self.speech_tempo=90 # for robot speech
        self.lastSpokenPhrase=""

        # self.knowledge stores current situation of the product choice
        # to conclude a roleplay each topic has a trait to appear exactly once
        # the array has to be ordered same as TopicArray
        self.knowledge=[""]*len(TopicArray)
        self.price_discount = [0, "none"]
        self.price_offer_count = 0
        self.successful_sale = True
        self.tried_on = False
        self.payed = False
        self.noanswer_limit = 4

        # wikipedia
        self.wikiobject = wikipediaapi.Wikipedia('RobotProject (nao@pepper.com)', 'de')
        self.sentence_limit = 3

        # second roleplay
        self.suggestion = [[] for i in range(len(TopicArray))]
        self.after_request = False
        self.choice_complete = False
        self.roleplay_end = False
        self.try_on_count = 0

        # emotion recognition
        self.desired_friendly_limit = 60
        self.emotions=["angry","disgust","fear","happy","sad","surprised","neutral"]
        self.accumulate_emotion={
            "angry":0,
            "disgust":0,
            "fear":0,
            "happy":0,
            "sad":0,
            "surprise":0,
            "neutral":0,
            "none":0
        }

    def run(self):
        time.sleep(10) # waiting for FER to start
        moveOn=self.initialization()
        if moveOn:
            self.first_roleplay()
        self.second_roleplay()
        self.completion()

    def initialization(self):
        self.emotion_acc_reset()
        self.speak("generalIntro",motion="generalIntro")
        self.react_emotion("afraid_begin")
        self.speak("makeChoice",motion="makeChoice")
        answer=self.listen()
        moveOn=self.search_answer_or(self.text_scenario["yes"],answer)
        if moveOn:
            self.speak("mentionGlad",motion="mentionGlad")
        else:
            self.speak("okay")
        return moveOn

    def completion(self):
        self.speak("doneScenario")

    def listen(self,pause_emotion_detection=False):
        for x in range(self.noanswer_limit):
            if emotion_detection==True:
                answer,emotion=self.sobot.listen(detect_emotion=True)
            else:
                answer=self.sobot.listen()
            if guided_listening:
                additional=input("add text or enter: ")
                answer=answer+" "+additional
            if (len(answer)>1 and not guided_listening) or len(answer)>2:
                if emotion_detection==True and pause_emotion_detection==False:
                    self.emotion_acc(emotion)
                return answer
            else:
                if x<(self.noanswer_limit-1):
                    self.speak(self.text_scenario["noAnswer"]+self.lastSpokenPhrase,rawtext=True)
        self.speak("problemTerminate")
        self.terminate()

    # motion should be a gesture which is in .sobotify\data
    def speak(self,text,speech_tempo="default",motion="standard_gesture",pause_emotion_detection=False,rawtext=False):
        if rawtext==False:
            text=self.text_scenario[text]
        if str(type(text))=="<class 'list'>":
            text=self.random_sentence(text)
        if speech_tempo=="default":
            speech_tempo=self.speech_tempo
        self.lastSpokenPhrase=text
        if emotion_detection==True:
            emotion=self.sobot.speak(text,speed=speech_tempo,gesture=motion,detect_emotion=True)
            if pause_emotion_detection==False:
                self.emotion_acc(emotion)
        else:
            self.sobot.speak(text,speed=speech_tempo,gesture=motion)


    def terminate(self):
        self.sobot.terminate()

###########################first roleplay#########################

    def first_roleplay(self):
        self.introduction_first_roleplay()
        self.welcome_first_roleplay()
        goBlock=self.determine_block()
        while (goBlock!="no topics left") and (self.successful_sale==True):
            self.continueToBlock(goBlock)
            goBlock=self.determine_block()
        self.end_first_roleplay()

    def introduction_first_roleplay(self) :
        self.speak("introduction_first_roleplay",motion="introduction_first_roleplay")

    def welcome_first_roleplay(self) :
        self.speak("welcomeQuestion")
        answer=self.listen()
        self.store_traits(answer)
        if self.knowledge_empty()!=True:
            self.available()

    def determine_block(self):
        if self.successful_sale==False:
            if self.roleplay_end==True:
                return "no topics left"
            else:
                return "farewell"
        # searches for not chosen trait of topic in knowledge
        for i in range(Offset_size):
            if self.knowledge[i]=="":
                return TopicArray[i]
        if self.choice_complete==False:
            return "size"
        elif self.tried_on==False:
            return "try_on"
        elif self.payed==False:
            return "make_payment"
        elif self.roleplay_end==False:
            return "farewell"
        return "no topics left"

    def continueToBlock(self, goBlock) :
        if goBlock=="try_on" or goBlock=="make_payment" or goBlock=="size" or goBlock=="farewell":
            eval("self."+goBlock+"()")
        for topic in TopicArray :
            if topic is goBlock :
                eval("self."+topic+"()")
                return
        return

    def available(self):
        if self.knowledge[0]!="":
            sentence="Eine "
            if self.knowledge[1]!="":
                sentence+=self.knowledge[1]+"e "
            sentence+=self.knowledge[0]
            if self.knowledge[2]!="":
                sentence+="aus "+self.knowledge[2]+" "
            sentence+="haben wir im Sortiment."
        elif self.knowledge[1]!="":
            sentence=self.text_scenario["clothes_name"]+" in "+self.knowledge[1]+" "
            if self.knowledge[2]!="":
                sentence+="aus "+self.knowledge[2]+" "
            sentence+="haben wir im Sortiment"
        elif self.knowledge[2]!="":
            sentence=self.text_scenario["clothes_name"]+" aus "+self.knowledge[2]+" haben wir da."
        self.speak(self.correct_sentence(sentence),rawtext=True)

    def clothes(self) :
        if self.knowledge[0]=="":
            traits=self.assemble_traits(TraitsArray[0],"und")
            sentence=self.text_scenario["currentlyOffer_part1"]+traits+self.text_scenario["currentlyOffer_part2"]
            self.speak(sentence,rawtext=True,motion="currentlyOffer")
            self.speak("askForYou")
            answer=self.listen()
            self.store_traits(answer)
            if self.knowledge[0]!="":
                self.speak("goodChoice",motion="goodChoice")
                return
            elif self.knowledge[0]=="":
                self.speak("emphasizeChoice",motion="emphasizeChoice")
                self.emotion_acc_reset()
                self.price_reduction(item=TraitsArray[0][0],discount_type="Prozent",amount=50,situation="first time customer")
                self.speak("goodOpportunity")
                traits = self.assemble_traits(TraitsArray[0],"oder")
                self.react_emotion("first-time_customer_price_reduction")
                self.speak(traits+self.text_scenario["whatTryOn"],rawtext=True)
                answer=self.listen()
                self.store_traits(answer)
                if self.knowledge[0] == "" :
                    if self.search_answer_or(self.text_scenario["no"],answer):
                        self.speak("sadNothingThere")
                        self.successful_sale=False
                        return
                    else:
                         self.speak(self.correct_sentence(self.text_scenario["offer_part1"]+TraitsArray[0][0]+self.text_scenario["offer_part2"]),rawtext=True)
                         self.speak("maybeTryOn")
                         answer=self.listen()
                         if self.search_answer_or(self.text_scenario["no"],answer):
                             self.speak("sadNothingThere")
                             self.successful_sale=False
                             return
                         elif self.search_answer_or(self.text_scenario["yes"],answer):
                             self.speak("goodChoice")
                             self.knowledge[0]=TraitsArray[0][0]
                             return
                         else:
                             self.speak("motivate2try")
                             self.knowledge[0]=TraitsArray[0][0]
                             return

    def colour(self):
        if self.knowledge[1] == "":
            traits = self.assemble_traits(TraitsArray[1],"und")
            colour_choice = self.correct_sentence(self.text_scenario["thereIs_part1"]+self.knowledge[0]+self.text_scenario["thereIs_part2"]+traits)
            self.speak(colour_choice,rawtext=True,motion="thereIs")
            self.speak("askColourLikemost")
            answer=self.listen()
            self.store_traits(answer)
        if self.knowledge[1] == "":
            random_colour=self.random_sentence(TraitsArray[1])
            self.emotion_acc_reset()
            self.speak(self.text_scenario["colourFits_part1"]+random_colour+self.text_scenario["colourFits_part2"],rawtext=True)
            answer=self.listen()
            self.store_traits(answer)
            if self.search_answer_or(self.text_scenario["yes"],answer):
                self.knowledge[1]=random_colour
                self.speak("goodChoice")
            elif self.search_answer_or(self.text_scenario["no"],answer):
                self.react_emotion("colour_no")
                successful_sale=False
                self.speak("likeNoColour")
                if self.price_offer_count<1:
                    self.price_reduction(situation="first time customer")
                elif self.price_offer_count<2:
                    self.price_reduction(situation="repeated offer")
                time.sleep(1)
                self.speak("tryOtherMaybe")
                self.speak(colour_choice,rawtext=True)
                answer=self.listen()
                self.store_traits(answer)
                if self.knowledge[1]=="":
                    self.speak("canNotDoAnything",motion="canNotDoAnything")
                    self.successful_sale=False
                    return
            else:
                self.knowledge[1]=random_colour
                self.speak("letJustTry")
                self.react_emotion("colour_lets_try")
        else:
            self.speak(self.knowledge[1]+self.text_scenario["goodChoice_end_part"],rawtext=True)

    def material(self):
        if self.knowledge[2]=="":
            favoured_material=TraitsArray[2][0]
            self.speak(self.text_scenario["materialOffer_part1"]+self.knowledge[0]+self.text_scenario["materialOffer_part2"]+favoured_material+self.text_scenario["materialOffer_part3"],rawtext=True)
            wikitext=self.get_wiki_text(2,0)
            if wikitext=="page not found" or wikitext=="no wikipath":
                print(wikitext)
            else:
                self.speak("foundWikiInfo")
                print(wikitext)
                self.speak(wikitext,rawtext=True,motion="improvised_not_sure")
            self.speak(self.text_scenario["offer2_part1"]+favoured_material+self.text_scenario["offer2_part2"],rawtext=True)
            answer = self.listen()
            self.store_traits(answer)
            if self.search_answer_or(self.text_scenario["yes"],answer):
                self.speak("goodChoice")
                self.knowledge[2]=favoured_material
            else:
                traits = self.assemble_traits(TraitsArray[2][1:],"und")
                sentence = self.text_scenario["weHave"]+traits
                self.speak(sentence,rawtext=True)
                self.speak("askIfMoreWiki")
                self.consult_material()
                self.speak("soWhatMaterial")
                answer = self.listen()
                self.store_traits(answer)
            if self.knowledge[2]=="":
                self.emotion_acc_reset()
                sentence=self.random_sentence(self.text_scenario["okay"])+self.text_scenario["offer3_part1"]+favoured_material+self.text_scenario["offer3_part2"]
                self.knowledge[2]=favoured_material
                self.speak(sentence,rawtext=True)
                self.react_emotion("Choice_by_robot")

    def size(self):
        indexOfCloth=TraitsArray[0].index(self.knowledge[0])
        topic_index_size1=-1
        topic_index_size2=-1
        sizename1=self.text_scenario["size"]
        sizename2=""
        for topic in range(Offset_size,len(Topics_include_matrix[indexOfCloth])):
            if Topics_include_matrix[indexOfCloth][topic]==1 and topic_index_size1==-1:
                topic_index_size1=topic
            elif Topics_include_matrix[indexOfCloth][topic]==1 and topic_index_size2==-1:
                topic_index_size2=topic
        if topic_index_size1!=-1 and topic_index_size2==-1:
            if TopicArray[topic_index_size1]=="size footwear":
                sizename1=TopicGerman[topic_index_size1]
            if self.try_on_count>0:
                sentence=self.text_scenario["changeSize_part1"]+sizename1+self.text_scenario["changeSize_part2"]+sizename1+self.text_scenario["changeSize_part3"]
                self.speak(sentence,rawtext=True)
            else:
                sentence=self.text_scenario["askwhatneeded_part1"]+sizename1+self.text_scenario["askwhatneeded_part2"]
                self.speak(sentence,rawtext=True)
        elif topic_index_size1!=-1 and topic_index_size2!=-1:
            if TopicArray[topic_index_size1]=="size bottom wide":
                sizename1=TopicGerman[topic_index_size1]
            if TopicArray[topic_index_size2]=="size bottom length":
                sizename2=TopicGerman[topic_index_size2]
            if self.try_on_count>0:
                sentence=self.text_scenario["changeSize2_part1"]+sizename1+self.text_scenario["changeSize2_part2"]+sizename2+self.text_scenario["changeSize2_part3"]+sizename1+self.text_scenario["changeSize2_part4"]+sizename2+self.text_scenario["changeSize2_part5"]
                self.speak(sentence,rawtext=True)
            else:
                sentence=self.text_scenario["askwhatneeded2_part1"]+sizename1+self.text_scenario["askwhatneeded2_part2"]+sizename2+self.text_scenario["askwhatneeded2_part3"]
                self.speak(sentence,rawtext=True)
        answer=self.listen()
        self.choice_complete=True

    def try_on(self):
        if self.try_on_count==0:
            sentence=self.text_scenario["bringCloth"]+self.knowledge[0]+"."
            self.speak(self.correct_sentence(sentence),rawtext=True,motion="bringCloth")
            time.sleep(2)
            self.speak("tryItOn")
            self.observe_emotion(3)
            self.react_emotion("try_on_observe")
            self.speak("askSizeFit")
        elif self.try_on_count>0:
            sentence=self.text_scenario["bringClothAgain_part1"]+self.knowledge[0]+self.text_scenario["bringClothAgain_part2"]
            self.speak(self.correct_sentence(sentence),rawtext=True)
            time.sleep(2)
            self.speak("tryItOn")
            self.observe_emotion(3)
            self.react_emotion("try_on_observe2")
            self.speak("askFitBetter")
        answer=self.listen()
        if self.search_answer_or(self.text_scenario["no"],answer) or self.search_answer_or(["klein","groß","eng"], answer):
            self.try_on_count+=1
            if self.try_on_count>=2:
                self.speak("nothingFits")
                self.successful_sale=False
                return
            self.choice_complete=False
        elif self.search_answer_or(self.text_scenario["yes"], answer):
            self.speak("robotHappy")
            self.try_on_count+=1
            self.tried_on=True

    def make_payment(self):
        self.emotion_acc_reset()
        if self.price_offer_count==0:
            self.price_reduction(item=self.knowledge[0],amount=20,situation="normal_offer")
        cloth_index=TraitsArray[0].index(self.knowledge[0])
        material_index=TraitsArray[2].index(self.knowledge[2])
        price=Pricetable[material_index][cloth_index]
        sentence=self.text_scenario["tellPrice"]+str(price)+" "+self.text_scenario["currency"]+"."
        if self.price_offer_count>0:
            if self.price_discount[1]=="Prozent":
                price_reduced=price*(1-self.price_discount[0]/100)
                price_reduced=round(price_reduced)
        self.speak(sentence,rawtext=True)
        if self.price_offer_count>0:
            sentence=self.text_scenario["tellPriceReduction_part1"]+str(self.price_discount[0])+" "+self.price_discount[1]+"."
            sentence+=self.text_scenario["tellPriceReduction_part2"]+str(price_reduced)+" "+self.text_scenario["currency"]+"."
            self.speak(sentence,rawtext=True)
        self.speak("askPayment")
        answer=self.listen()
        self.speak("paymentCompleted")
        self.payed = True

    def farewell(self):
        if self.successful_sale==True:
            self.speak("farewell_first_roleplay_positive1")
            self.react_emotion("after_payment")
            self.speak("farewell_first_roleplay_positive2",motion="farewell_first_roleplay_positive2")
        else:
            self.speak("inviteToNextTime")
            self.speak("farewell_first_roleplay_negative")
        self.roleplay_end=True

    def end_first_roleplay(self):
        self.speak(self.random_sentence(self.text_scenario["okay"])+self.text_scenario["firstRoleplayDone"],rawtext=True,motion="firstRoleplayDone")

    def consult_material(self):
        information_colllected=False
        self.emotion_acc_reset()
        while information_colllected!=True:
            answer=self.listen()
            if self.search_answer_or(self.text_scenario["no"],answer) or not self.search_answer_or(TraitsArray[2],answer):
                information_colllected=True
            elif self.search_answer_or(TraitsArray[2],answer):
                materials=self.search_return_topics(TraitsArray[2],answer)
                for material in materials:
                    material_index=TraitsArray[2].index(material)
                    wikitext=self.get_wiki_text(2,material_index)
                    self.speak(self.text_scenario["foundSpecificWiki_part1"]+material+self.text_scenario["foundSpecificWiki_part2"],rawtext=True)
                    self.speak(wikitext,rawtext=True)
                self.speak("askIfMoreWiki2")
        self.react_emotion("end_consult_material")

    def price_reduction(self, item=TraitsArray[0][0], discount_type="Prozent", amount=10, situation="normal_offer"):
        if self.validate_price_reduction(discount_type,amount)==False:
            print("Not a valid reduction_type-amount combination: "+reduction_type+" "+amount)
            return
        self.price_discount=[amount,discount_type]
        self.price_offer_count+=1
        if situation=="normal_offer":
            sentence=self.text_scenario["normalOffer_part1"]+str(amount)+" "+discount_type+self.text_scenario["normalOffer_part2"]+item+self.text_scenario["normalOffer_part3"]
            sentence=self.correct_sentence(sentence)
            self.speak(sentence,rawtext=True)
            return
        elif situation=="first time customer":
            self.speak(self.text_scenario["firstTimeCustomerPrice"]+str(amount)+" "+discount_type,rawtext=True)
            return
        elif situation=="repeated offer":
            self.speak(self.text_scenario["repeatedOfferPrice"]+str(amount)+" "+discount_type,rawtext=True)
            return
        else:
            print("Not a valid reduction-type: "+discount_type)
            return

    def validate_price_reduction(self,discount_type,amount):
        if discount_type=="Prozent":
            if amount<=0 or amount>100:
                print("not a valid percentage: "+amount)
                return False
        elif discount_type=="Euro":
            if amount<=0:
                print("not a valid amount: "+amount)
                return False
        return True

    def knowledge_empty(self):
        for trait in range(Offset_size):
            if(self.knowledge[trait]!=""):
                return False
        return True

    #stores all recognized traits in answer in knowledge
    def store_traits(self,answer,overwrite=False) :
        for topic in range(Offset_size) :
            for trait in TraitsArray[topic] :
                if  self.search_answer_or([trait],answer) :
                    #print("trait: "+trait+" answer: "+answer)
                    if self.knowledge[topic] == "" or overwrite :
                        self.knowledge[topic]=trait #store traits of Portfolio

    def search_return_topics(self,keywords,answer):
        foundTopics=[]
        for keyword in keywords:
            if keyword.lower() in answer.lower():
                foundTopics.append(keyword)
        return foundTopics

#################################second roleplay############################
    def second_roleplay(self):
        self.reset_data()
        self.emotion_acc_reset()
        self.introduction_second_roleplay()
        self.emotion_acc_reset()
        self.welcome_second_roleplay()
        goBlock=self.determine_block2()
        while (goBlock!="no topics left") and (self.successful_sale==True):
            self.continueToBlock2(goBlock)
            goBlock=self.determine_block2()
        self.end_second_roleplay()
        return

    def determine_block2(self):
        if self.after_request==False:
            return "tell_request"
        elif self.choice_complete==False:
            return self.check_situation()
        elif self.tried_on==False:
            return "try_on"
        elif self.payed==False:
            return "make_payment"
        elif self.roleplay_end==False:
            return "farewell"
        else:
            return "no topics left"

    def check_situation(self):
        for topic in range(Offset_size):
            if Goal[topic]=="":
                return TopicArray[topic]
            if Goal[topic].lower() not in TraitsArray[topic]:
                return TopicArray[topic]
        return "size"

    def continueToBlock2(self, goBlock):
        if goBlock=="tell_request":
            eval("self."+goBlock+"()")
            return
        if goBlock=="try_on" or goBlock=="make_payment" or goBlock=="size" or goBlock=="farewell":
            eval("self."+goBlock+"2()")
            return
        for topic in TopicArray:
            if topic is goBlock:
                eval("self."+topic+"2()")
                return
        return # when goBlock="no topics left"

    def introduction_second_roleplay(self):
        self.speak("introduction_second_roleplay1")
        self.react_emotion("start_second_roleplay")
        self.speak("introduction_second_roleplay2",motion="introduction_second_roleplay2")

    def welcome_second_roleplay(self):
        mistakes=2
        counter=0
        while mistakes>1 and counter<2:
            counter+=1
            mistakes=0
            answer=self.listen()
            if self.search_answer_or(self.text_scenario["answer_greeting"],answer)!=True:
                if counter==1:
                    self.speak("hint_greeting",pause_emotion_detection=True)
                mistakes+=1
            if self.search_answer_or(self.text_scenario["answer_welcome"],answer)!=True:
                if counter==1:
                    self.speak("hint_welcome",pause_emotion_detection=True)
                mistakes+=1
            if self.search_answer_or(self.text_scenario["answer_brand"],answer)!=True:
                if counter==1:
                    self.speak("hint_brand",pause_emotion_detection=True)
                mistakes+=1
            if self.search_answer_or(self.text_scenario["answer_help"],answer)!=True:
                if counter==1:
                    self.speak("hint_help",pause_emotion_detection=True)
                mistakes+=1
            if mistakes>1 and counter==1:
                self.speak("repeatWelcome",pause_emotion_detection=True)
            if mistakes>0 and counter>1:
                self.speak("notPerfectMoveOn",pause_emotion_detection=True)

    def tell_request(self):
        if self.goal_is_empty()==False:
            request="Hallo. "
            for topic in range(Offset_size):
                if Goal[topic]!="" and TopicArray[topic]=="clothes":
                    request+="Ich bin auf der Suche nach einer "+Goal[topic]
                    if Goal[1]=="":
                        request+=". "
                elif Goal[topic]!="" and TopicArray[topic]=="colour":
                    if Goal[0]!="":
                        request+=" in "+Goal[topic]+"er Farbe. "
                    else:
                        request+="Ich suche etwas in "+Goal[topic]+". "
                elif Goal[topic]!="" and TopicArray[topic]=="material":
                    request+="Es wäre schön, wenn es das aus "+Goal[topic]+" gebe. "
                elif Goal[topic]!="":
                    request+="Außerdem suche ich etwas mit "+Goal[topic]+". "
            request=self.correct_sentence(request)
            self.speak(request,rawtext=True)
            answer=self.listen()
            self.store_suggestion(answer)
        self.after_request=True

    def clothes2(self):
        if Goal[0]=="":
            right_answer=False
            trycount=0
            countlimit=1
            while right_answer==False:
                if trycount==countlimit:
                    right_answer=True
                trycount+=1
                self.speak("spontaneousArrival")
                answer=self.listen()
                self.store_suggestion(answer)
                if self.search_array(TraitsArray[0],self.suggestion[0],"and")!=True:
                    if self.search_array(TraitsArray[0],self.suggestion[0],"or")!=True:
                        self.speak("hint_topicOrder")
                    else:
                        forgotten_traits=[]
                        for trait in TraitsArray[0]:
                            if self.search_answer_or([trait],self.assemble_traits(self.suggestion[0]," "))!=True:
                                forgotten_traits.append(trait)
                        sentence=self.text_scenario["hint_forgot2Mention_part1"]+self.assemble_traits(forgotten_traits,"und")+self.text_scenario["hint_forgot2Mention_part2"]
                        self.speak(sentence,pause_emotion_detection=True,rawtext=True)
                    if right_answer==False:
                        self.speak("repeat_request",pause_emotion_detection=True,motion="repeat_request")
                else:
                    right_answer=True
            if len(self.suggestion[0])>0:
                random_cloth=self.random_sentence(self.suggestion[0])
                Goal[0]=random_cloth
                sentence=self.correct_sentence(self.text_scenario["wantHave_part1"]+Goal[0]+self.text_scenario["wantHave_part2"])
                self.speak(sentence,rawtext=True)
            else:
                Goal[0]=self.random_sentence(TraitsArray[0])
                return
        if Goal[0]!="" and self.try_on_count==0:
            if not Goal[0] in TraitsArray[0]:
                if len(self.suggestion[0])>0:
                    random_cloth=self.random_sentence(self.suggestion[0])
                    Goal[0]=random_cloth
                    self.speak(self.correct_sentence(self.text_scenario["wantHaveInstead_part1"]+Goal[0]+self.text_scenario["wantHaveInstead_part2"]),rawtext=True)

    def colour2(self):
        if Goal[1]=="":
            if len(self.suggestion[1])==0:
                self.speak("whatcolours")
                answer=self.listen()
                self.suggest_trait(1)
            random_colour=self.random_sentence(self.suggestion[1])
            Goal[1]=random_colour
            self.speak(self.text_scenario["thinkGoodColour_part1"]+random_colour+self.text_scenario["thinkGoodColour_part2"],rawtext=True)
        elif Goal[1]!="":
            if len(self.suggestion[1])==0:
                self.speak("whatcolours")
                answer=self.listen()
                self.store_suggestion(answer)
            elif Goal[1] in self.suggestion[1]:
                sentence=self.text_scenario["wantThat_part1"]+Goal[1]+self.text_scenario["wantThat_part2"]+Goal[0]+self.text_scenario["wantThat_part3"]+Goal[1]+self.text_scenario["wantThat_part4"]
                self.speak(self.correct_sentence(sentence),rawtext=True)
            else:
                self.speak(self.text_scenario["noColour_part1"]+Goal[1]+self.text_scenario["noColour_part2"],rawtext=True)
                answer=self.listen()
                if self.search_answer_or(self.text_scenario["yes"],answer):
                    self.speak(self.text_scenario["IChoose"]+Goal[1]+".",rawtext=True)
                else:
                    random_colour=self.random_sentence(self.suggestion[1])
                    Goal[1]=random_colour
                    self.speak(self.text_scenario["notThereTryInstead_part1"]+Goal[1]+self.text_scenario["notThereTryInstead_part2"],rawtext=True)
        return

    def material2(self):
        if len(self.suggestion[2])==0:
            self.speak(self.correct_sentence(self.text_scenario["whatMaterial_part1"]+Goal[0]+self.text_scenario["whatMaterial_part2"]),rawtext=True)
            answer=self.listen()
            self.store_suggestion(answer)
        if Goal[2]=="":
            if len(self.suggestion[2])>0:
                Goal[2]=self.random_sentence(self.suggestion[2])
        if len(self.suggestion[2])>0:
            if not self.search_array(Goal[2],self.suggestion[2]):
                self.speak(self.text_scenario["insteadMaterial_part1"]+Goal[2]+self.text_scenario["insteadMaterial_part2"],rawtext=True)
                answer=self.listen()
                if self.search_answer_or(self.text_scenario["no"],answer) and self.search_array(Goal[2],TraitsArray[2]):
                    self.speak(self.text_scenario["hint_assortment_part1"]+Goal[2]+self.text_scenario["hint_assortment_part2"],pause_emotion_detection=True,rawtext=True)
                else:
                    Goal[2]=self.random_sentence(self.suggestion[2])
            if self.search_array(Goal[2],self.suggestion[2]):
                self.speak("iThink",motion="iThink")
                self.consult()
                self.speak(self.random_sentence(self.text_scenario["understand"])+self.text_scenario["wantChoose-part1"]+Goal[2]+self.text_scenario["wantChoose-part2"],rawtext=True)
        elif len(self.suggestion[2])==0:
            if Goal[2]=="" or not self.search_array(Goal[2],TraitsArray[2]):
                Goal[2]=self.random_sentence(TraitsArray[2])
            self.speak("hint_proceedNoMaterial",pause_emotion_detection=True)
            self.suggestion[2].extend(TraitsArray[2])
        self.emotion_evaluate_halftime()

    def size2(self):
        # determine which size is necessary
        indexOfCloth=TraitsArray[0].index(Goal[0])
        topic_index_size1=-1
        topic_index_size2=-1
        sizename1=self.text_scenario["size"]
        sizename2=""
        sentencepart1=self.text_scenario["ineed"]+Goal[0]
        for topic in range(Offset_size,len(Topics_include_matrix[indexOfCloth])):
            if Topics_include_matrix[indexOfCloth][topic]==1 and topic_index_size1==-1:
                topic_index_size1=topic
            elif Topics_include_matrix[indexOfCloth][topic]==1 and topic_index_size2==-1:
                topic_index_size2=topic

        if Goal[topic_index_size1]=="":
            Goal[topic_index_size1]=self.random_sentence(TraitsArray[topic_index_size1])
        if topic_index_size2>0:
            if Goal[topic_index_size1]=="":
                Goal[topic_index_size2]=self.random_sentence(TraitsArray[topic_index_size2])
        if topic_index_size1!=-1 and topic_index_size2==-1:
            if TopicArray[topic_index_size1]=="size footwear":
                sizename1=TopicGerman[topic_index_size1]
            sentence=sentencepart1+" in "+sizename1+" "+Goal[topic_index_size1]
        elif topic_index_size1!=-1 and topic_index_size2!=-1:
            if TopicArray[topic_index_size1]=="size bottom wide":
                sizename1=TopicGerman[topic_index_size1]
            if TopicArray[topic_index_size2]=="size bottom length":
                sizename2=TopicGerman[topic_index_size2]
            sentence=sentencepart1+"in "+sizename1+" "+Goal[topic_index_size1]+" und "+sizename2+" "+Goal[topic_index_size2]
        sentence=self.correct_sentence(sentence)
        self.speak(sentence,rawtext=True)
        self.choice_complete=True

    def try_on2(self):
        answer=self.listen()
        sentence=""
        if not self.search_answer_or(["probieren","hole","Moment","gebe"],answer):
            self.speak("hint_tryOn",pause_emotion_detection=True)
            sentence=self.random_sentence(self.text_scenario["okay"])
        sentence+=self.text_scenario["instructionProceed"]
        self.speak(sentence,rawtext=True)
        answer=self.listen()
        if not self.search_answer_or(["pass","find","sieht","steht","nehmen","gefällt","sitzt"],answer):
            sentence=self.text_scenario["hint_youLikeIt_part1"]+self.text_scenario["repeat_request"]+self.text_scenario["hint_youLikeIt_part2"]
            self.speak(sentence,pause_emotion_detection=True,rawtext=True)
            answer=self.listen()
        sentence=self.correct_sentence(self.text_scenario["want2buy_part1"]+Goal[0]+self.text_scenario["want2buy_part2"]+Goal[0]+self.text_scenario["want2buy_part3"])
        self.speak(sentence,rawtext=True)
        self.tried_on=True

    def make_payment2(self):
        answer=self.listen()
        if not self.search_answer_or(["preis","euro","koste","macht"],answer):
            self.speak(self.text_scenario["hint_payment_part1"]+self.text_scenario["repeat_request"]+self.text_scenario["hint_payment_part2"],pause_emotion_detection=True,rawtext=True)
            answer=self.listen()
        if not self.search_answer_or(["zahlen","karte","bar"],answer):
            self.speak("okay")
            answer=self.listen()
            if not self.search_answer_or(["zahlen","karte","bar"],answer):
                self.speak("hint_paymentMethod",pause_emotion_detection=True)
        self.speak("want2pay")
        self.speak(self.random_sentence(self.text_scenario["okay"])+self.text_scenario["paymentCompleted2"],rawtext=True)
        self.payed=True

    def farewell2(self):
        answer=self.listen()
        tryOnceMore=False
        if not self.search_answer_or(["tschüss","Wiedersehen","bis bald","nächsten Mal","tschau","schönen Tag"],answer):
            self.speak("hint_sayBye",pause_emotion_detection=True)
            tryOnceMore=True
        if not self.search_answer_or(["wünsche","gut","schön","freue"],answer):
            self.speak("hint_positiveWords",pause_emotion_detection=True)
            tryOnceMore=True
        if not self.search_answer_or(["dank"],answer):
            self.speak("hint_sayThank",pause_emotion_detection=True)
            tryOnceMore=True
        if tryOnceMore:
            self.speak("repeat_request",pause_emotion_detection=True)
            self.listen()
        self.speak("sayBye")
        self.roleplay_end=True

    def end_second_roleplay(self):
        self.speak(self.random_sentence(self.text_scenario["okay"])+self.text_scenario["farewell_second_roleplay"],pause_emotion_detection=True,rawtext=True)
        self.emotion_evaluate_second_roleplay()
        return

    def consult(self):
        indexOfgoal=TraitsArray[2].index(Goal[2])
        numberOfquestions=len(Consult_material_questions[indexOfgoal])
        questions_answered=0
        repeated_question=False
        self.speak(Consult_material_questions[indexOfgoal][questions_answered],rawtext=True)
        while questions_answered<numberOfquestions:
            answer=self.listen()
            if self.search_answer_or(Consult_material_keywords[indexOfgoal][questions_answered],answer) or repeated_question==True:
                if repeated_question==True and not self.search_answer_or(Consult_material_keywords[indexOfgoal][questions_answered],answer):
                    sentence=self.text_scenario["hint_consult_part1"]+self.assemble_traits(Consult_material_keywords[indexOfgoal][questions_answered],"und")+self.text_scenario["hint_consult_part2"]
                    self.speak(sentence,rawtext=True)
                questions_answered+=1
                if questions_answered==numberOfquestions:
                    break
                sentence=self.random_sentence(self.text_scenario["understand"])+Consult_material_questions[indexOfgoal][questions_answered]
                self.speak(sentence,rawtext=True)
                repeated_question=False
            else:
                self.speak("askPreciseAnswer",motion="askPreciseAnswer")
                repeated_question=True

    # provided that there is something left to choose
    # makes sure at least one right trait has been suggested
    def suggest_trait(self,topic_index):
        topic=TopicGerman[topic_index]
        request=self.correct_sentence(self.text_scenario["whatYouRecommend_part1"]+topic+self.text_scenario["whatYouRecommend_part2"])
        right_answer=False
        trylimit=4
        tries=0
        while right_answer==False:
            self.speak(self.text_scenario["canNotDecide"]+request,rawtext=True)
            answer=self.listen()
            if self.search_answer_or(TraitsArray[topic_index],answer):
                right_answer=True
            else:
                self.speak("hint_OfferRight")
                self.speak("repeat_request",motion="repeat_request")
            tries+=1
            if tries>=trylimit:
                self.speak(self.text_scenario["proceedConsult_part1"]+topic+self.text_scenario["proceedConsult_part2"],rawtext=True)
                self.store_suggestion(self.random_sentence(TraitsArray[topicindex]))
                return
        self.suggestion[topic_index]=[]
        self.store_suggestion(answer)

    def emotion_evaluate_halftime(self):
        percent_friendly=self.calculate_friendlyness()
        if not percent_friendly>self.desired_friendly_limit:
            self.speak("hint_friendlyFail",pause_emotion_detection=True)

    def emotion_evaluate_second_roleplay(self):
        percent_friendly=self.calculate_friendlyness()
        if percent_friendly>self.desired_friendly_limit:
            self.speak("evaluateFriendlySucces",pause_emotion_detection=True)
        else:
            self.speak("evaluateFriendlyFail",pause_emotion_detection=True)
        self.speak("askEmotionData",pause_emotion_detection=True)
        answer=self.listen(pause_emotion_detection=True)
        if self.search_answer_or(self.text_scenario["yes"],answer):
            self.speak("emotionAdditionalInfo",pause_emotion_detection=True)
            self.emotion_tell_results()
        else:
            self.speak("okay")

    def calculate_sum_emotions(self):
        sum=0
        for key,value in self.accumulate_emotion.items():
            sum+=value
        sum-=self.accumulate_emotion["none"]
        return sum

    def calculate_friendlyness(self):
        sum=self.calculate_sum_emotions()
        if sum==0:
            print("Warning: emotion sum==0")
            return 0
        sum_positive_emotions=self.accumulate_emotion["happy"]+self.accumulate_emotion["neutral"]
        percent_friendly=sum_positive_emotions/sum*100
        return percent_friendly

    def emotion_tell_results(self):
        sum=self.calculate_sum_emotions()
        if sum==0:
            print("Error: sum==0")
            return
        for key,value in self.accumulate_emotion.items():
            if key!="none":
                percent=round(value/sum*100)
                emotion=self.text_scenario[key]
                self.speak(str(percent)+self.text_scenario["tellemotion"]+emotion,pause_emotion_detection=True,rawtext=True)

    def reset_data(self):
        self.knowledge=[""]*len(TopicArray)
        self.price_discount = [0, "none"]
        self.price_offer_count = 0
        self.successful_sale = True
        self.tried_on = False
        self.choice_complete = False
        self.payed = False

    def store_suggestion(self,answer):
        self.suggestion = [[] for i in range(Offset_size)]
        for topic in range(Offset_size):
            for trait in TraitsArray[topic]:
                if self.search_answer_or([trait],answer):
                    if self.already_suggested(trait,topic)==False:
                            self.suggestion[topic].append(trait)
        print("suggestion state: "+str(self.suggestion))

    def search_array(self,elements,arrayToSearch,mode="and"):
        if str(type(elements))=="<class 'str'>":
            if elements in arrayToSearch:
                return True
            else:
                return False
        elif str(type(elements))=="<class 'list'>":
            if mode=="and":
                for i in range(len(elements)):
                    if not elements[i] in arrayToSearch:
                        return False
                return True
            elif mode=="or":
                for i in range(len(elements)):
                    if elements[i] in arrayToSearch:
                        return True
                return False

    def goal_is_empty(self):
        for trait in range(Offset_size):
            if Goal[trait]!="":
                return False
        return True

    def search_answer_and(self,keyword_groups,answer):
        if answer=="" or str(type(answer))=="<class 'NoneType'>":
            return False
        for keyword in keyword_groups:
            if not self.search_answer_or([keyword],answer):
                return False
        return True

#################################used in both roleplays############################
    def emotion_acc(self,emotion):
        self.accumulate_emotion[emotion]+=1

    def emotion_give_dominant(self):
        max_key=max(self.accumulate_emotion, key=self.accumulate_emotion.get)
        valueList=list(self.accumulate_emotion.values())
        counted=valueList.count(self.accumulate_emotion[max_key])
        if counted>1:
            return "none"
        return max_key

    def emotion_acc_reset(self):
        if emotion_detection==False:
            return
        for key,value in self.accumulate_emotion.items():
            self.accumulate_emotion[key]=0

    def observe_emotion(self,seconds=3):
        #self.emotion_acc_reset()
        self.sobot.detect(command="start")
        time.sleep(seconds)
        emotion=self.sobot.detect(command="stop")
        self.emotion_acc(emotion)

    def react_emotion(self,reaction_name):
        if emotion_detection==False:
            return
        emotion=self.emotion_give_dominant()
        if emotion=="none":
            return
        if emotion not in self.emotions:
            print("emotion not found: "+emotion)
            return
        emotion_index=self.emotions.index(emotion)
        if reaction_name not in self.emotion_scenario:
            print("reaction name or reaction not found")
            return
        reaction_array=self.emotion_scenario[reaction_name]
        sentence=reaction_array[emotion_index]
        if sentence=="":
            return
        gesture=reaction_name+"_"+emotion
        self.speak(sentence,motion=gesture,rawtext=True)

    # search if at least one keyword appears in answer
    def search_answer_or(self,keywords,answer) : # keywords has to be an array/iterable
        if answer=="":
            return False
        for keyword in keywords :
            self.sobot.log(f"search for keyword: {keyword} in {keywords}")
            if keyword.lower() in answer.lower():
                return True
        return False

    def random_sentence(self, sentences) :
        t = time.time()
        t = round(t) # rounds to int
        seed(t)
        selection = choice(sentences)
        return selection

    def assemble_traits(self, traits, conjunction) : # traits has to be array of words!
        if len(traits)==0:
            print("assemble_traits received empty list!")
            return ""
        sentencepart = " "+traits[0]+" "
        for i in range(1, len(traits)) :
            if i < (len(traits)-1) :
                sentencepart += traits[i] + " "
            elif (len(traits)-1) == i  :
                sentencepart += conjunction+ traits[i] + " "
        return sentencepart

#################################Wiki API############################
    def get_wiki_text(self, index_topic, index_trait):
        if len(Wikipath[index_topic][index_trait])>0:
            page = self.wikiobject.page(Wikipath[index_topic][index_trait][0])
            if page.exists():
                for section_index in range(1,len(Wikipath[index_topic][index_trait])):
                    section=page.section_by_title(Wikipath[index_topic][index_trait][section_index])
            else:
                return "page not found"
            return self.filtertext(section.text)
        else:
            return "no wikipath"

    def filtertext(self, text):
        rest_of_text=self.removebrackets(text)
        extracted_text=""
        sentence_count=0
        while len(rest_of_text)>1 and sentence_count<self.sentence_limit:
            index=rest_of_text.find(".")
            if index!=-1:
                extracted_sentence=rest_of_text[:index+1]
                rest_of_text=rest_of_text[index+1:]
                if self.search_answer_or(Filterkeywords_include,extracted_sentence):
                    extracted_text+=extracted_sentence
                    sentence_count+=1
            else:
                if self.search_answer_or(Filterkeywords_include,rest_of_text):
                    extracted_text+=extracted_sentence
                    sentence_count+=1
                rest_of_text=""
        return extracted_text

    def removebrackets(self, text):
        found_brackets=True
        while found_brackets==True:
            index_first_bracket=text.find("(")
            index_second_bracket=text.find(")")
            if index_first_bracket!=-1 and index_second_bracket!=-1:
                text=text[:index_first_bracket-1]+text[index_second_bracket+1:]
            else:
                found_brackets=False
        return text

#################################grammar correction############################
    def correct_sentence(self,text):
        if grammar_correction==False:
            return text
        print("text to correct: "+text)
        errors_raw=self.sobot.grammar_check(text)
        errors=ast.literal_eval(errors_raw)
        pointer=0
        corrected_text=""
        for mistake in errors:
            if len(mistake["replacement"])>0:
                corrected_text+=text[pointer:mistake["offset"]]+mistake["replacement"]
                pointer=mistake["offset"]+mistake["length"]
            else:
                corrected_text+=text[pointer:mistake["offset"]+mistake["length"]]
                pointer=mistake["offset"]+mistake["length"]
        corrected_text+=text[pointer:]
        print(corrected_text)
        return corrected_text

#################################punctuation############################
    #pip install transformers
    #pip install sentencepiece
    #pip install deepmultilingualpunctuation
    def store_suggestion_safe(self,answer):
        answer_punctuated=self.set_punctuation(answer)
        sentences=self.split_text_to_sentences(answer_punctuated)
        for topic in range(self.Offset_size):
            for trait in TraitsArray[topic]:
                if self.search_answer_or([trait],answer):
                    if self.already_suggested(trait,topic)==False:
                        if self.inspect_sentence(trait,sentences):
                            self.suggestion[topic].append(trait)

    # returns True if sentence with trait contains no negation
    # otherwise False
    def inspect_sentence(self,trait,sentences):
        for sentence in sentences:
            if self.search_answer_or(trait,sentence):
                if self.search_answer_or(["nicht","kein"],sentence)!=True:
                    return True

    def set_punctuation(self,text):
        model = PunctuationModel()
        result = model.restore_punctuation(text)
        #print("before punctuation: "+text)
        #print("after puncutation: "+result)
        return result

    def split_text_to_sentences(self,text_punctuated=""):
        sentences=[]
        pointFound=True
        while pointFound==True:
            index_point=text_punctuated.find(".")
            if index_point<0:
                pointFound=False
            else:
                sentences.append(text_punctuated[:index_point+1])
                text_punctuated=text_punctuated[index_point+1:]
        return sentences

    def already_suggested(self,trait,topic):
        if trait in self.suggestion[topic]:
            return True
        else:
            return False

#############################################################
def handler(signal_received, frame):
    # Handle cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    commerce_training.terminate()
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, handler)
    parser=argparse.ArgumentParser(description='speech recognition with mqtt client') #arguments are only default, values actually taken when invoking commerce.py with commandline command, for example in sobotify_app_gui
    parser.add_argument('--mosquitto_ip',default='127.0.0.1',help='ip address of the mosquitto server')
    parser.add_argument('--robot_name',default='stickman',help='name of the robot (stickman,pepper,nao)')
    parser.add_argument('--robot_ip',default='127.0.0.1',help='ip address of the robot')
    parser.add_argument('--language',default="german",help='choose language (english,german)')
    parser.add_argument('--sound_device',default=0,type=int,help='number of sound device, can be found with: import sounddevice;sounddevice.query_devices()')
    parser.add_argument('--project_file',default='quiz_data.xlsx',help='project file with app data')
    args=parser.parse_args()

    commerce_training = commerce(args.robot_name,args.robot_ip,args.language,args.sound_device,args.mosquitto_ip,args.project_file)
    commerce_training.run()
    print("scenerio done")
    while True:
        time.sleep(1)
