#-*- coding: utf-8 -*-
"""
command to get the min_attend instances for acts with an attendance_pdf url
"""

#PACKAGE TO INSTALL
#poppler-utils

from django.core.management.base import NoArgsCommand
#new table
from import_app.models import ImportMinAttend
from act_ids.models import ActIds
from act.models import Country, Verbatim, Status
import urllib, urllib2, time, os, tempfile, subprocess
from django.db import IntegrityError


def pdf_to_string(file_object):
    """
    FUNCTION
    get the text of a pdf and put it in a string variable
    PARAMETERS
    file_object: pdf file wrapped in a python file object [File object]
    RETURN
    string: extracted text [string]
    """
    pdfData = file_object.read()

    tf = tempfile.NamedTemporaryFile()
    tf.write(pdfData)
    tf.seek(0)

    outputTf = tempfile.NamedTemporaryFile()

    if (len(pdfData) > 0) :
        out, err = subprocess.Popen(["pdftotext", "-layout", tf.name, outputTf.name ]).communicate()
        return outputTf.read()
    else :
        return None


def find_nth(string, substring, n):
    """
    FUNCTION
    return the index of the occurence number n of substring in a string
    PARAMETERS
    string: string to use for the search [string]
    substring: string to be found [string]
    n: number of the occurence [int]
    RETURN
    start: index of the occurence number n [int]
    """
    start = string.find(substring)
    while start >= 0 and n > 1:
        start = string.find(substring, start+len(substring))
        n -= 1
    return start


def get_participants(string):
    """
    FUNCTION
    extract the participant part from the pdf (just before the ITEMS DEBATED section)
    PARAMETERS
    string: text extracted from the pdf [string]
    RETURN
    string: participant part [string]
    """
    begin=end=-1
    participants=["PARTICIPA(cid:6)TS", "PARTICIPANTS", "PARTICIPA TS"]
    for participant in participants:
        begin=find_nth(string, participant, 2)
        if begin!=-1:
            break

    #TOBACCO: http://www.consilium.europa.eu/uedocs/cms_data/docs/pressdata/en/agricult/70070.pdf
    items=["ITEMS DEBATED", "TOBACCO"]
    for item in items:
        end=string.find(item, begin)
        if end!=-1:
            break

    return string[begin:end].split('\n')



def string_to_file(string, path):
    """
    FUNCTION
    save a string into a txt file
    PARAMETERS
    string: string to save [string]
    path: path of the file to use [string]
    RETURN
    None
    """
    with open(path, "w") as text_file:
        text_file.write(string)


def file_to_string(path):
    """
    FUNCTION
    get the text of a txt file
    PARAMETERS
    path: path of the file to use [string]
    RETURN
    participants: text of the file split at each line break [list of strings]
    """
    with open(path) as string:
        participants=string.read().split('\n')
    return participants


def capitalized_word(words, display=False):
    """
    FUNCTION
    check if there is at least one capitalized word in a group of words (used to detect ministers's names)
    PARAMETERS
    words: group of words to check [string]
    RETURN
    True if there is at least one capitalized word, False otherwise [boolean]
    """
    #Micheál MARTIN without Mr or Ms

    #PROVISIO AL VERSIO: http://www.consilium.europa.eu/uedocs/cms_data/docs/pressdata/en/envir/99178.pdf
    #not any(char.isdigit() for char in word): discard dates (roman numerals are in upper case)
    if words!="PROVISIO AL VERSIO" and not any(char.isdigit() for char in words):
        words=words.split()
        excluded_list=["EU","EN"]
        for word in words:
            #word.isupper() is what we really want to test
            #http://www.consilium.europa.eu/uedocs/cms_data/docs/pressdata/en/lsa/111599.pdf
            #len(word)>1: "E" (problem with N of EN)
            if word.isupper() and len(word)>1 and word not in excluded_list:
                if display:
                    print "word", word
                    print "word.isupper()", word.isupper()
                    print "not any(char.isdigit() for char in word)", not any(char.isdigit() for char in word)
                    print "word not in [EU,EN]", word not in ["EU","EN"]
                return True

    return False


