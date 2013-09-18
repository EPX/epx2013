from django import forms
from models import ActsIdsModel
#modif form: add non field error
from django.forms.util import ErrorList


class ActsIdsForm(forms.ModelForm):
	"""
	FORM
	details the ActsIds form (ids of the acts only)
	"""
	#EURLEX
	fileNoCelex=forms.RegexField(regex=r'^[0-9](195[789]|19[6-9][0-9]|20[0-1][0-9])([dflryDFLRY]|PC)[0-9]{4}(\(0[1-9]\)|R\(0[1-9]\))?$')
	#~ noCelex
	#Ne peut etre = 000L (sauf pour l'acte de NoSaisie 329)
	#Chaque acte a un numero Celex et ce numero est unique (sauf exception : acte de ReleveAnnee='2004', ReleveMois='4' et NoOrdre='52', OrdreSaisie='329')


	#OEIL

	fileNoUniqueType = forms.RegexField(regex=r'^COD|SYN|CNS|ACC|AVC|CS|CNB|ACI$', required=False)
	#~ noUniqueType
	#^(COD|SYN|CNS|ACC|AVC|CS|CNB|ACI)$"
	#~ Valeur du champ indiquee sur la fiche Prelex, oeil et Celex si NoUniqueType = COD ou SYN ou CNS ou AVC
	#~ ou ACI, uniquement sur les fiches Prelex et Celex si NoUniqueType = ACC
	#~ Codes COD, SYN, CNS, ACC, AVC, CNB et ACI attribues par l'UE ; en cas de divergences entre la fiche Prelex
	#~ et la fiche oeil, on prend le numero qui permet de retrouver la fiche via Oeil
	#~ Code CS recode lors de la constitution de la base pour les procedures n'impliquant que le Conseil

	fileNoUniqueAnnee = forms.IntegerField(min_value=1957, max_value=2020, required=False)
	#~ noUniqueAnnee
	#~ 1957 a l'annee courante.
	#~ Valeur du champ indiquee sur la fiche Prelex, oeil et Celex si NoUnique Type = COD ou SYN ou CNS ou AVC
	#~ ou ACI, uniquement sur les fiches Prelex et Celex si NoUniqueType = ACC
	#~ Valeur 000L si NumUniqueType = CS

	fileNoUniqueChrono = forms.RegexField(regex=r'^([1-9]([0-9]?){3})([a-zA-Z])?$', required=False)
	#~ noUniqueChrono
	#4 digits or 4 digits + 1 letter (if splitted proposition)
	#De 1 a 999
	#Valeur du champ indiquee sur la fiche Prelex, oeil et Celex si NoUniqueType = COD ou SYN ou CNS ou AVC ou ACI, uniquement sur les fiches Prelex et Celex si NoUniqueType = ACC
	#Valeur 000L si NumUniqueType = CS


	#PRELEX

	#normal case
	fileProposOrigine = forms.RegexField(regex=r'^COM|JAI|BCE|EM|CONS|CJEU$', required=False)
	#~ Ne peut etre = 000L. Une valeur parmi :COM, JAI, BCE, EM, CONS
	#~ Valeurs COM et JAI indiquees sur la fiche Prelex, Celex (et oeIL si le PE intervient dans la procedure)
	#~ Valeurs BCE indiquees sur la fiche Celex (il n'y a pas toujours de fiche Prelex)
	#~ Valeurs EM et CONS recodees lors de la constitution de la base
	#~ Ce champ est issu d'une saisie manuelle

	fileProposAnnee = forms.IntegerField(min_value=1957, max_value=2020, required=False)
	#~ Valeurs possibles : Ne peut etre = 000L
	#~ de 1957 a annee courante.
	#~ Lorsque ProposOrigine = COM ou JAI ou BCE, la valeur est celle qui figure dans le "code" du projet a l'origine de l'acte du Conseil, attribue par l'UE et indique sur les fiches Celex et Prelex (en cas de BCE, il n'existe pas toujours de fiche Prelex)
	#~ Lorsque ProposOrigine = CONS, la valeur est l'annee du document le plus ancien que nous puissions trouver
	#~ dans le registre du Conseil
	#~ Lorsque ProposOrigine = EM et que la date de la demande de l'Etat membre figure sur l'acte publie au JO, la
	#~ valeur est l'annee de cette date
	#~ Lorsque ProposOrigine = EM et que la date de la demande de l'Etat membre ne figure pas sur l'acte publie au
	#~ JO, la valeur est l'annee du document le plus ancien que nous puissions trouver dans le registre du Conseil

	fileProposChrono = forms.RegexField(regex=r'^([0-9]([0-9]?){4})(-[1-9][0-9]?)?$', required=False)
	#one to 5 digits (+ one hyphen and digit if splitted proposition)
	#~ Valeurs possibles : Peut etre = 000L
	#~ De 1 a 99999
	#~ Origine :
	#~ 1) Fiche Celex et Prelex
	#~ 2) Registre du Conseil (saisie manuelle)
	#~ 3) et 4) Fiche Celex ou registre du Conseil (saisie manuelle)

	#dosId
	fileDosId = forms.IntegerField(min_value=1, max_value=9999999, required=False)
	#between 1 and 9999999


	notes = forms.CharField(widget=forms.Textarea, required=False)


	class Meta:
		model = ActsIdsModel
		#OBLIGATORY FOR ACT VALIDATION (displays the variable values from the database)
		fields=('fileNoCelex', 'fileNoUniqueType', 'fileNoUniqueAnnee', 'fileNoUniqueChrono', 'fileProposOrigine', 'fileProposAnnee', 'fileProposChrono', 'fileDosId', 'notes')

	#trim trailing spaces
	def clean(self):
		cleaned_data = self.cleaned_data
		for k in self.cleaned_data:
			try:
				#only strings
				cleaned_data[k] = self.cleaned_data[k].strip()
			except:
				pass
		return cleaned_data


