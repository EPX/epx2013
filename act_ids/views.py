#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from act_ids.forms import ActIdsForm, ActForm, Add, Modif
from act_ids.models import ActIds
from act.models import Act
from history.models import History
from import_app.models import ImportDosId, ImportMinAttend
from common.db import save_get_object, get_act_ids
from common.views import check_add_modif_forms, get_ajax_errors
#variables name
import act_ids.var_name_ids as var_name_ids
import act.var_name_data as var_name_data
#used to recreate and display the urls
import sys
from django.conf import settings
import import_app.get_ids_eurlex as eurlex
import import_app.get_ids_oeil as oeil
from import_app.views import get_save_act_ids
#redirect to login page if not logged
from django.contrib.auth.decorators import login_required
#use json for the ajax request
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import simplejson
#log
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


def check_equality_fields(fields):
    """
    FUNCTION
    check if fields of a list are all equal
    PARAMETERS
    fields: fields to check [list of strings]
    RETURN
    true if all the fields are equal, false otherwise [boolean]
    """
    for field in fields[1:]:
        if fields[0]!=field:
            return False
    return True


@login_required
def act_ids(request):
    """
    VIEW
    displays and processes the Act ids validation page
    TEMPLATES
    act_ids/index.html: display the act ids page which itself calls the template of the act_ids form
    act_ids/form.html: display the act_ids form
    """
    response={}
    #display "real" name of variables (not the ones stored in db)
    response['display_name']=var_name_ids.var_name
    response['display_name'].update(var_name_data.var_name)
    #state=display (display the ids of an act), saved (the act is being saved) or ongoing (validation errors while saving)
    state="display"
    #html page of the form
    form_template='act_ids/form.html'

    if request.method=='POST':
        #mode: "add" if selection of an act to add from the drop down list, "modif" if click on the modif_act button and None otherwise
        #add_modif: same than mode but return None if the add or modif form is not valid
        #act=act to validate / modify or None if no act is found (modifcation)
        #response: add add or modif to the forms being displayed / to be displayed
        mode, add_modif, act, response=check_add_modif_forms(request, response, Add, Modif, "act_ids")

        #if any of this key is present in the response dictionary -> no act display and return the errors with a json object
        #otherwise display act and return the html form of the act to validate or update in a string format
        keys=["msg", "add_act_errors", "modif_act_errors", "update_act_errors"]

        #if selection of an act in the drop down list or click on the modif_act button
        if mode!=None:
            #~ #if we are about to add or modif an act (the add or modif form is valid)
            if add_modif!=None:

                act_ids=ActIds.objects.get(act=act, src="index")
                form_ids=ActIdsForm(request.POST, instance=act_ids)
                #just for the notes field
                form_data=ActForm(request.POST, instance=act)

                #saves the act
                if 'save_act' in request.POST:
                    print "save"
                    if form_ids.is_valid():
                        print "form_ids valid"
                        #save the ids of the act in ActIds
                        form_ids.save()
                        #save notes and validate the act
                        act.notes=request.POST['notes']
                        if act.validated==0:
                            act.validated=1
                        act.save()
                        state="saved"
                        #success message (calls unicode method)
                        response["msg"]="The act " + str(act) + " has been validated!"
                        response["msg_class"]="success_msg"

                        #save in history
                        History.objects.create(action=add_modif, form="ids", act=act, user=request.user)
                    else:
                        print "form_ids not valid", form_ids.errors
                        if request.is_ajax():
                            response['save_act_errors']= get_ajax_errors(form_ids)
                        else:
                            response['form_ids']=form_ids
                        response["msg"]="The form contains errors! Please correct them before submitting again."
                        response["msg_class"]="error_msg"
                        state="ongoing"

                #if click on the actualisation button
                elif 'update_act' in request.POST:
                    print "update"
                    state="update"
                    #news ids must be saved in the database
                    if form_ids.is_valid():
                        print "update: form_ids valid"
                        form_ids.save()
                        #we retrieve and save the new ids (from the new urls)
                        ids_row={}
                        ids_row["releve_annee"]=act.releve_annee
                        ids_row["releve_mois"]=act.releve_mois
                        ids_row["no_ordre"]=act.no_ordre
                        #actualisation button -> use acts ids retrieval from the import module
                        get_save_act_ids([ids_row])
                        #get the updated instance of the act
                        act=Act.objects.get(id=act.id)
                    else:
                        print "form_ids not valid", form_ids.errors
                        if request.is_ajax():
                            response['update_act_errors']= get_ajax_errors(form_ids)
                        else:
                            response['form_ids']=form_ids

                #displays the ids of an act to validate
                #selection of an act in the add / modif form or update of an act with no form error
                #if javasxript deactivated, also display act ids if click on save button and errors in form_ids
                if not any(key in response for key in keys) or not request.is_ajax() and state!="saved":
                    print 'act_to_validate display'
                    
                    #an act has been selected in the drop down list -> the related data are displayed
                    if state=="display":
                        #the default value of the dos_id drop down list is the validated dos_id if any
                        init=None
                        if act_ids.dos_id!=None:
                            init=act_ids.dos_id
                        form_ids=ActIdsForm(instance=act_ids, initial ={'dos_id_choices': init})
                        form_data=ActForm(instance=act)
                    #otherwise use POST too (done before)

                    data={}
                    #retrieve the act ids instance for each source
                    act_ids=get_act_ids(act)

                    fields=["no_celex", "propos_annee", "propos_chrono", "propos_origine", "no_unique_annee", "no_unique_type", "no_unique_chrono"]

                    #check if the corresponding data are equal -> they will appear in red if not
                    for field in fields:
                        param=[]
                        for src in ["index", "eurlex", "oeil"]:
                            param.append(getattr(act_ids[src], field))
                        data[field]=check_equality_fields(param)

                    #check dos_id
                    data["dos_id"]=False
                    if act_ids["eurlex"].dos_id!=None:
                        #if there is a validated dos_id, do the comparison with that one
                        if act_ids["index"].dos_id!=None:
                            data["dos_id"]=check_equality_fields([act_ids["index"].dos_id, act_ids["eurlex"].dos_id])
                        else:
                            #otherwise search for the dos_id from the ImportDosId model matching the no_celex
                            try:
                                ImportDosId.objects.get(dos_id=act_ids["eurlex"].dos_id, no_celex=act_ids["index"].no_celex)
                                data["dos_id"]=True
                            except Exception, e:
                                print "no matching dos_id", e

                    #get urls
                    data["url_eurlex"]=eurlex.get_url_eurlex(act_ids["index"].no_celex, "HIS")
                    data["url_oeil"]=oeil.get_url_oeil(str(act_ids["index"].no_unique_type), str(act_ids["index"].no_unique_annee), str(act_ids["index"].no_unique_chrono))

                    response['form_ids']=form_ids
                    response['form_data']=form_data
                    response['act']=act
                    response['act_ids']=act_ids
                    response['data']=data
                    response['add_modif']=add_modif

                response['mode']=mode

            if request.is_ajax():
                #save act (with or without errors) or act display, modif and update (with errors)
                if any(key in response for key in keys):
                    return HttpResponse(simplejson.dumps(response), mimetype="application/json")
                else:
                    #act display, modif or update (without errors)
                    return HttpResponse(render_to_string(form_template, response, RequestContext(request)))

        if request.is_ajax():
            #no act has been selected-> do nothing
            return HttpResponse(simplejson.dumps(""), mimetype="application/json")


    #unbound forms
    forms=[("form_ids", ActIdsForm()), ("form_data", ActForm()), ("add", Add()), ("modif", Modif())]
    for form in forms:
        if form[0] not in response  or state=="saved":
            response[form[0]]=form[1]

    response['form_template']=form_template

    #displays the page (GET) or POST if javascript disabled
    return render_to_response('act_ids/index.html', response, context_instance=RequestContext(request))


def reset_ids_form(request):
    """
    VIEW
    reset the act_ids form (except add and modif forms)
    TEMPLATES
    act_ids/form.html
    """
    response={}
    #display "real" name of variables (not the one stored in db)
    response['display_name']=var_name_ids.var_name
    response['form_ids']=ActIdsForm()
    response['form_data']=ActForm()
    return render_to_response('act_ids/form.html', response, context_instance=RequestContext(request))
