#-*- coding: utf-8 -*-

#queries about the amdt variables

#import general steps common to each query
from  ..init import *
from  ..get import *
from  ..write import *


def q16():
    #nombre moyen de EPComAmdtTabled, EPComAmdtAdopt, EPAmdtTabled, EPAmdtAdopt
    question="nombre moyen de EPComAmdtTabled, EPComAmdtAdopt, EPAmdtTabled, EPAmdtAdopt par année"
    print question
    amdts={}
    amdts["EPComAmdtTabled"]="com_amdt_tabled"
    amdts["EPComAmdtAdopt"]="com_amdt_adopt"
    amdts["EPAmdtTabled"]="amdt_tabled"
    amdts["EPAmdtAdopt"]="amdt_adopt"
    res={}
    for amdt in amdts:
        res[amdt]={}
        for year in years_list:
            res[amdt][year]=[0,0]

    for act in Act.objects.filter(validated=2):
        year=str(act.releve_annee)
        for amdt in amdts:
            if getattr(act, amdts[amdt])!=None:
                res[amdt][year][1]+=1
                res[amdt][year][0]+=getattr(act, amdts[amdt])
    print "res", res

    writer.writerow([question])
    writer.writerow(years_list_zero)
    for amdt in amdts:
        row=[amdt]
        for year in years_list:
            if res[amdt][year][1]==0:
                res_year=0
            else:
                res_year=round(float(res[amdt][year][0])/res[amdt][year][1],3)
            row.append(res_year)
        writer.writerow(row)
    writer.writerow("")
    print ""




def q32(display_name, variable_name):
    #nombre moyen de EPComAmdtTabled, EPComAmdtAdopt, EPAmdtTabled, EPAmdtAdopt
    question="nombre moyen de " +display_name+ " par secteur, en fonction de l'année"
    print question
    res, total_year=init_cs_year(total=True, amdt=True)
    res, total_year=get_by_cs_year(res, variable=variable_name, total_year=total_year)
    write_cs_year(question, res, total_year=total_year, amdt=True)



def q75(cs=None):
    variables={"com_amdt_tabled": "Nombre moyen d’amendements déposés par la commission parlementaire du PE saisie au fond", "amdt_tabled": "Nombre moyen d’amendements déposés au PE"}
    Model=Act
    if cs is not None:
        list_acts_cs=get_list_acts_cs(cs[0], Model=Model)

    for var, question in variables.iteritems():
        filter_vars_acts={var+"__isnull": False}
        periods, nb_periods, res, filter_vars, filter_total=init_periods(Model, filter_vars_acts=filter_vars_acts)

        #filter by specific cs
        if cs is not None:
            question+=" (code sectoriel: "+cs[1]+")"
            res=get_by_period_cs(list_acts_cs, periods, nb_periods, res, Model, filter_vars, filter_total, avg_variable=var)
        else:
            res=get_by_period(periods, nb_periods, res, Model, filter_vars, filter_total, avg_variable=var)

        write_periods(question, res, periods, nb_periods, percent=1)


def q99():
    #Nombre d’EPComAmdtAdopt, 2/Nombre d’EPComAmdtTabled, 3/Nombre d’EPAmdtAdopt, 4/Nombre d’EPAmdtTabled, par année, par secteur, par année et par secteur
    variables={"com_amdt_tabled": "EPComAmdtTabled", "com_amdt_adopt": "EPComAmdtAdopt", "amdt_tabled": "EPAmdtTabled", "amdt_adopt": "EPAmdtAdopt"}

    for key, value in variables.iteritems():
        filter_vars={key+"__isnull": False}

        question="Nombre total d'"+value+" par secteur"
        print question
        res=init_cs(count=False)
        res=get_by_cs(res, count=False, variable=key, filter_vars=filter_vars)
        write_cs(question, res, count=False)
#~
        question="Nombre total d'"+value+" par année"
        print question
        res=init_year(count=False)
        res=get_by_year(res, count=False, variable=key, filter_vars=filter_vars)
        write_year(question, res, count=False)

        question="Nombre total d'"+value+" par année et par secteur"
        print question
        res=init_cs_year(count=False)
        res=get_by_cs_year(res, count=False, variable=key, filter_vars=filter_vars)
        write_cs_year(question, res, count=False)


def q100():
    #1/Moyenne EPVotesFor1-2, 3/Moyenne EPVotesAgst1-2, 5/Moyenne EPVotesAbs1-2, par année, par secteur, par année et par secteur
    variables={"votes_for_": "EPVotesFor", "votes_agst_": "EPVotesAgst", "votes_abs_": "EPVotesAbs"}
    res={}
    nb=2

    for key, value in variables.iteritems():
        filter_vars={key+"1__isnull": False, key+"2__isnull": False}
        #~
        question="Nombre moyen de "+value+"1-2 par secteur"
        print question
        for index in range(1, nb+1):
            i=str(index)
            res["res_"+i]=init_cs()
            res["res_"+i]=get_by_cs(res["res_"+i], variable=key+i, filter_vars=filter_vars)
        write_cs(question, res["res_1"], res_2=res["res_2"], percent=1)

        question="Nombre moyen de "+value+"1-2 par année"
        print question
        for index in range(1, nb+1):
            i=str(index)
            res["res_"+i]=init_year()
            res["res_"+i]=get_by_year(res["res_"+i], variable=key+i, filter_vars=filter_vars)
        write_year(question, res["res_1"], res_2=res["res_2"], percent=1)

        question="Nombre moyen de "+value+"1-2 par secteur et par année"
        print question
        for index in range(1, nb+1):
            i=str(index)
            res["res_"+i]=init_cs_year()
            res["res_"+i]=get_by_cs_year(res["res_"+i], variable=key+i, filter_vars=filter_vars)
        write_cs_year(question, res["res_1"], res_2=res["res_2"], percent=1)


def q100_periods(cs=None):
    #1/Moyenne EPVotesFor1-2, 3/Moyenne EPVotesAgst1-2, 5/Moyenne EPVotesAbs1-2, suivant différentes périodes
    variables={"votes_for_": "EPVotesFor", "votes_agst_": "EPVotesAgst", "votes_abs_": "EPVotesAbs"}
    res_vars={}
    nb=2
    Model=Act
    list_acts_cs=get_list_acts_cs(cs[0], Model=Model)

    for key, value in variables.iteritems():
        filter_vars_acts={key+"1__isnull": False, key+"2__isnull": False}
        periods, nb_periods, res, filter_vars, filter_total=init_periods(Model, filter_vars_acts=filter_vars_acts)

        #filter by specific cs
        if cs is not None:
            question="Nombre moyen de "+value+"1-2 (code sectoriel: "+cs[1]+")"

            for index in range(1, nb+1):
                i=str(index)
                res_vars["res_"+i]=list(res)
                res_vars["res_"+i]=get_by_period_cs(list_acts_cs, periods, nb_periods, res_vars["res_"+i], Model, filter_vars, filter_total, avg_variable=key+i)

            write_periods(question, res_vars["res_1"], periods, nb_periods, percent=1, res_2=res_vars["res_2"])
