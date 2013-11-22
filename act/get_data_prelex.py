#-*- coding: utf-8 -*-
#for accents between comments inside this file
"""
get data from Prelex (fields for the statistical analysis)
"""
import re
from bs4 import BeautifulSoup
#models
from act.models import DG, DGNb, Person, CodeSect, GvtCompo, PartyFamily
from import_app.views import save_adopt_cs_pc
from import_app.models import ImportAdoptPC
#model as parameter
from django.db.models.loading import get_model
#remove accents
from common.functions import remove_nonspacing_marks, date_string_to_iso, list_reverse_enum
from datetime import datetime
#save resp
from common.db import save_get_field_and_fk, save_get_object, save_fk_code_sect


def get_adopt_com_table(soup):
	"""
	FUNCTION
	get the html content of the table tag "Adoption by Commission" from the prelex url
	PARAMETERS
	soup: prelex url content [BeautifulSoup object]
	RETURN
	html content of the table "Adoption by Commission" [BeautifulSoup object]
	"""
	try:
		return soup.find("b", text=re.compile("Adoption by Commission")).find_parent('table')
	except:
		print "no table called 'Adoption by Commission' (prelex)"
		return None


def get_adopt_propos_origine(soup, propos_origine):
	"""
	FUNCTION
	get the adopt_propos_origine variable from the prelex url
	PARAMETERS
	soup: prelex url content [BeautifulSoup object]
	propos_origine: propos_origine variable [string]
	RETURN
	adopt_propos_origine: adopt_propos_origine variable [date]
	"""
	adopt_propos_origine=None
	try:
		if propos_origine=="COM":
			adopt_propos_origine=soup.find("a", text=re.compile("Adoption by Commission")).find_next('br').next.strip()
		elif propos_origine=="JAI":
			adopt_propos_origine=get_transm_council(soup, propos_origine)
		elif propos_origine=="CONS":
			print "TODO: extraction pdf almost done (see tests)"

		#transform dates to the iso format (YYYY-MM-DD)
		if adopt_propos_origine!=None:
			adopt_propos_origine=date_string_to_iso(adopt_propos_origine)
	except:
		print "no adopt_propos_origine!"

	return adopt_propos_origine

#~ Date in front of "Adoption by Commission"
#~ not NULL
#~ AAAA-MM-JJ format
#~ ProposOrigine=COM -> date adoption de la proposition par la Commission
#~ ProposOrigine=JAI -> TransmissionConseil date
#~ EM -> not processed because appears only when no_unique_type=CS which concerns non definitive acts (not processed)
#~ ProposOrigine=CONS -> date in pdf document (council path link)


def get_com_proc(soup, propos_origine):
	"""
	FUNCTION
	get the com_proc variable from the prelex url
	PARAMETERS
	soup: prelex url content [BeautifulSoup object]
	propos_origine: propos_origine variable [string]
	RETURN
	com_proc variable [string]
	"""
	try:
		if propos_origine=="COM":
			return soup.find("td", text="Decision mode:").find_next('td').get_text().strip()
	except:
		print "no com_proc!"
	return None

#~ in front of "Decision mode"
#~ Possible values:
#~ "Oral Procedure", "Written Procedure", "Empowerment procedure"
#~ Null if ProposOrigine !=COM


def save_get_resp(names):
	"""
	FUNCTION
	save the name in the db and get the instance
	PARAMETERS
	names: full name of the person [string]
	RETURN
	instance: instance of Person [Person model instance]
	"""
	#remove trailing "'"
	if names[-1]=="'":
		names=names[:-1]
	#remove accents
	names=remove_nonspacing_marks(names)
	#change name format: "Firstname LASTNAME" -> "LASTNAME Firstname"
	names=names.split()
	first_name=last_name=""
	#get first names
	for name in names:
		#get last names
		if name.isupper():
			last_name+=name+" "
		#get first names
		else:
			first_name+=name+" "

	names=last_name[:-1]+" "+first_name[:-1]
	print "name", names

	field=[Person, "name", names]
	src="resp"
	instance=save_get_field_and_fk(field, [], src)[0]

	return instance


