#-*- coding: utf-8 -*-

from django.core.management.base import NoArgsCommand


#import specific queries
from common import *
from query import acts, adopt_cs, duree, ep_amdt_vote, min_attend, modif_propos, nb_mots, party_family, pers, point_b, type_acte, vote, country




class Command(NoArgsCommand):
    def handle(self, **options):
        #proportion d’actes avec plusieurs codes sectoriels
        #~ q1()
        #ventilation par domaines
        #~ acts.q2()
        #Concordance PartyFamilyResp et GroupePolitiqueRapporteur (Social Democracy): Pourcentage sur la periode 1996-2012
        #~ q3()
        #Concordance PartyFamilyResp et GroupePolitiqueRapporteur (Conservative/Christian Democracy): Pourcentage sur la periode 1996-2012
        #~ q4()
        #~ #durée moyenne des actes adoptés en 1e et en 2e lecture
        #~ q7()
        #~ #durée moyenne entre transmission au conseil et adoption pour les actes qui ont donné lieu à un vote public
        #~ q8()


        #PAR ANNEE

        #production législative
        #~ acts.q9()
        #ventilation par domaines
        #~ q10()
        #pourcentage de propositions modifiées par la Commission
        #~ q11()
        #~ #durée moyenne d’adoption
        #~ q12()
        #pourcentage d’actes adoptés en 1e et 2e lecture
        #~ q13()
        #durée moyenne des actes adoptés en 1e et en 2e lecture
        #~ q14()
        #durée moyenne entre transmission au conseil et adoption pour les actes qui ont donné lieu à un vote public
        #~ q15()
        #nombre moyen d’amendements déposés/adoptés
        #~ q16()
        #vote?
        #~ q17()
        #pourcentage AdoptCSContre=Y
        #~ q18("adopt_cs_contre")
        #~ #1/ %age AdoptCSContre=Y ET 1 EM.       2/%age AdoptCSContre=Y ET 2 EM.        3/%age AdoptCSContre=Y ET 3 EM
        #~ q19()
        #Durée moyenne des actes soumis à un vote
        #~ q20()
        #Nombre d’actes pour lesquels on a eu au moins une discussion en points B
        #~ q21()
        #pourcentage de ministres presents (M) et de RP (CS ou CS_PR)? par annee
        #~ q22()
        #Concordance PartyFamilyResp et GroupePolitiqueRapporteur (Social Democracy): Pourcentage par année
        #~ q23()
        #Concordance PartyFamilyResp et GroupePolitiqueRapporteur (Conservative/Christian Democracy): Pourcentage par année
        #~ q24()


        #PAR SECTEUR ET PAR ANNEE

        #% age de propositions modifiées par la Commission
        #~ q27()
        #~ #durée moyenne d’adoption
        #~ q28()
        #~ #% age d’actes adoptés en 1e et 2e lecture
        #~ q29()
        #~ #durée moyenne des actes adoptés en 1e et en 2e lecture
        #~ q30()
        #~ #durée moyenne entre transmission au conseil et adoption pour les actes qui ont donné lieu à un vote public
        #~ q31()
        #~ #nombre moyen d’amendements déposés/adoptés
        #~ q32("EPComAmdtTabled", "com_amdt_tabled")
        #~ q32("EPComAmdtAdopt", "com_amdt_adopt")
        #~ q32("EPAmdtTabled", "amdt_tabled")
        #~ q32("EPAmdtAdopt", "amdt_adopt")
        #Vote?
        #~ q33()
        #%age de votes négatifs par Etat membre
        #~ q34()
        #% age de votes négatifs isolés, de 2 Etats, de 3 Etats
        #~ q35(1)
        #~ q35(2)
        #~ q35(3)
        #Durée moyenne des actes soumis à un vote
        #~ q36()
        #~ #Pourcentage d’actes pour lesquels on a eu au moins une discussion en points B
        #~ q37()
        #~ #pourcentage de ministres presents (M) et de RP (CS ou CS_PR)? par annee ET par secteurs
        #~ q38()
        #Concordance PartyFamilyResp et GroupePolitiqueRapporteur (Social Democracy): Pourcentage par année et par secteur
        #~ q39()
        #~ #Concordance PartyFamilyResp et GroupePolitiqueRapporteur (Conservative/Christian Democracy): Pourcentage par année et par secteur
        #~ q40()
        #~

        #période 2010-2012 : %age d’actes ayant fait l’objet d’ interventions des parlements nationaux
        #~ q43()

        #~ #pourcentage AdoptCSContre=Y (parmi les actes AdoptCSRegleVote=U du même secteur et de la même année) par secteur et par année
        #~ q44()
        #pourcentage 1/2/3 EM (parmi les actes AdoptCSContre=Y et AdoptCSRegleVote=U du même secteur et de la même année) par secteur et par année
        #~ q45(1)
        #~ q45(2)
        #~ q45(3)
        #pourcentage AdoptCSAbs=Y (parmi les actes AdoptCSRegleVote=U du même secteur et de la même année) par secteur et par année
        #~ q46()
        #~ #pourcentage 1/2/3 EM (parmi les actes AdoptCSAbs=Y et AdoptCSRegleVote=U du même secteur et de la même année) par secteur et par année
        #~ q47(1)
        #~ q47(2)
        #~ q47(3)

        #DureeTotaleDepuisTransCons moyenne pour actes avec au moins une discussion en point B par année
        #~ q48()
        #DureeTotaleDepuisTransCons moyenne pour actes avec au moins une discussion en point B par secteur
        #~ q49()
        #~ #DureeTotaleDepuisTransCons moyenne pour les actes avec au moins une discussion en point B, par secteur et par année
        #~ q50()
       #DureeTotaleDepuisTransCons moyenne lorsque AdoptCSRegleVote=U par année
        #~ q51("U")
        #~ q51("V")
        #~ #DureeTotaleDepuisTransCons moyenne lorsque AdoptCSRegleVote=U par secteur
        #~ q52("U")
        #~ q52("V")
        #DureeTotaleDepuisTransCons moyenne lorsque AdoptCSRegleVote=U, par secteur et par année
        #~ q53("U")
        #~ q53("V")

        #Nombre de mots moyen des textes des actes, par année
        #~ q54()
        #~ #Nombre de mots moyen des textes des actes, par secteur
        #~ q55()
        #~ #Nombre de mots moyen des textes des actes, par secteur et par année
        #~ q56()

        #pourcentage d'actes avec plusieurs bases juridiques dans la production législative, par année
        #~ q57()
        #~ q57("13", "Marché intérieur")
        #DureeTotaleDepuisPropCom moyenne des actes pour lesquels il y a concordance des PartyFamilyResp et GroupePolitiqueRapporteur ("Social Democracy")
        #~ q58()
        #impact du nombre de bases juridiques sur la durée de la procédure
        #~ q59("13", "Marché intérieur")
        #~ #impact du nombre de bases juridiques sur la nombre de points b
        #~ q60()
        #Nombre d'actes avec un vote public
        #~ q61()
        #~ #Pourcentages d'actes adoptés en 1ère lecture en fonction du nombre de base juridiques et du code sectoriel
        #~ acts.q62("13", "Marché intérieur")

        #Nombre de mots moyen suivant le type de l'acte, par année
        #~ q63()
        #~ q63_bis()
        #~ #Nombre de mots moyen suivant le NoUniqueType, par année
        #~ q64()
        #~ q64_bis()

        #Nombre de points B par année
        #~ q65()
        #Nombre de points B par secteur
        #~ q66()
        #Nombre de points B par année et par secteur
        #~ q67()
        #~ #Nombre de points B pour les actes avec un vote public, par année
        #~ q68()
        #~ #Nombre de points B pour les actes avec un vote public, par secteur
        #~ q69()
        #~ #Nombre de points B pour les actes avec un vote public, par année et par secteur
        #~ q70()


        #2014-07-24 : Hausse de la bureaucratisation, Conflictualité
        #pourcentages de propositions de la Commission adoptées par procédure écrite
        #~ acts.q71()
        #~ #pourcentage de textes adoptés en « points A » au Conseil
        #~ acts.q72()
        #~ #nombre de moyen de points B par texte
        #~ point_b.q73()
        #pourcentage de textes adoptés en 1ère lecture au Parlement Européen
        #~ acts.q74()
        #~ #nombre moyen d’amendements déposés
        #~ ep_amdt_vote.q75()
        #~ #% moyen de représentants permanents par acte
        #~ min_attend.q76()
        #~ #% ages moyens de votes publics, vote contre, abstentions là où VMQ est possible
        #~ acts.q77()
        #durée moyenne par acte
        #~ duree.q78()
        #% d’actes adoptés en 2ème lecture
        #~ acts.q79()
        #~ #% d’actes avec au moins 1 point B
        #~ acts.q80()


        #Liste des actes avec leur titre pour la période 1996-2012 lorsque l’un des 4 codes sectoriels comprend le code suivant
        #~ q82()
        #~ #Nb de mots x Nb d’actes par année, pour les secteurs
        #~ q83()
        #~
        #Pourcentage de textes lorsque PartyFamilyRapporteurPE1 DIFFERENTE de PartyFamilyRespPropos1
        #~ q84()

        #Nombre de CS DVE+DVE, pour certains secteurs, par année
        #~ q85()