def remove_footer_header(new_participants, country_list):
    #if two pages, remove footer and header of separation
    begin=-1
    for i in range(len(new_participants)):
        participant=new_participants[i].strip()
        #don't take into account countries after UK (last country) -> countries part of the commission or accedding states
        if "United Kingdom" in participant:
            break
        
        #'Ms Audron MORNIEN', 'Deputy minister for Social Security and Labour', '16611/2/09 REV 2 (en) (Presse 348)                                                                             5', 'E', '30.XI-1.XII.2009', 'Luxembourg:', 'Mr Mars DIBO'
        #find beginning of string (footer / header) to be removed
        if any(char.isdigit() for char in participant):
            #remove isolated footer / header elements
            if begin==-1:
                begin=i

            #http://www.consilium.europa.eu/uedocs/cms_data/docs/pressdata/en/trans/137408.pdf
            #remove footer / header elements inside verbatim
            

        #new page starts with a minister's name from a country started on the previous page
        #http://www.consilium.europa.eu/uedocs/cms_data/docs/pressdata/en/gena/87078.pdf
        #or new page starts with a new country
        if begin!=-1 and (participant[:2].lower() in ["mr", "ms"] or capitalized_word(participant) or participant.split(":")[0].strip() in country_list):
            #~ print "PB"
            #~ print new_participants[i]
            #~ print new_participants[i-5:i+5]
            #~ capitalized_word(new_participants[i], True)
            #~ print ""
            #~ print new_participants
            new_participants=new_participants[:begin]+new_participants[i:]
            #~ print ""
            #~ print new_participants
            #~ begin=-1
            break

    return new_participants
            


def format_participants(participants, country_list):
    """
    FUNCTION
    get the participants only from the participants part (remove extra or unreadble characters, blanks, header, footer...)
    keep only countries, ministers' names and verbatims
    PARAMETERS
    participants: text of the participant part split at each line break [list of strings]
    country_list: list of EU countries [list of string]
    RETURN
    new_participants: participants part (countries, ministers' names and verbatims)  [list of strings]
    """
    new_participants=[]

    #~ print "begin participants"
    #~ print participants
    #~ print ""

    #separate 'Mr Didier REYNDERS                  Deputy Prime Minister and Minister for Foreign Affairs,'
    for participant in participants:
        participant=participant.strip()
        #remove empty items
        if participant!="":
            #~ print "participant", participant
            if participant[:2].lower() in ["mr", "ms"] or capitalized_word(participant):
                for i in range(len(participant)):
                    if participant[i]==" " and participant[i+1]==" ":
                        #add Mr or Ms
                        new_participants.append(participant[:i].strip())
                        #add verbatim
                        new_participants.append(participant[i:].strip())
                        break
                else:
                    new_participants.append(participant)
            else:
                new_participants.append(participant)

    #~ print "begin new_participants"
    #~ print new_participants
    #~ print ""

    #start the list with the first participant (Belgium)
    for participant in new_participants:
        if participant.strip() in ["Belgium", "Belgium:", "Belgium :"]:
            index_belgium=new_participants.index(participant)
            break

    new_participants=new_participants[index_belgium:]

    #~ print "begin new_participants"
    #~ print new_participants
    #~ print ""

    #remove first header / footer
    new_participants=remove_footer_header(new_participants, country_list)
    #remove second header / footer
    new_participants=remove_footer_header(new_participants, country_list)


    #~ print "begin new_participants before UK"
    #~ print new_participants
    #~ print ""

    #stop after last country (uk usually)
    index_uk=len(new_participants)-1
    for participant in new_participants:
        #remove all whitespaces from the string
        temp=''.join(participant.split())
        if temp in ["Commission", "Commission:", "***"]:
            index_uk=new_participants.index(participant)
            #~ print 'uk ok'
            break
        #~ else:
            #~ print participant.strip()

    new_participants=new_participants[:index_uk]
#~ 
    #~ print "new_participants BEFORE"
    #~ print new_participants
    #~ print ""

    #~ #remove "*" before the word "Commission" and remove final header / footer
    for i, element in reversed(list(enumerate(new_participants))):
        element=element.strip()
        #~ print "element", element
        if "*" not in element and not any(char.isdigit() for char in element) and element !="EN" and len(element)>1:
            new_participants=new_participants[:i+1]
            break

    #~ print "new_participants AFTER"
    #~ print new_participants
    #~ print ""
    return new_participants