def get_jointly_resps(soup):
	"""
	FUNCTION
	get the names of the jointly responsible persons (dg_2 and resp_2 or resp_3 from the prelex url
	PARAMETERS
	soup: prelex url content [BeautifulSoup object]
	RETURN
	names of jointly responsible persons (dg_2 and resp_2 or resp_3 ) [list of strings]
	"""
	dg_2=resp_2=None
	try:
		#~ http://ec.europa.eu/prelex/detail_dossier_real.cfm?CL=en&DosId=191926
		jointly_resps=soup.find_all("td", text="Jointly responsible")
		#dg_2
		dg_2=jointly_resps[0].find_next('td').get_text().strip()
		#resp_2 or 3
		resp_2=jointly_resps[1].find_next('td').get_text()

	except:
		print "no dg_2 or resp_2"

	return dg_2, resp_2

#in front of "Jointly responsible"
#can be Null


def get_dg_1(soup):
	"""
	FUNCTION
	get the dg_1 variable from the prelex url
	PARAMETERS
	soup: prelex url content [BeautifulSoup object]
	RETURN
	dg_1 variable [string]
	"""
	try:
		#dg
		dg_1=soup.find("td", text="Primarily responsible").find_next('td').get_text().strip()
		if dg_1!="":
			return dg_1
	except:
		pass
	return None

#~ in front of "Primarily responsible"
#can be Null


def save_get_dgs(dgs):
	"""
	FUNCTION
	get the dg instances associated to each dg passed in parameter
	PARAMETERS
	dgs: list of dgs [list of strings]
	RETURN
	dgs_instances: list of dg instances [list of DG model instances]
	"""
	dgs_instances=[]
	for dg in dgs:
		instance=None
		if dg!=None:
			#if it is a dg_nb, it can refer to more than one DG (manual validation)
			if dg[-1].isdigit():
				try:
					dg_nb=DGNb.objects.get(dg_nb=dg)
					#only one dg one many possible dgs?
					try:
						instance=DG.objects.get(dg_nb=dg_nb)
					except Exception, e:
						print "many possible dgs", e
						instance=DG.objects.filter(dg_nb=dg_nb)
				except Exception, e:
					print "save_get_dgs exception", e
					instance=None
			#it is a dg
			else:
				instance=save_get_object(DG, {"dg": dg})

		dgs_instances.append(instance)

	return dgs_instances


def get_resps(soup):
	"""
	FUNCTION
	get the responsible names from the prelex url (resp_1, resp_2, resp_3)
	PARAMETERS
	soup: prelex url content [BeautifulSoup object]
	RETURN
	resps: resp_* names [list of strings]
	"""
	resps=None
	try:
		resps=soup.find("td", text="Responsible").find_next('td').get_text()
		resps=resps.split(";")
	except Exception, e:
		print "no responsible", e
	#two responsibles
	#http://ec.europa.eu/prelex/detail_dossier_real.cfm?CL=en&DosId=191554
	return resps

#~ in front of "Responsible"
#can be Null


def get_resp_objs(resps):
	"""
	FUNCTION
	get the responsible objects from the responsible names
	PARAMETERS
	resps: list of responsible names [list of strings]
	RETURN
	persons: resp_* variables [list of Person model instances]
	"""
	persons=[None for i in range(3)]
	try:
		for index in xrange(len(persons)):
			persons[index]=save_get_resp(resps[index].strip())
	except Exception, e:
		print "exception", e
	return persons


def get_transm_council(soup, propos_origine):
	"""
	FUNCTION
	get the transm_council variable from the prelex url
	PARAMETERS
	soup: prelex url content [BeautifulSoup object]
	propos_origine: propos_origine variable [string]
	RETURN
	transm_council: transm_council variable [date]
	"""
	transm_council=None
	try:
		if propos_origine=="CONS":
			transm_council=get_adopt_propos_origine(soup, propos_origine)
		else:
			transm_council=soup.find("a", text=re.compile("Transmission to Council")).find_next('br').next.strip()
	except:
		print "pb transm_council"

	#transform dates to the iso format (YYYY-MM-DD)
	if transm_council!=None:
		transm_council=date_string_to_iso(transm_council)
	return transm_council