#~
        #~ #Nombre de CS REG+REG, pour certains secteurs, par année
        #~ q86()
#~
        #~ #Nombre de CS DEC+DEC+CS DEC W/O ADD, pour certains secteurs, par année
        #~ q87()

        #1/pourcentage AdoptCSContre=Y (parmi les actes AdoptCSRegleVote=V) 2/pourcentage AdoptCSAbs=Y (parmi les actes AdoptCSRegleVote=U), par secteur, par annee, par secteur et par annee
        #~ q88()
#~
        #~ #Nombre de textes x Nombre de mots Pour l’année 2009 uniquement par mois
        #~ q90_mois()
        #~ q90_mois_nut()

        #Liste des RespPropos
        #~ q91()
        #Liste des Rapporteurs
        #~ q92()

        #Pourcentage des familles politiques des RespPropos
        #~ q93()
        #~ #Pourcentage des familles politiques des Rapporteurs
        #~ q94()


        #2014-10-31
        #Pourcentage de points B, par année, par secteur, par année et par secteur
        #~ point_b.q95()
        #~ #Durée DureeTotaleDepuisTransCons moyenne 1/pour tous les actes, 2/quand VotePublic=Y ou 3/quand VotePublic= N, par année, par secteur, par année et par secteur
        #~ duree.q96()
        #1/Pourcentage de AdoptCSContre=Y, 2/Pourcentage de AdoptCSAbs=Y, par année, par secteur, par année et par secteur
        #~ adopt_cs.q97()
        #Pourcentage d’actes adoptés avec NoUniqueType=COD 1/et NbLectures=1, 2/et NbLectures=2, par année, par secteur, par année et par secteur
        #~ acts.q98()
        #1/Nombre d’EPComAmdtAdopt, 2/Nombre d’EPComAmdtTabled, 3/Nombre d’EPAmdtAdopt, 4/Nombre d’EPAmdtTabled, par année, par secteur, par année et par secteur
        #~ ep_amdt_vote.q99()
        #~ #1/Moyenne EPVotesFor1-2, 3/Moyenne EPVotesAgst1-2, 5/MoyenneEPVotesAbs1-2, par année, par secteur, par année et par secteur
        #~ ep_amdt_vote.q100()


        #2014-11-5
        #Pourcentage des pays des RespPropos
        #~ country.q101()
        #Pourcentage des pays des Rapporteurs
        #~ country.q102()


        #2014-11-12 : Hausse de la bureaucratisation, Conflictualité pour le secteur Économie
        cs=[10, "Économie"]
        #pourcentages de propositions de la Commission adoptées par procédure écrite
        #~ acts.q71(cs=cs)
        #pourcentage de textes adoptés en « points A » au Conseil
        #~ acts.q72(cs=cs)
        #nombre de moyen de points B par texte
        #~ point_b.q73(cs=cs)
        #~ #pourcentage de textes adoptés en 1ère lecture au Parlement Européen
        #~ acts.q74(cs=cs)
        #nombre moyen d’amendements déposés
        #~ ep_amdt_vote.q75(cs=cs)
        #% moyen de représentants permanents par acte
        #~ min_attend.q76(cs=cs)
        #% ages moyens de votes publics, vote contre, abstentions là où VMQ est possible
        #~ acts.q77(cs=cs)
        #~ #durée moyenne par acte
        #~ duree.q78(cs=cs)
        #~ #% d’actes adoptés en 2ème lecture
        #~ acts.q79(cs=cs)
        #% d’actes avec au moins 1 point B
        #~ acts.q80(cs=cs)
        #~ #1/Moyenne EPVotesFor1-2, 2/Moyenne EPVotesAgst1-2, 3/MoyenneEPVotesAbs1-2
        #~ ep_amdt_vote.q100_periods(cs=cs)


        # 2014-11-17
        #nombre d actes adoptés sans point B, par période
        #~ acts.q103()


        #2014-11-18
        #1/Moyenne EPVotesFor1-2, 2/Moyenne EPVotesAgst1-2, 3/MoyenneEPVotesAbs1-2
        #~ ep_amdt_vote.q100_periods()


        #2014-11-19
        #Nombre d'actes par période
        #~ acts.q104()


        #2014-11-28
        #for all the acts, by cs, by year, by cs and by year
        #Pourcentage d'actes avec NoUniqueType=COD adoptés en 1ère / (2ème ou 3ème) lecture
        #~ acts.q98()
        #~ #Durée de la procédure (= Moyenne DureeTotaleDepuisTransCons ET DureeProcedureDepuisTransCons)
        #~ #1/pour tous les actes 2/VotePublic=Y 3/VotePublic=N 4/AdoptCSRegleVote=U 5/AdoptCSRegleVote=V 6/VotePublic=Y et AdoptCSRegleVote=U 7/ VotePublic=Y et AdoptCSRegleVote=V
        #~ duree.q96()
        #Durée Moyenne DureeTotaleDepuisTransCons
        #1/pour tous les actes 2/VotePublic=Y 3/VotePublic=N 4/AdoptCSRegleVote=U 5/AdoptCSRegleVote=V 6/VotePublic=Y et AdoptCSRegleVote=U 7/ VotePublic=Y et AdoptCSRegleVote=V
        #~ duree.q110()
        #~ #1/ Moyenne EPComAmdtAdopt + EPAmdtAdopt, 2/ Moyenne EPComAmdtTabled + EPAmdtTabled
        #~ ep_amdt_vote.q105()
        #Nombre moyen (EPComAmdtAdopt+EPAmdtAdopt) / Nombre moyen (EPComAmdtTabled+EPAmdtTabled)
        #ep_amdt_vote.q106()
        #Nombre moyen de EPComAmdtAdopt / EPComAmdtTabled
        #~ ep_amdt_vote.q111()
        #Nombre moyen de EPAmdtAdopt / EPAmdtTabled
        #~ ep_amdt_vote.q112()
        #~ #Nombre moyen de (EPAmdtAdopt - EPComAmdtAdopt) / (EPAmdtTabled - EPComAmdtTabled)
        #~ ep_amdt_vote.q113()
        #Pourcentage d'actes avec VotePublic=Y
        #~ acts.q107()
        #~ #1/Pourcentage "AdoptCSContre"= Y avec AdoptCSRegleVote=V 2/ Pourcentage "AdoptCSAbs"=Y, avec AdoptCSRegleVote=V 3/ pourcentage "AdoptCSAbs"=Y, avec AdoptCSRegleVote=U
        #~ adopt_cs.q88()
        #~ #Pourcentage d'actes avec au moins un point B
        #~ acts.q108()
        #~ #Nombre de mots moyen
        #~ nb_mots.q54()
        #Nombre de mots x Nombre d'actes
        #~ nb_mots.q83()
        #~ #Pourcentage de discordance des familles politiques
        #~ party_family.q84()
        #1/ Moyenne EPVotesFor1-2 2/ Moyenne EPVotesAgst1-2 3/ Moyenne EPVotesAbs1-2
        #ep_amdt_vote.q109()
        #~ ep_amdt_vote.q100()


        #2014-12-4 : Hausse de la bureaucratisation, Conflictualité pour le secteur Économie
        # NOUVELLES PERIODES
        factors=["periods"]
        periods=(
            ("Période 01/01/1996 - 15/09/1999", fr_to_us_date("01/01/1996"), fr_to_us_date("15/09/1999")),
            ("Période 16/09/1999 - 30/04/2004", fr_to_us_date("16/09/1999"), fr_to_us_date("30/04/2004")),
            ("Période 01/05/2004 - 14/09/2008", fr_to_us_date("01/05/2004"), fr_to_us_date("14/09/2008")),
            ("Période 15/09/2008 - 31/12/2013", fr_to_us_date("15/09/2008"), fr_to_us_date("31/12/2013"))
        )
        for period in periods:
            print period[1]
        #~ #pourcentages de propositions de la Commission adoptées par procédure écrite
        #~ acts.q71(cs=cs)
        #pourcentage de textes adoptés en « points A » au Conseil
        #~ acts.q72(cs=cs)
        #~ #nombre de moyen de points B par texte
        #~ point_b.q73(cs=cs)
        #pourcentage de textes adoptés en 1ère lecture au Parlement Européen
        #~ acts.q74(cs=cs)
        #nombre moyen d’amendements déposés
        #~ ep_amdt_vote.q75(cs=cs)
        #% moyen de représentants permanents par acte
        #~ min_attend.q76(cs=cs)
        #% ages moyens de votes publics, vote contre, abstentions là où VMQ est possible
        acts.q77(factors=factors, periods=periods)
        #durée moyenne par acte
        #~ duree.q78(cs=cs)
        #~ #% d’actes adoptés en 2ème lecture
        #~ acts.q79(cs=cs)
        #~ #% d’actes avec au moins 1 point B
        #~ acts.q80(cs=cs)
        #1/Moyenne EPVotesFor1-2, 2/Moyenne EPVotesAgst1-2, 3/MoyenneEPVotesAbs1-2
        #~ ep_amdt_vote.q100_periods(cs=cs)


        #2014-12-4
        #Duree de la procedure : DureeTotaleDepuisTransCons moyenne 1/pour tous les actes 2/VotePublic=Y 3/VotePublic=N 4/AdoptCSRegleVote=U 5/AdoptCSRegleVote=V 6/VotePublic=Y et AdoptCSRegleVote=V 7/VotePublic=Y et AdoptCSRegleVote=U
        #~ duree.q8()


        #2014-12-18
        #1/pourcentage de AdoptCSContre et 2/pourcentage de AdoptCSAbs pour chaque Etat membre, pour tous les actes puis par périodes
        #~ country.q114()

        #for all the acts, by cs, by year, by cs and by year
        #Pourcentage d'actes avec NoUniqueType=COD adoptés en 1ère / (2ème ou 3ème) lecture
        factor=["csyear"]
        #~ acts.q98(factor=factor)
        #~ #Durée de la procédure (= Moyenne DureeTotaleDepuisTransCons ET DureeProcedureDepuisTransCons)
        #~ #1/pour tous les actes 2/VotePublic=Y 3/VotePublic=N 4/AdoptCSRegleVote=U 5/AdoptCSRegleVote=V 6/VotePublic=Y et AdoptCSRegleVote=U 7/ VotePublic=Y et AdoptCSRegleVote=V
        #~ duree.q96(factor=factor)
        #Durée Moyenne DureeTotaleDepuisTransCons
        #1/pour tous les actes 2/VotePublic=Y 3/VotePublic=N 4/AdoptCSRegleVote=U 5/AdoptCSRegleVote=V 6/VotePublic=Y et AdoptCSRegleVote=U 7/ VotePublic=Y et AdoptCSRegleVote=V
        #~ duree.q110(factor=factor)
        #1/ Moyenne EPComAmdtAdopt + EPAmdtAdopt, 2/ Moyenne EPComAmdtTabled + EPAmdtTabled
        #~ ep_amdt_vote.q105(factor=factor)
        #Nombre moyen de EPComAmdtAdopt / EPComAmdtTabled
        #~ ep_amdt_vote.q111(factor=factor)
        #Nombre moyen de EPAmdtAdopt / EPAmdtTabled
        #~ ep_amdt_vote.q112(factor=factor)
        #~ #Nombre moyen de (EPAmdtAdopt - EPComAmdtAdopt) / (EPAmdtTabled - EPComAmdtTabled)
        #~ ep_amdt_vote.q113(factor=factor)
        #Pourcentage d'actes avec VotePublic=Y
        #~ acts.q107(factor=factor)
        #~ #1/Pourcentage "AdoptCSContre"= Y avec AdoptCSRegleVote=V 2/ Pourcentage "AdoptCSAbs"=Y, avec AdoptCSRegleVote=V 3/ pourcentage "AdoptCSAbs"=Y, avec AdoptCSRegleVote=U
        #~ adopt_cs.q88(factor=factor)
        #~ #Pourcentage d'actes avec au moins un point B
        #~ acts.q108(factor=factor)
        #~ #Nombre de mots moyen
        #~ nb_mots.q54(factor=factor)
        #Nombre de mots x Nombre d'actes
        #~ nb_mots.q83(factor=factor)
        #~ #Pourcentage de discordance des familles politiques
        #~ party_family.q84(factor=factor)
        #1/ Moyenne EPVotesFor1-2 2/ Moyenne EPVotesAgst1-2 3/ Moyenne EPVotesAbs1-2
        #~ ep_amdt_vote.q100(factors=factor, nb_figures_cs=5)