def get_countries(participants, country_list):
    """
    FUNCTION
    for each country, group together the country name and its ministers' names and verbatims
    PARAMETERS
    participants: list of participants split at each line break [list of strings]
    country_list: list of EU countries [list of string]
    RETURN
    countries: participants with countries and associated ministers grouped together [list of lists of strings / lists]
    """
    countries=[]
    for index in range(len(participants)):
        #~ print "participant", participant
        country=participants[index].split(":")[0].strip()
        #problem when conversion from pdf to text
        if country=="etherlands":
            country="Netherlands"
        #http://www.consilium.europa.eu/uedocs/cms_data/docs/pressdata/en/agricult/101422.pdf
        #'Ms Michelle GILDERNEW', 'Minister for Agriculture and Rural Development, Northern', 'Ireland']
        #http://www.consilium.europa.eu/uedocs/cms_data/docs/pressdata/en/agricult/70070.pdf
        #'Portugal :', 'Mr Jaime SILVA', 'Agricultural Counsellor at the Permanent Representation of', 'Portugal', 'Finland :
        if country in country_list and index<len(participants)-1 and participants[index+1].split(":")[0].strip() not in country_list:
            countries.append([country, []])
        else:
            countries[-1][1].append(participants[index])

    #~ print "countries"
    #~ print countries
    #~ print ""
    #~ print "nb countries", len(countries)
    #~ print ""
    return countries


def get_verbatims(countries, country_list):
    """
    FUNCTION
    get the final format of the ministers' attendance: remove ministers' name and split the country into as many parts as there are ministers
    PARAMETERS
    participants: list of participants split at each line break [list of strings]
    country_list: list of EU countries [list of string]
    RETURN
    countries: participants with countries and associated ministers grouped together [list of lists of strings / lists]
    """
    verbatims=[]

    #check that each country starts with a minister's name, not a verbatim
    #-> pb Belgium with http://www.consilium.europa.eu/uedocs/cms_data/docs/pressdata/en/agricult/75376.pdf
    #['Belgium', ['Minister, attached to the Minister for Foreign Affairs, with', 'Ms Annemie NEYTS-UTTENBROEK', 'responsibility for Agriculture', 'Mr Jos\xc3\xa9 HAPPART', 'Minister for Agriculture and Rural Affairs (Walloon Region)', 'Ms Vera DUA', 'Minister for the Environment and Agriculture (Flemish Region)']]
    #~ print "countries BEFORE moving ministers", countries
    #~ print ""
    nb_pbs=[0, ""]
    for country in countries:
        first=country[1][0].lstrip()
        #pb
        if first[:2].lower() not in ["mr", "ms"] or not capitalized_word(first):
            for index in range(len(country[1])):
                if country[1][index].lstrip()[:2].lower() in ["mr", "ms"] or capitalized_word(country[1][index]):
                    #move the minister to the first place
                    #['Belgium', ['Ms Annemie NEYTS-UTTENBROEK', 'Minister, attached to the Minister for Foreign Affairs, with', 'responsibility for Agriculture', 'Mr Jos\xc3\xa9 HAPPART', 'Minister for Agriculture and Rural Affairs (Walloon Region)', 'Ms Vera DUA', 'Minister for the Environment and Agriculture (Flemish Region)']]
                    country[1].insert(0, country[1].pop(index))
                    nb_pbs[0]+=1
                    nb_pbs[1]+=country[0]+ ";"
                    break
