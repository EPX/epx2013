from django import forms
from import_app.models import ImportMinAttend
from act.models import Country, Status
#variables names
import act.var_name_data as var_name_data
from django.forms.util import ErrorList
from django.core.exceptions import ValidationError, ObjectDoesNotExist


class ImportMinAttendForm(forms.ModelForm):
    """
    FORM
    form to validate the ministers' attendance
    """
    country=forms.ModelChoiceField(queryset=Country.objects.all(), empty_label="Select a country")
    status=forms.ModelChoiceField(queryset=Status.objects.values_list('status', flat = True).distinct(), empty_label="Select a status")

    class Meta:
        model=ImportMinAttend
        #fields used for the validation and order
        fields = ('country', 'status', 'verbatim')


    def clean(self):
        #call status clean method
        self.cleaned_data["status"]=self.clean_status()
        return self.cleaned_data

    def clean_country(self):
        #avoid validation error
        country = self.cleaned_data['country'].pk
        return country

    def clean_verbatim(self):
        #remove extra blank spaces
        verbatim = self.cleaned_data['verbatim']
        return ' '.join(verbatim.split())

    def clean_status(self):
        #valid if a value has been selected
        if self["status"].value()!="":
            del self._errors["status"]
        return self["status"].value()

    def save(self, *args, **kwargs):
        #if extra forms, add ids
        if "no_celex" in kwargs:
            self.instance.no_celex = kwargs.pop('no_celex', None)
            self.instance.releve_annee = kwargs.pop('releve_annee', None)
            self.instance.releve_mois = kwargs.pop('releve_mois', None)
            self.instance.no_ordre = kwargs.pop('no_ordre', None)
        instance = super(ImportMinAttendForm, self).save(*args, **kwargs)
        #when saving from the attendance form validation, validated=True
        instance.validated = True
        instance.save()
        return instance


def format_releve_ids(releves):
    releves=releves.split(",")
    releve_annee=var_name_data.var_name['releve_annee'] + "=" + releves[0]
    releve_mois=var_name_data.var_name['releve_mois'] + "=" + releves[1]
    no_ordre=var_name_data.var_name['no_ordre'] + "=" + releves[2]
    return releve_annee + ", " + releve_mois + ", " + no_ordre


class Add(forms.Form):
    """
    FORM
    details the Add form (fields for the add mode of MinAttendForm)
    """
    act_to_validate=forms.ChoiceField()

    #no duplicate in the drop down list
    def __init__(self, *args, **kwargs):
        super(Add, self).__init__(*args, **kwargs)

        #create list of different acts to validate
        acts_list=[]
        qs=ImportMinAttend.objects.filter(validated=0).order_by("releve_annee", "releve_mois", "no_ordre")
        for act in qs:
            name=str(act.releve_annee)+","+str(act.releve_mois)+","+str(act.no_ordre)
            if name not in acts_list:
                acts_list.append(name)
        #add name to be displayed in the form to have a list of tuples
        for index in range(len(acts_list)):
            acts_list[index]=(acts_list[index], format_releve_ids(acts_list[index]))

        #empty label
        acts_list=[('','Select an act to validate')] + acts_list

        #assign the choices to the drop down list
        self.fields['act_to_validate'].choices = acts_list



class Modif(forms.Form):
    """
    FORM
    details the Modif form (fields for the modification mode of MinAttendForm)
    """
    #ids input boxes used for the modification
    releve_annee_modif=forms.IntegerField(label=var_name_data.var_name['releve_annee'], min_value=1957, max_value=2020)
    releve_mois_modif=forms.IntegerField(label=var_name_data.var_name['releve_mois'], min_value=1, max_value=12)
    no_ordre_modif=forms.IntegerField(label=var_name_data.var_name['no_ordre'], min_value=1, max_value=99)

    #check if the searched act already exists in the db and has been validated
    def is_valid(self):
        print "is valid"
        # run the parent validation first
        valid=super(Modif, self).is_valid()

        # we're done now if not valid
        if not valid:
            return valid

        #if the form is valid
        releve_annee_modif=self.cleaned_data.get("releve_annee_modif")
        releve_mois_modif=self.cleaned_data.get("releve_mois_modif")
        no_ordre_modif=self.cleaned_data.get("no_ordre_modif")

        try:
            #~ print ImportMinAttend.objects.get(releve_annee=releve_annee_modif, releve_mois=releve_mois_modif, no_ordre=no_ordre_modif, validated=True).query
            act=ImportMinAttend.objects.get(releve_annee=releve_annee_modif, releve_mois=releve_mois_modif, no_ordre=no_ordre_modif, validated=True)
        except ObjectDoesNotExist, e:
            #~ print "pb find act", e
            self._errors['__all__']=ErrorList([u"The act you are looking for has not been validated yet!"])
            return False
        except Exception, e:
            print "more than one rows: OK", e

        # form valid -> return True
        return True