#~ 
        #~ #) Pourcentage d'actes avec 1/CommissionPE= LIBE 2/CommissionPE= JURI par cs et par année
        #~ acts.q115(factor=factor)


        #2014-12-23
        #Nombre de mots moyen
        #~ nb_mots.q116(factors=["year"])
        #Nombre de mots x Nombre d’actes
        #~ nb_mots.q83(factors=["year"])

        #période 1/07/2009- 31/12/2013
        period=("2009-07-01", "2013-12-31")
        #Nombre d’actes par secteur
        #~ acts.q2(factors=["cs"], periods=period)
        #~ #pourcentage d'actes avec NoUniqueType= COD et NbLectures=1/2/3
        #~ acts.q98(factors=["all"], periods=period)
        #DureeTotaleDepuisTransCons moyenne
        #~ duree.q110(factors=["all"], periods=period)
        #1/Pourcentage "AdoptCSAbs"= Y parmi tous les actes 2/Pourcentage "AdoptCSContre"= Y parmi les actes avec AdoptCSRegleVote=V
        #~ adopt_cs.q97(factors=["all"], periods=period)
        #Pourcentage de M présents parmi les personnes de status différent de NA ou AB
        #~ min_attend.q117(factors=["all"], periods=period)

        #1/ Moyenne EPVotesFor1-2 2/ Moyenne EPVotesAgst1-2 3/ Moyenne EPVotesAbs1-2
        #~ ep_amdt_vote.q100(factors=["year", "cs", "csyear"])
