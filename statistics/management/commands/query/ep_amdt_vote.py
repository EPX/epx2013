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
    variables={"com_amdt_tabled": "Nombre moyen d’amendements déposés par la commission parlementaire du PE saisie au fond, par période", "amdt_tabled": "Nombre moyen d’amendements déposés au PE, par période"}
    Model=Act
    if cs is not None:
        list_acts_cs=get_list_acts_cs(cs[0], Model=Model)

    for var, question in variables.iteritems():
        filter_vars_acts={var+"__isnull": False}
        res, filter_vars, filter_total=init_periods(Model, filter_vars_acts=filter_vars_acts)

        #filter by specific cs
        if cs is not None:
            question+=" (code sectoriel : "+cs[1]+")"
            res=get_by_period_cs(list_acts_cs, res, Model, filter_vars, filter_total, avg_variable=var)
        else:
            res=get_by_period(res, Model, filter_vars, filter_total, avg_variable=var)

        write_periods(question, res, percent=1)


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


def q100(factor="everything"):
    #1/Moyenne EPVotesFor1-2, 3/Moyenne EPVotesAgst1-2, 5/Moyenne EPVotesAbs1-2, par année, par secteur, par année et par secteur
    variables={"votes_for_": "EPVotesFor", "votes_agst_": "EPVotesAgst", "votes_abs_": "EPVotesAbs"}
    nb_figures_cs=2

    if factor=="csyear":
        #get by cs and by year only (for specific cs)
        analyses, nb_figures_cs=get_specific_cs()

    for key, value in variables.iteritems():
        exclude_vars_acts={key+"1__isnull": True, key+"2__isnull": True}
        init_question="Nombre moyen de "+value+"1-2"

        for analysis, question in analyses:
            question=init_question+question
            res=init(analysis)
            res=get(analysis, res, variable=key+"1", variable_2=key+"2", exclude_vars_acts=exclude_vars_acts, nb_figures_cs=nb_figures_cs)
            write(analysis, question, res, percent=1)


def q100_periods(cs=None):
    #1/Moyenne EPVotesFor1-2, 2/Moyenne EPVotesAgst1-2, 3/Moyenne EPVotesAbs1-2, suivant différentes périodes
    variables={"votes_for_": "EPVotesFor", "votes_agst_": "EPVotesAgst", "votes_abs_": "EPVotesAbs"}
    res_vars={}
    nb=2
    Model=Act
    if cs is not None:
        list_acts_cs=get_list_acts_cs(cs[0], Model=Model)

    for key, value in variables.iteritems():
        question="Nombre moyen de "+value+"1-2, par période"
        filter_vars_acts={key+"1__gt": 0, key+"2__gt": 0}
        res, filter_vars, filter_total=init_periods(Model, filter_vars_acts=filter_vars_acts)

        #filter by specific cs
        if cs is not None:
            question+=" (code sectoriel : "+cs[1]+")"

        for index in range(1, nb+1):
            i=str(index)
            res_vars["res_"+i]=list(res)

            if cs is not None:
                res_vars["res_"+i]=get_by_period_cs(list_acts_cs, res_vars["res_"+i], Model, filter_vars, filter_total, avg_variable=key+i)
            else:
                res_vars["res_"+i]=get_by_period(res_vars["res_"+i], Model, filter_vars, filter_total, avg_variable=key+i)

        write_periods(question, res_vars["res_1"], percent=1, res_2=res_vars["res_2"])


def q105(factor="everything"):
    #1/ Moyenne EPComAmdtAdopt + EPAmdtAdopt, 2/ Moyenne EPComAmdtTabled + EPAmdtTabled
    #par année, par secteur, par année et par secteur
    variables=(
        (("com_amdt_adopt", "EPComAmdtAdopt"), ("amdt_adopt", "EPAmdtAdopt")),
        (("com_amdt_tabled", "EPComAmdtTabled"), ("amdt_tabled", "EPAmdtTabled"))
    )

    if factor=="csyear":
        #get by cs and by year only (for specific cs)
        analyses, nb_figures_cs=get_specific_cs()

    for variable in variables:
        filter_vars={variable[0][0]+"__gt": 0, variable[1][0]+"__gt": 0}
        init_question="Nombre moyen de "+variable[0][1]+"+"+variable[1][1]
        
        for analysis, question in analyses:
            question=init_question+question
            
            res_1=init(analysis)
            res_2=init(analysis)
            res_1=get(analysis, res_1, variable=variable[0][0], filter_vars_acts=filter_vars, nb_figures_cs=nb_figures_cs)
            res_2=get(analysis, res_2, variable=variable[1][0], filter_vars_acts=filter_vars, nb_figures_cs=nb_figures_cs)
            write(analysis, question, res_1, res_2=res_2, percent=1, query="1+2")