#~
    #~ print 'NB DIFFS', nb_pbs
    #~ print ""
    #~ print "countries AFTER moving ministers", countries
    #~ print ""


    #remove ministers' names and group long verbatims split into more than one item
    for country in countries:
        #~ print "country", country
        for minister in country[1]:
            #new minister for the country
            if minister.lstrip()[:2].lower() in ["mr", "ms"] or capitalized_word(minister):
                #~ print "mr ms", minister
                verbatims.append([country[0], ""])
            else:
                #~ print "verbatim", minister
                #for long verbatims in 2 or more lines
                #~ print "verbatims", verbatims
                if verbatims[-1][1]=="":
                    separator=""
                else:
                    separator=" "
                verbatims[-1][1]+=separator+minister
            #~ print "verbatims", verbatims
        #~ break

    #~ print "no more ministers' names"
    #~ print verbatims
    #~ print ""

    #remove extra blank spaces
    for country in verbatims:
        country[1]=' '.join(country[1].split())


    #display final result
    for country in verbatims:
        print country[0]+": "+country[1]
    print ""
    print "nb different countries", len(countries)
    print "nb countries", len(verbatims)
    print ""
    return verbatims




class Command(NoArgsCommand):
    """
    for each act, get the pdf of the ministers' attendance, extract the relevant information and import it into ImportMinAttend
    run the command from a terminal: python manage.py attendance.pdf
    """

    def handle(self, **options):

        nb_pbs=0
        urls={}
        #get the list of countries from the db
        country_list=Country.objects.values_list('country', flat=True)

        #delete not validated acts
        #~ ImportMinAttend.objects.filter(validated=False).delete()

        #~ #get all the acts with a non null attendance_path and attendances not yet validated
        acts_ids=ActIds.objects.filter(src="index", act__attendance_pdf__isnull=False, act__validated_attendance=0,  act__releve_annee=2013,  act__releve_mois=6)
        for act_ids in acts_ids:
            ok=False
            act=act_ids.act

#~ #~
            #TEST ONLY
            #~ act.attendance_pdf="http://www.consilium.europa.eu/uedocs/cms_data/docs/pressdata/en/intm/110310.pdf"
#~ #~
            print ""
            print "act", act
            print act.attendance_pdf
            print ""
            
            #new attendance pdf document?
            if act_ids.act.attendance_pdf not in urls:
                
                #~ #get the pdf
                try:
                    file_object = urllib2.urlopen(act.attendance_pdf)
                except Exception, e:
                    #wait a few seconds
                    print e
                    print ""
                    time.sleep(3)
                    file_object = urllib2.urlopen(act.attendance_pdf)

                #read the pdf and assign its text to a string
                string=pdf_to_string(file_object)
                participants=get_participants(string)
                readable=False
                for participant in participants:
                    #for some acts in 2002, countries are not read properly
                    if "Belgium" in participant:
                        readable=True
                        break

                if readable:
                    #format the string variable to get the countries and verbatims only
                    #~ #participants=file_to_string(file_path+file_name+".txt")
                    participants=format_participants(participants, country_list)
                    countries=get_countries(participants, country_list)
                    verbatims=get_verbatims(countries, country_list)
                    
                    urls[act.attendance_pdf]=verbatims
                    ok=True
                else:
                    print "countries not readable"
                    nb_pbs+=1
#~             
            #html page already retrieved
            else:
                verbatims=urls[act.attendance_pdf]
                ok=True
       
                
            #~ #if the verbatims have been extracted
            if ok:
                #remove non validated ministers' attendances
                ImportMinAttend.objects.filter(no_celex=act_ids.no_celex).delete()
    #~ #~
                for country in verbatims:
                    status=None
                    #retrieves the status if the verbatim exists in the dictionary
                    try:
                        verbatim=Verbatim.objects.get(verbatim=country[1])
                        status=Status.objects.get(verbatim=verbatim, country=Country.objects.get(country=country[0])).status
                    except Exception, e:
                        pass
                        #print "no verbatim", e
    #~ #~
                    #add extracted attendances into ImportMinAttend
                    try:
                        ImportMinAttend.objects.create(releve_annee=act.releve_annee, releve_mois=act.releve_mois, no_ordre=act.no_ordre, no_celex=act_ids.no_celex, country=Country.objects.get(country=country[0]).country_code, verbatim=country[1], status=status)
                    except IntegrityError as e:
                        pass
                        #print "integrity error", e
                    
                #validate attendance in act table
                #~ act.validated_attendance=1
                #~ act.save()
        #~ #~
                #TEST ONLY
                #~ break

                print ""

        print "nb_pbs", nb_pbs