#~ 
        factors=["cs", "periods"]
        periods=(
            ("2000-01-01", "2004-04-30"),
            ("2004-05-01", "2009-11-30"),
            ("2009-12-01", "2013-12-31")
        )
        #Pourcentage d'actes avec au moins un points B, exactement un point B, deux points B, plus de deux points B
        #~ acts.q108(factors=factors, periods=periods)
        #~ #DureeTotaleDepuisTransCons quand NbPointsB = 0,1,2,3 ou plus
        #~ duree.q118(factors=factors, periods=periods)
        #Pourcentage d'actes avec VotePublic=Y quand NbPointsB = 1,2,3 ou plus
        #~ acts.q119(factors=factors, periods=periods)
#~ 
        #~ periods=(
            #~ ("1996-01-01", "1999-10-31"),
            #~ ("1999-11-01", "2004-10-31"),
            #~ ("2004-11-01", "2009-10-31"),
            #~ ("2009-11-01", "2013-12-31")
        #~ )
        #~ #1/pourcentage de AdoptCSContre et 2/pourcentage de AdoptCSAbs pour chaque Etat membre, pour tous les actes puis par périodes
        #~ country.q114(factors=["country", "periods"], periods=periods)
        #old version
        #~ country.q114()


        #2015-02-05
        #Liste des actes pour lesquels au moins 1 CodeSect commence par 03 / 12 / 13 / 15
        #~ acts.q120()
        #~ #Liste des actes pour lesquels plusieurs Bases Juridiques
        #~ acts.q121()
        #Pourcentage d’actes adoptés avec M=0 (Ministers Attendance)
        factors=["cs", "year", "csyear"]
        #TEST
        #~ factors=["year"]
        #~ acts.q122(factors=factors)