#NOT USED
def q106():
    #Nombre moyen (EPComAmdtAdopt+EPAmdtAdopt) / Nombre moyen (EPComAmdtTabled+EPAmdtTabled)
    
    num_vars=("amdt_adopt", "com_amdt_adopt")
    num_names=("EPAmdtAdopt", "EPComAmdtAdopt")
    denom_vars=("amdt_tabled", "com_amdt_tabled")
    denom_names=("EPAmdtTabled", "EPComAmdtTabled")
    division(num_vars, num_names, denom_vars, denom_names, operation="+")


#NOT USED
def q109():
    #1/ Moyenne EPVotesFor1/EPVotesFor2 2/ Moyenne EPVotesAgst1/EPVotesAgst2 3/ Moyenne EPVotesAbs1/EPVotesAbs2
    variables=(
        ("votes_for_", "EPVotesFor"),
        ("votes_agst_", "EPVotesAgst"),
        ("votes_abs_", "EPVotesAbs")
    )

    for var in variables:
        var1=var[0]+"1"
        var2=var[0]+"2"
        init_question="Nombre moyen de " + var[1] + "1 / " + var[1]+"2, "
        filter_vars={var1+"__gt": 0, var2+"__gt": 0}

        question=init_question+"par secteur"
        res=init_cs()
        res=get_by_cs_division(res, var1, var2, filter_vars=filter_vars)
        write_cs(question, res, percent=1)

        question=init_question+"par année"
        res=init_year()
        res=get_by_year_division(res, var1, var2, filter_vars=filter_vars)
        write_year(question, res, percent=1)

        question=init_question+"par secteur et par année"
        res=init_cs_year()
        res=get_by_cs_year_division(res, var1, var2, filter_vars=filter_vars)
        write_cs_year(question, res, percent=1)


def division(num_vars, num_names, denom_vars, denom_names, factor, operation=None):
    filter_vars={num_vars[0]+"__gt": 0, denom_vars[0]+"__gt": 0}
    init_question="Nombre moyen (" + num_names[0]
    
    #only one variable in the numerator and one in the denominator
    if len(num_vars)==1:
        init_question=init_question + "/" + denom_names[0] +")"
    else:
        #2 variables in the numerator and 2 in the denominator
        init_question=init_question +operation+num_names[1]+") /  ("+denom_names[0]+operation+denom_names[1]+")"

        filter_vars.update({num_vars[1]+"__gt": 0,  denom_vars[1]+"__gt": 0})

    if factor=="csyear":
        #get by cs and by year only (for specific cs)
        analyses, nb_figures_cs=get_specific_cs()


    for analysis, question in analyses:
        question=init_question+question
        res=init(analysis)
        res=get(analysis, res, num_vars=num_vars, denom_vars=denom_vars, filter_vars_acts=filter_vars, operation=operation, nb_figures_cs=nb_figures_cs)
        write(analysis, question, res, percent=1)


def q111(factor="everything"):
    #Nombre moyen de EPComAmdtAdopt / EPComAmdtTabled
    #pour tous les actes, par année, par secteur, par année et par secteur
    num_vars=("com_amdt_adopt",)
    num_names=("EPComAmdtAdopt",)
    denom_vars=("com_amdt_tabled",)
    denom_names=("EPComAmdtTabled",)
    division(num_vars, num_names, denom_vars, denom_names, factor)


def q112(factor="everything"):
    #Nombre moyen de EPAmdtAdopt / EPAmdtTabled
    #pour tous les actes, par année, par secteur, par année et par secteur
    num_vars=("amdt_adopt",)
    num_names=("EPAmdtAdopt",)
    denom_vars=("amdt_tabled",)
    denom_names=("EPAmdtTabled",)
    division(num_vars, num_names, denom_vars, denom_names, factor)


def q113(factor="everything"):
    #Nombre moyen de (EPAmdtAdopt - EPComAmdtAdopt) / (EPAmdtTabled - EPComAmdtTabled)
    #pour tous les actes, par année, par secteur, par année et par secteur
    num_vars=("amdt_adopt", "com_amdt_adopt")
    num_names=("EPAmdtAdopt", "EPComAmdtAdopt")
    denom_vars=("amdt_tabled", "com_amdt_tabled")
    denom_names=("EPAmdtTabled", "EPComAmdtTabled")
    division(num_vars, num_names, denom_vars, denom_names, factor, operation="-")
