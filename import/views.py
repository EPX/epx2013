#-*- coding: utf-8 -*-
import csv
from django.conf import settings
from django.db import IntegrityError
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from forms import CsvUploadForm
from models import CsvUploadModel, DosIdModel
from actsIdsValidation.models import ActsIdsModel
from datetime import date
import os

#cross validation functions and get information from eurlex, oeil, prelex
import getIdsFunctions as info


def saveDosIds(csvFile):
	"""
	FUNCTION
	open a csv file and save prelex unique ids (dosId) in the database
	PARAMETERS
	csvFile: file to handle
	RETURN
	list of prelex unique ids (dosId) saved and list of dosId not saved
	"""
	errorList=[]
	idsList=[]
	f = open(csvFile, 'r')  
	reader=csv.reader(f,delimiter=',')
	header=reader.next()
	
	for row in reader:
		if row[0].strip() !="":
			dosId = DosIdModel()
			dosId.dosId=int(row[0])
			dosId.proposOrigine=row[1].strip()
			dosId.proposAnnee=int(row[2])
			dosId.proposChrono=row[3].strip()
			dosId.splitNumber=emptyOrVar(row[4], "int")
			
			try:
				dosId.save()
				idsList.append(dosId.dosId)
			except IntegrityError, e:
				error= "The dosId " + str(dosId.dosId) + " ALREADY EXISTS!!"
				errorList.append(error)
				print "error", error
		else:
			#end of file
			break
			
	f.close() 
	return idsList, errorList

def emptyOrVar(var, varType):
	"""
	FUNCTION
	returns the variable of None if it contains no value
	PARAMETERS
	var: variable to test
	varType: type of the variable (string, int)
	RETURN
	variable or None
	"""
	returnValue=None
	if varType=="str":
		if var.strip()!="NULL" and var.strip()!="":
			#~ print "not null str"
			returnValue=var
	elif varType=="int":
		try: 
			int(var)
			#~ print "not null int"
			returnValue=var
		except:
			#~ print "not int"
			pass
	
	return returnValue

def saveActsToValidate(csvFile):
	"""
	FUNCTION
	open a csv file and save its acts in the database
	PARAMETERS
	csvFile: file to handle
	RETURN
	list of act ids (releve*) saved and list of act ids not saved
	"""
	errorList=[]
	idsList=[]
	f = open(csvFile, 'r')  
	reader=csv.reader(f,delimiter=',')
	header=reader.next()
	
	for row in reader:   
		#act is not taken into account when noUniqueType=CS (it's not a definitive act)
		if (row[12].strip())!="CS" and row[7].strip()!="":
			actsIds = ActsIdsModel()
			actsIds.releveAnnee=int(row[0])
			actsIds.releveMois=int(row[1])
			actsIds.noOrdre=int(row[2])
			actsIds.titreRMC=row[3].strip()
			actsIds.adopCSRegleVote=row[4].strip()
			actsIds.adopCSAbs=row[5].strip()
			actsIds.adoptCSContre=row[6].strip()
			actsIds.fileNoCelex=row[7].strip()
			actsIds.fileProposAnnee=emptyOrVar(row[8], "int")
			actsIds.fileProposChrono=emptyOrVar(row[9].replace(" ", ""), "str")
			actsIds.fileProposOrigine=emptyOrVar(row[10], "str")
			actsIds.fileNoUniqueAnnee=emptyOrVar(row[11], "int")
			actsIds.fileNoUniqueType=emptyOrVar(row[12], "str")
			actsIds.fileNoUniqueChrono=emptyOrVar(row[13], "str")
			if row[14].strip()=="Y":
				actsIds.proposSplittee=True
			if row[15].strip()=="Y":
				actsIds.suite2eLecturePE=True
			actsIds.councilPath=row[16].strip()
			if actsIds.councilPath!="" and actsIds.councilPath[-1]==".":
				actsIds.councilPath=actsIds.councilPath[:-1]
			#we don't take the council path column
			actsIds.notes=row[17].strip()
			
			#we save fileDosId from the dosIdModel model
			#if splitted proposition
			if len(actsIds.fileProposChrono)>2 and actsIds.fileProposChrono[-2]=="-":
				newFileProposChrono=actsIds.fileProposChrono[:-2]
				newSplitNumber=actsIds.fileProposChrono[-1]
				try:
					fileDosId=DosIdModel.objects.get(proposOrigine=actsIds.fileProposOrigine, proposAnnee=actsIds.fileProposAnnee, proposChrono=newFileProposChrono, splitNumber=newSplitNumber)
					actsIds.fileDosId=fileDosId.dosId
				except Exception, e1:
					actsIds.fileDosId=None
					print e1
			else:
				try:
					fileDosId=DosIdModel.objects.get(proposOrigine=actsIds.fileProposOrigine, proposAnnee=actsIds.fileProposAnnee, proposChrono=actsIds.fileProposChrono)
					actsIds.fileDosId=fileDosId.dosId
				except Exception, e2:
					actsIds.fileDosId=None
					print e2
					
			try:
				actsIds.save()
				idsList.append((actsIds.releveAnnee, actsIds.releveMois, actsIds.noOrdre))
			except IntegrityError, e:
				error= "The act releveAnnee="+str(actsIds.releveAnnee)+ " releveMois="+str(actsIds.releveMois)+ " noOrdre="+str(actsIds.noOrdre) + " ALREADY EXISTS!!"
				errorList.append(error)
				print e
				
				
			#save only one act -> TESTS
			#~ break

	f.close() 
	return idsList, errorList