#date in front of "Transmission to Council"
#not Null (except blank page -> error on page)
#AAAA-MM-JJ format
#ProposOrigine=CONS -> AdoptionProposOrigine


def get_nb_point_b(soup, propos_origine):
	"""
	FUNCTION
	get the nb_point_b variable from the prelex url
	PARAMETERS
	soup: prelex url content [BeautifulSoup object]
	propos_origine: propos_origine variable [string]
	RETURN
	nb_point_b: nb_point_b variable [int]
	"""
	nb_point_b=None
	try:
		if propos_origine!="CONS" and propos_origine!="BCE":
			nb_point_b= len(soup.find_all(text=re.compile('ITEM "B"')))
	except:
		print "no nb_point_b!"

	return nb_point_b

#~ in front of "COUNCIL AGENDA": counts the number of 'ITEM "B"' on the page
#~ not NULL
#~ De 0 a 20
#~ if propos_origine=="CONS" or "BCE", filled manually


def get_cons_b(soup, propos_origine):
	"""
	FUNCTION
	get the cons_b variable from the prelex url
	PARAMETERS
	soup: prelex url content [BeautifulSoup object]
	propos_origine: propos_origine variable [string]
	RETURN
	cons_b variable [string]
	"""
	cons_b=None
	try:
		if propos_origine!="CONS":
			cons_b_temp=""
			for tables in soup.find_all(text=re.compile('ITEM "B" ON COUNCIL AGENDA')):
				cons_b_temp+=tables.find_parent('table').find(text=re.compile("SUBJECT")).find_next("font", {"size":-2}).get_text().strip()+'; '
			cons_b=cons_b_temp[:-2]
	except:
		print "no nb_point_b!"

	return cons_b

#can be Null
#in front of SUBJECT, only if the act is processed at B point (preceded by 'ITEM "B" ON COUNCIL AGENDA')
#concatenate all the values, even if redundancy
#~ if propos_origine=="CONS", filled manually


def get_adopt_conseil(soup, suite_2e_lecture_pe, split_propos, nb_lectures):
	"""
	FUNCTION
	get the adopt_conseil variable from the prelex url
	PARAMETERS
	soup: prelex url content [BeautifulSoup object]
	suite_2e_lecture_pe: suite_2e_lecture_pe variable [boolean]
	split_propos: split_propos variable [boolean]
	nb_lectures: nb_lectures variable [int]
	RETURN
	adopt_conseil: adopt_conseil variable [date]
	"""
	adopt_conseil=None
	# if there is no  2d Lecture at PE
	if suite_2e_lecture_pe==False:
		acts=["Formal adoption by Council", "Adoption common position", "Council approval 1st rdg"]
		for act in acts:
			try:
				adopt_conseil=soup.find("a", text=re.compile(act)).find_next('br').next.strip()
				break
			except:
				print "pb", act
	# if Suite2LecturePE=Y and split_propos=N
	elif split_propos==False:
		if nb_lectures==2:
			try:
				#~ http://ec.europa.eu/prelex/detail_dossier_real.cfm?CL=en&DosId=156619
				date_table_soup=soup.find("b", text="EP opinion 2nd rdg").find_parent("table")
				#check table contains "Approval without amendment"
				approval=date_table_soup.find(text="Approval without amendment")
				#check next table title is "Signature by EP and Council"
				next_table_title=date_table_soup.find_next("table").find(text="Signature by EP and Council")
				#if conditions are met, then get the date
				adopt_conseil=date_table_soup.find("b").get_text()
			except:
				print "pb AdoptionConseil (case split_propos==0)"
		elif nb_lectures==3:
			#~ http://ec.europa.eu/prelex/detail_dossier_real.cfm?CL=en&DosId=137644
			date_table_soup=soup.find("b", text="Council decision at 3rd rdg").find_parent("table")
			#check next table title is "Signature by EP and Council"
			next_table_title=date_table_soup.find_next("table").find(text="Signature by EP and Council")
			#if conditions are met, then get the date
			adopt_conseil=date_table_soup.find("b").get_text()
			#~ return soup.find("a", text=re.compile("Council decision at 3rd rdg")).find_next('br').next.strip()

	#transform dates to the iso format (YYYY-MM-DD)
	if adopt_conseil!=None:
		adopt_conseil=date_string_to_iso(adopt_conseil)
	return adopt_conseil

