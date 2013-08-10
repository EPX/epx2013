# -*- coding: utf-8 -*-
"""
get the information from gvtCompo
"""
from actsInformationRetrieval.models import GvtCompoModel


def getAssocVariables(act):
	"""
	FUNCTION
	get all the nationGvtPoliticalComposition from an act object
	PARAMETERS
	act: instance of an act (ActsInformationModel)
	RETURN
	prelexNationGvtPoliticalComposition (ActsInformationModel)
	"""
	gvt_compo=""
	for gvtCompo in act.prelexNationGvtPoliticalComposition.all():
		gvt_compo+=gvtCompo.nationGvtPoliticalComposition+"; "
	#delete last "; "
	gvt_compo=gvt_compo[:-2]
	return gvt_compo


def linkActInfoToGvtCompo(act):
	"""
	FUNCTION
	fill the assocation table which links an act to its governments composition
	PARAMETERS
	act: instance of an act (ActsInformationModel)
	RETURN
	True if matching data were saved in the association, False otherwise
	"""
	#we retrieve all the rows from GvtCompoModel for which startDate<adoptionConseil<endDate
	gvtCompos=GvtCompoModel.objects.filter(startDate__lte=act.prelexAdoptionConseil, endDate__gte=act.prelexAdoptionConseil)
	#fill the association
	for gvtCompo in gvtCompos:
		act.prelexNationGvtPoliticalComposition.add(gvtCompo)

	if gvtCompos:
		return True
	return False


def getGvtCompo(act):
	"""
	FUNCTION
	get nationGvtPoliticalComposition (GvtCompoModel)
	PARAMETERS
	act: instance of an act (ActsInformationModel)
	RETURN
	prelexNationGvtPoliticalComposition (ActsInformationModel)
	"""

	nationGvtPoliticalComposition=getAssocVariables(act)
	#no match in the db
	if not nationGvtPoliticalComposition:
		#the government compositions for the current act have not been searched and filled yet
		#let's fill the association
		if linkActInfoToGvtCompo(act)==True:
			#if there is at least one matching row
			return getAssocVariables(act)
		else:
			return None
	else:
		return nationGvtPoliticalComposition

	return None



def getGvtCompoInfo(act):
	"""
	FUNCTION
	returns GvtCompoModel data matching the current act
	PARAMETERS
	act: instance of the act
	RETURN
	gvtCompo data
	"""
	#TEST ONLY -> TO REMOVE
	#~ act.prelexAdoptionConseil="2012-02-21"

	gvt_compo=getGvtCompo(act)
	print "prelexNationGvtPoliticalComposition", gvt_compo

	return gvt_compo