def saveRetrievedIds(idsList):
	"""
	FUNCTION
	save retrieved ids from eurlex, oeil and prelex in the the database
	PARAMETERS
	idsList: list of act ids to save (monthly summary ids)
	RETURN
	no
	"""
	dataDic={}
	for ids in idsList:
		releveAnneeVar=ids[0]
		releveMoisVar=ids[1]
		noOrdreVar=ids[2]
		act=ActsIdsModel.objects.get(releveAnnee=releveAnneeVar,releveMois=releveMoisVar,noOrdre=noOrdreVar)
		
		#get ids
		#eurlex
		dataDic=info.checkAndGetEurlexIds(str(act.fileNoCelex))
		#oeil
		dataDic.update(info.checkAndGetOeilIds(str(act.fileNoUniqueType), str(act.fileNoUniqueAnnee), str(act.fileNoUniqueChrono)))
		#prelex
		idsDic={}
		#try with dosId
		if act.fileDosId!=None:
			idsDic['dosId']=str(act.fileDosId)
		#splitted proposition?
		elif len(act.fileProposChrono)>2 and act.fileProposChrono[-2]=="-":
			#try with the oeil ids
			idsDic['noUniqueType']=str(act.fileNoUniqueType)
			idsDic['noUniqueAnnee']=str(act.fileNoUniqueAnnee)
			idsDic['noUniqueChrono']=str(act.fileNoUniqueChrono)
		else:
			#prelex ids
			idsDic['proposOrigine']=str(act.fileProposOrigine)
			idsDic['proposAnnee']=str(act.fileProposAnnee)
			idsDic['proposChrono']=str(act.fileProposChrono)
		
		dataDic.update(info.checkAndGetPrelexIds(idsDic))
		
		#~ print dataDic
		
		#save retrieved ids
		act.eurlexNoCelex=dataDic['eurlexNoCelex']
		act.oeilNoCelex=dataDic['oeilNoCelex']
		act.prelexNosCelex=dataDic['prelexNosCelex']
		act.fileEurlexUrlExists=dataDic['eurlexEurlexUrlExists']
		
		act.eurlexProposAnnee=dataDic['eurlexProposAnnee']
		act.oeilProposAnnee=dataDic['oeilProposAnnee']
		act.prelexProposAnnee=dataDic['prelexProposAnnee']
		act.eurlexProposChrono=dataDic['eurlexProposChrono']
		act.oeilProposChrono=dataDic['oeilProposChrono']
		act.prelexProposChrono=dataDic['prelexProposChrono']
		act.eurlexProposOrigine=dataDic['eurlexProposOrigine']
		act.oeilProposOrigine=dataDic['oeilProposOrigine']
		act.prelexProposOrigine=dataDic['prelexProposOrigine']
		act.filePrelexUrlExists=dataDic['prelexPrelexUrlExists']
		act.prelexUrl=dataDic['prelexPrelexUrl']
		
		act.prelexDosId=dataDic['prelexDosId']
		act.eurlexNoUniqueAnnee=dataDic['eurlexNoUniqueAnnee']
		act.oeilNoUniqueAnnee=dataDic['oeilNoUniqueAnnee']
		act.prelexNoUniqueAnnee=dataDic['prelexNoUniqueAnnee']
		act.eurlexNoUniqueType=dataDic['eurlexNoUniqueType']
		act.oeilNoUniqueType=dataDic['oeilNoUniqueType']
		act.prelexNoUniqueType=dataDic['prelexNoUniqueType']
		act.eurlexNoUniqueChrono=dataDic['eurlexNoUniqueChrono']
		act.oeilNoUniqueChrono=dataDic['oeilNoUniqueChrono']
		act.prelexNoUniqueChrono=dataDic['prelexNoUniqueChrono']
		act.fileOeilUrlExists=dataDic['oeilOeilUrlExists']
		
		
		try:
			act.save()
			print "act", releveAnneeVar, releveMoisVar, noOrdreVar,"saved"
		except IntegrityError, e:
			print e


def importView(request):
	"""
	VIEW
	displays and processes the import page
	template called: import/index.html
	"""
	responseDic={}
	if request.method == 'POST':
		form = CsvUploadForm(request.POST, request.FILES)
		responseDic['form']=form
		#the form is valid and the import can be processed
		if form.is_valid():
			print "csv import"
			fileToImport=form.cleaned_data['fileToImport']
			newFilename=" ".join(request.FILES['csvFile'].name.split())
			path = settings.MEDIA_ROOT+"import/"+newFilename
			#if a file with the same name already exists, we delete it
			if os.path.exists(path):
				os.remove(path)
			newCsvFile = CsvUploadModel(csvFile = request.FILES['csvFile'])
			newCsvFile.save()
			idsList=[]
			errorList=[]
				
			#importation of prelex unique ids (dosId)
			#delete FROM europolix.actsIdsValidation_dosidmodel;
			if fileToImport=="dosId":
				#save csv file
				idsList, errorList= saveDosIds(path)
				responseDic['errorList']=errorList
				responseDic['success']=str(len(idsList)) + " prelex unique ids (dosId) imported, "+ str(len(errorList)) +" error(s)!"
			#importation of acts to validate
			elif fileToImport=="act":
				#save csv file
				idsList, errorList= saveActsToValidate(path)
				responseDic['errorList']=errorList
				responseDic['success']=str(len(idsList)) + " act(s) imported, "+ str(len(errorList)) +" error(s)!"
				#save retrieved ids
				saveRetrievedIds(idsList)
				
	else:
		responseDic['form']=CsvUploadForm()

	return render_to_response('import/index.html', responseDic, context_instance=RequestContext(request))