#~ date in front of "Formal adoption by Council" or "Adoption common position" or "Council approval 1st rdg"
#not Null
#~ AAAA-MM-JJ format

#~ quand Suite2LecturePE=Y ET quand ProposSplittee=N and nb_lectures=2. Dans ce cas, la date AdoptionConseil=la date qui se trouve en face de la ligne « EP Opinion 2nd rdg » (vérifier qu’à la ligne qui suit dans le même carré, on trouve « Approval without amendment » et que le titre du carré qui suit est bien « Signature by EP and Council »
#~ Exemple : http://ec.europa.eu/prelex/detail_dossier_real.cfm?CL=en&DosId=156619

#~ quand Suite2LecturePE=Y ET quand ProposSplittee=N and nb_lectures=3 -> date in front of Council decision at 3rd rdg (vérifier que le titre du carré qui suit est bien « Signature by EP and Council »)
#~ Example: http://ec.europa.eu/prelex/detail_dossier_real.cfm?CL=en&DosId=137644

# if Suite2LecturePE=Y and split_propos=Y -> to fill manually


def get_nb_point_a(soup, propos_origine):
	"""
	FUNCTION
	get the nb_point_a variable from the prelex url
	PARAMETERS
	soup: prelex url content [BeautifulSoup object]
	propos_origine: propos_origine variable [string]
	RETURN
	nb_point_a: nb_point_a variable [int]
	"""
	nb_point_a=None
	try:
		if propos_origine!="CONS" and propos_origine!="BCE":
			nb_point_a=len(soup.find_all(text=re.compile('ITEM "A"')))
	except:
		print "no nb_point_a!"

	return nb_point_a

#~ in front of "COUNCIL AGENDA": counts the number of 'ITEM "A"' on the page
#~ not NULL
#~ De 0 a 20
#~ if propos_origine=="CONS" or "BCE", filled manually


def get_council_a(soup):
	"""
	FUNCTION
	get the council_a variable from the prelex url
	PARAMETERS
	soup: prelex url content [BeautifulSoup object]
	RETURN
	council_a: council_a variable [string]
	"""
	council_a=None
	try:
		council_a_temp=""
		for tables in soup.find_all(text=re.compile('ITEM "A" ON COUNCIL AGENDA')):
			council_a_temp+=tables.find_parent('table').find(text=re.compile("SUBJECT")).find_next("font", {"size":-2}).get_text().strip()+'; '
		council_a=council_a_temp[:-2]
	except:
		print "no council_a!"

	return council_a

#not Null
#in front of SUBJECT, only if the act is processed at A point (preceded by 'ITEM "A" ON COUNCIL AGENDA')
#concatenate all the values, even if redundancy


def save_config_cons(code_sect_1):
	"""
	FUNCTION
	save the config_cons variable into the CodeSect model
	PARAMETERS
	code_sect_1: code_sect_1 instance [CodeSect model instance]
	RETURN
	None
	"""
	save_fk_code_sect(code_sect_1, "config_cons")