class ActsAddForm(forms.Form):
	"""
	FORM
	details the ActsAddForm form (fields for the add mode of Acts validation)
	"""
	actsToValidate=forms.ModelChoiceField(queryset=ActsIdsModel.objects.only("releveAnnee", "releveMois", "noOrdre").filter(validated=0), empty_label="Select an act to validate", widget=forms.Select(attrs={'onchange': 'display_or_update_act("add_act")'}))


class ActsModifForm(forms.Form):
	"""
	FORM
	details the ActsModifForm form (fields for the modification mode of Acts validation)
	"""
	#ids input boxes used for the modification
	releveAnneeModif=forms.IntegerField(label='ReleveAnnee', min_value=1957, max_value=2020)
	releveMoisModif=forms.IntegerField(label='ReleveMois', min_value=1, max_value=12)
	noOrdreModif=forms.IntegerField(label='NoOrdre', min_value=1, max_value=99)

	#check if the searched act already exists in the db and has been validated
	def is_valid(self):
		# run the parent validation first
		valid = super(ActsModifForm, self).is_valid()

		# we're done now if not valid
		if not valid:
			return valid

		#if the form is valid
		releveAnneeModif = self.cleaned_data.get("releveAnneeModif")
		releveMoisModif = self.cleaned_data.get("releveMoisModif")
		noOrdreModif = self.cleaned_data.get("noOrdreModif")

		try:
			act=ActsIdsModel.objects.get(releveAnnee=releveAnneeModif, releveMois=releveMoisModif, noOrdre=noOrdreModif, validated=1)
		except:
			print "pb find act"
			self._errors['__all__']=ErrorList([u"The act you are looking for has not been validated yet!"])
			return False

		# form valid -> return True
		return True


#~ il arrive que l'acte soit sur 1 fiche (Celex, par 32003D0277) ou 2 fiches (Celex et Prelex, par ex 32003D0065) ou 3 fiches (Celex, Prelex et OEIL, par ex 32003L0015).

#~ from celex, check if there is an oeil page:
#~ sur le document Celex il n'y a pas non plus de NumUnique, mais il s'agit parfois d'un oubli, donc il vaut mieux verifier avec le contenu de l'acte qui se trouve aussi dans le document Celex : il faut que l'acte soit adopte uniquement par le Conseil et qu'il n'y ait PAS au debut de l'acte 'Having regard to the opinion of the European Parliament'.

#~ il faudrait que lorsqu'on les rentre manuellement dans la base ou sur une interface (je ne sais pas si j'utilise le bon mot!), on puisse savoir immediatement s'il y a un probleme 1) pour construire l'url et trouver la page/fiche correspondante 2) d'incoherences entre les identifiants sur les differentes pages (si par ex il y a une fiche prelex et oeil, il faut que le NoUnique soit le meme sur les deux fiches)