def get_nb_lectures(soup, no_unique_type, split_propos):
	"""
	FUNCTION
	get the nb_lectures variable from the prelex url
	PARAMETERS
	soup: prelex url content [BeautifulSoup object]
	no_unique_type: no_unique_type variable [string]
	split_propos: split_propos variable [boolean]
	RETURN
	nb_lectures variable [int]
	"""
	if no_unique_type!="COD":
		return None

	#proposition not splited
	if split_propos==False:
		if soup.find(text=re.compile('EP opinion 3rd rdg'))>0 or soup.find(text=re.compile('EP decision 3rd rdg'))>0 or soup.find(text=re.compile('EP decision on 3rd rdg'))>0:
			return 3
		if soup.find(text=re.compile('EP opinion 2nd rdg'))>0:
			return 2
		if soup.find(text=re.compile('EP opinion 1st rdg'))>0:
			return 1
		return 0

	#proposition is splited
	if soup.find(text=re.compile('EP: position, 3rd reading'))>0 or soup.find(text=re.compile('EP: decision, 3rd reading'))>0 or soup.find(text=re.compile('EP: legislative resolution, 3rd reading'))>0:
		return 3
	if soup.find(text=re.compile('EP: position, 2nd reading'))>0:
		return 2
	if soup.find(text=re.compile('EP: position, 1st reading'))>0:
		return 1
	return 0

#Possible values
#1, 2, 3 ou NULL
#~ NULL if NoUniqueType !=COD
#~ if NoUniqueType=COD and if the proposition is not splitted:
	#~ if page contains "EP opinion 3rd rdg" or "EP decision 3rd rdg" -> nombreLectures=3
	#~ if page contains "EP opinion 2nd rdg" -> nombreLectures=2
	#~ if page contains "EP opinion 1st rdg" -> nombreLectures=1
	#~ otherwise error
#~ if NoUniqueType=COD and if the proposition is splitted:
	#~ if page contains "EP: position, 3rd reading" or "EP: decision, 3rd reading" or "EP: legislative resolution, 3rd reading" -> nombreLectures=3
	#~ if page contains "EP: position, 2nd reading" -> nombreLectures=2
	#~ if page contains "EP: position, 1st reading" -> nombreLectures=1
	#~ otherwise error


def get_date_diff(date_1, date_2):
	"""
	FUNCTION
	compute the difference between two dates
	PARAMETERS
	date_1: first date [date]
	date_2: second date [date]
	RETURN
	difference between the two dates in parameters  [int]
	"""
	if date_1!=None and date_1!="None" and date_2!=None:
		#transform dates to the iso format (YYYY-MM-DD)
		date_1=datetime.strptime(date_1, "%Y-%m-%d")
		date_2=datetime.strptime(date_2, "%Y-%m-%d")
		return (date_1 - date_2).days
	return None

#DureeAdoptionTrans (TransmissionConseil - AdoptionProposOrigine)
#DureeProcedureDepuisPropCom (AdoptionConseil – AdoptionProposOrigine)
#DureeProcedureDepuisTransCons (AdoptionConseil – TransmissionConseil)
#DureeTotaleDepuisPropCom (SignPECS – AdoptionProposOrigine)
#DureeTotaleDepuisTransCons (SignPECS – TransmissionConseil) 


def get_vote_public(adopt_cs_contre, adopt_cs_abs):
	"""
	FUNCTION
	return the vote_public variable
	PARAMETERS
	adopt_cs_contre: adopt_cs_contre objet from index [AdoptCsContreAssoc model instance]
	adopt_cs_abs: adopt_cs_abs object from index [AdoptCsAbsAssoc model instance]
	RETURN
	vote_public [boolean]
	"""
	adopt_cs_contres=adopt_cs_contre.all()
	adopt_cs_abss=adopt_cs_abs.all()
	if adopt_cs_contres or adopt_cs_abss:
		return True
	return False

#vote_public is True if adopt_cs_contre or adopt_cs_abs has a value


#external table
def link_act_gvt_compo(act, adopt_conseil, sign_pecs):
	"""
	FUNCTION
	fill the assocation table which links an act to its governments composition
	PARAMETERS
	act: instance of an act [Act model instance]
	adopt_conseil: adopt_conseil variable [date]
	sign_pecs: sign_pecs variable [date]
	RETURN
	None
	"""

	#we retrieve all the rows from GvtCompo for which start_date<adoptionConseil<end_date
	if adopt_conseil!=None:
		date=adopt_conseil
	elif sign_pecs!=None:
		#if no adopt_conseil, take sign_pecs
		date=sign_pecs
	else:
		return None

	gvt_compos=GvtCompo.objects.filter(start_date__lte=date, end_date__gte=date)
	#fill the association
	for gvt_compo in gvt_compos:
		try:
			act.gvt_compo.add(gvt_compo)
		except Exception, e:
			print "gvt compo already exists!", e
	else:
		print "gvt compo: no matching date"


#external table
def link_act_adopt_pc(act):
	"""
	FUNCTION
	fill the assocation table which links an act to its adopt_pc_contre and adopt_pc_abs variables
	PARAMETERS
	act: instance of an act [Act model instance]
	RETURN
	adopt_pc: adopt_pc_contre and adopt_pc_abs variables
	"""
	adopt_pc=None
	try:
		#is there a match in the ImportAdoptPC table?
		adopt_pc=ImportAdoptPC.objects.only("adopt_pc_contre", "adopt_pc_abs").get(releve_annee=act.releve_annee, releve_mois=act.releve_mois, no_ordre=act.no_ordre)
		save_adopt_cs_pc(act, "adopt_pc_contre", adopt_pc.adopt_pc_contre)
		save_adopt_cs_pc(act, "adopt_pc_abs", adopt_pc.adopt_pc_abs)
	except Exception, e:
		print "no adopt_pc variables for this act!"

	return adopt_pc



def get_data_prelex(soup, act_ids, act):
	"""
	FUNCTION
	get all the data from the prelex url
	PARAMETERS
	soup: prelex url content [BeautifulSoup object]
	act_ids: act ids instance [model instance]
	act: instance of the data of the act [Act model instance]
	RETURN
	fields: retrieved data from prelex [dictionary]
	"""
	fields={}

	#adopt_propos_origine
	fields['adopt_propos_origine']=get_adopt_propos_origine(soup, act_ids.propos_origine)
	print "adopt_propos_origine:", fields['adopt_propos_origine']

	#extract Adoption by Commission table (html content)
	adopt_com_table_soup=get_adopt_com_table(soup)

	#com_proc
	fields['com_proc']=get_com_proc(adopt_com_table_soup, act_ids.propos_origine)
	print "com_proc:", fields['com_proc']

	#dg_1
	dg_1=get_dg_1(adopt_com_table_soup)

	#jointly responsible persons (dg_2 and resp_2 or resp_3)
	dg_2, resp_2=get_jointly_resps(adopt_com_table_soup)

	#dg_* and dg_sigle_*
	dgs=save_get_dgs([dg_1, dg_2])
	for index in xrange(len(dgs)):
		num=str(index+1)
		#django adds "_id" to foreign keys field names
		dg='dg_'+num+"_id"
		fields[dg]=None
		if dgs[index]!=None:
			fields[dg]=dgs[index]
			#list possible dgs
			try:
				for possible_dg in dgs[index]:
					print dg+":", possible_dg.dg
					print "dg_sigle_"+num+":", possible_dg.dg_sigle.dg_sigle
			except Exception, e:
				#only one dg
				#~ print "only one dg", e
				print dg+":", dgs[index].dg
				print "dg_sigle_"+num+":", dgs[index].dg_sigle.dg_sigle


	#resp_1, resp_2, resp_3
	resp_names=get_resps(adopt_com_table_soup)

	if resp_2!=None:
		if resp_names[1]==None:
			resp_names[1]=resp_2
		elif resp_names[2]==None:
			resp_names[2]=resp_2
	resps=get_resp_objs(resp_names)

	#resp variables (name, country, party, party_family)
	for index in xrange(len(resps)):
		num=str(index+1)
		#django adds "_id" to foreign keys field names
		name="resp_"+num+"_id"
		fields[name]=None
		if resps[index]!=None:
			fields[name]=resps[index]
			print name+":", fields[name].name
			if fields[name].country!=None:
				print "country_"+num+":", fields[name].country.pk
				party=fields[name].party
				print "party_"+num+":", party.party
				print "party_family_"+num+":", PartyFamily.objects.only("party_family").get(party=party.pk, country=fields[name].country.pk)

	#transm_council
	fields['transm_council']=get_transm_council(soup, act_ids.propos_origine)
	print "transm_council:", fields['transm_council']

	#nb_point_b
	fields['nb_point_b']=get_nb_point_b(soup, act_ids.propos_origine)
	print "nb_point_b:", fields['nb_point_b']

	#cons_b
	fields['cons_b']=get_cons_b(soup, act_ids.propos_origine)
	print "cons_b:", fields['cons_b']

	#nb_lectures -> ALREADY IN OEIL -> used only for adopt_conseil!
	fields['nb_lectures']=get_nb_lectures(soup, act_ids.no_unique_type, act.split_propos)
	#~ print "nb_lectures:", fields['nb_lectures']

	#adopt_conseil
	fields['adopt_conseil']=get_adopt_conseil(soup, act.suite_2e_lecture_pe, act.split_propos, fields['nb_lectures'])
	print "adopt_conseil:", fields['adopt_conseil']

	#nb_point_a
	fields['nb_point_a']=get_nb_point_a(soup, act_ids.propos_origine)
	print "nb_point_a:", fields['nb_point_a']

	#council_a
	fields['council_a']=get_council_a(soup)
	print "council_a:", fields['council_a']

	#config_cons
	save_config_cons(act.code_sect_1_id)

	#duree_adopt_trans
	fields['duree_adopt_trans']=get_date_diff(fields['transm_council'], fields['adopt_propos_origine'])
	print "duree_adopt_trans:", fields['duree_adopt_trans']

	#duree_proc_depuis_prop_com
	fields['duree_proc_depuis_prop_com']=get_date_diff(fields['adopt_conseil'], fields['adopt_propos_origine'])
	print "duree_proc_depuis_prop_com:", fields['duree_proc_depuis_prop_com']

	#duree_proc_depuis_trans_cons
	fields['duree_proc_depuis_trans_cons']=get_date_diff(fields['adopt_conseil'], fields['transm_council'])
	print "duree_proc_depuis_trans_cons:", fields['duree_proc_depuis_trans_cons']

	#duree_tot_depuis_prop_com
	fields['duree_tot_depuis_prop_com']=get_date_diff(str(act.sign_pecs), fields['adopt_propos_origine'])
	#if no sign_pecs
	if fields['duree_tot_depuis_prop_com']==None:
		fields['duree_tot_depuis_prop_com']=fields['duree_proc_depuis_prop_com']
	print "duree_tot_depuis_prop_com:", fields['duree_tot_depuis_prop_com']

	#duree_tot_depuis_trans_cons
	fields['duree_tot_depuis_trans_cons']=get_date_diff(str(act.sign_pecs), fields['transm_council'])
	#if no sign_pecs
	if fields['duree_tot_depuis_trans_cons']==None:
		fields['duree_tot_depuis_trans_cons']=fields['duree_proc_depuis_trans_cons']
	print "duree_tot_depuis_trans_cons:", fields['duree_tot_depuis_trans_cons']

	#vote_public
	fields['vote_public']=get_vote_public(act.adopt_cs_contre, act.adopt_cs_abs)
	print "vote_public:", fields['vote_public']

	#adopt_pc_contre, #adopt_pc_abs
	adopt_pc=link_act_adopt_pc(act)
	if adopt_pc!=None:
		print "adopt_pc_contre:", adopt_pc.adopt_pc_contre
		print "adopt_pc_abs:", adopt_pc.adopt_pc_abs

	#TEST ONLY -> TO REMOVE
	#~ act.adopt_conseil="2012-02-21"
	link_act_gvt_compo(act, fields['adopt_conseil'], act.sign_pecs)
	for gvt_compo in act.gvt_compo.all():
		print "gvt_compo_country:", gvt_compo.country.country_code
		partys=""
		for party in gvt_compo.party.all():
			partys+=party.party+"; "
		print "gvt_compo_partys:", partys[:-2]

	return fields
