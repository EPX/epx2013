#-*- coding: utf-8 -*-

#get the corresponding data for each variable and put them in a dictionary
from django.db import models
from act.models import Act, MinAttend, Status, NP, PartyFamily
from act_ids.models import ActIds
from django.db.models import Count
from common import *
import copy



#count=False and variable=True: count the sum of all the values taken by a variable
    #e.g.: sum of all the values taken by duree_variable=1000 -> res=1000
#count=False and variable=False: count the number of occurences of items matching a set of criteria defined by filter_vars
    #e.g.: number of acts with a duree_variable greater than 0=5 -> res=5

#count=True and variable=True -> average computation: count the sum of all the values taken by a variable AND its number of occurences
    #e.g.: sum of all the values taken by duree_variable=1000, number of occurences of duree_variable=5 -> res=[1000, 5]
#count=True and variable=False -> percentage computation: count the number of occurences of items matching a set of criteria (defined by check_vars_act and check_vars_act_ids) AMONG the number of occurences of items matching the set of criteria (defined by filter_vars)
    #e.g.: number of occurences of duree_variable among the acts with no_unique_type=COD=5, number of acts with no_unique_type=COD=15 -> res=[5, 15]




#number of figures to use to get all the different cs -> if nb=2 then cs=01.xx.xx.xx ... 20.xx.xx.xx, if nb=5 then cs=01.10.xx.xx ... 20.90.xx.xx
nb_figures_cs=len(max(css, key=len))


def get_cs(cs):
    """
    FUNCTION
    extract the first figures of a cs as required in the analysis ("01.20.30.60" gives "01" if a two-digit cs is required)
    PARAMETERS
    cs: cs to extract from [string]
    RETURN
    new_cs: shortened cs to match with the cs of the analysis [string]
    """
    return cs[:nb_figures_cs]


def get_all_css(act):
    """
    FUNCTION
    get all the matching cs of an act (every act has up to four cs)
    PARAMETERS
    act: act to extract the cs from [Act instance]
    RETURN
    css_list: list of cs of the act [list of strings]
    """
    css_list=[]
    for nb in range(1, nb_css+1):
        code_sect=getattr(act, "code_sect_"+str(nb))
        if code_sect is not None:
            cs=get_cs(code_sect.code_sect)
            if cs in css:
                css_list.append(cs)
        else:
            #if one cs is null, all the following are null too
            break
    return css_list


def check_css(act, searched_css):
    """
    FUNCTION
    check that the act in parameter has at least one matching cs in "searched_css" list
    PARAMETERS
    act: act to extract the cs from [Act instance]
    searched_css: list of cs to use for the analysis [list of strings]
    RETURN
    True if there is at least one matching cs, False if there is None [boolean]
    """
    for nb in range(1, nb_css+1):
        code_sect=getattr(act, "code_sect_"+str(nb))
        if code_sect is not None:
            cs=get_cs(code_sect.code_sect)
            if cs in searched_css:
                return True
        else:
            #if one cs is null, all the following are null too
            break
    return False


def get_all_dgs(act):
    dg_list=[]
    for nb in range(1, nb_dgs+1):
        dg=getattr(act, "dg_"+str(nb))
        if dg is not None:
            dg_list.append(dg.dg)
        else:
            #if one dg is null, all the following are null too
            break
    return dg_list


def get_all_rappgroups(act):
    groups=[]
    for nb in range(1, nb_rapps+1):
        pers=getattr(act, "rapp_"+str(nb))
        if pers is not None:
            groups.append(pers.party.party)
        else:
            #if one rapp is null, all the following are null too
            break
    return groups
    

def get_all_resppfs(act):
    pf_list=[]
    for nb in range(1, nb_resps+1):
        resp=getattr(act, "resp_"+str(nb))
        if resp is not None:
            pf_list.append(PartyFamily.objects.get(country=resp.country, party=resp.party).party_family)
        else:
            #if one resp is null, all the following are null too
            break
    return pf_list


def get_all_perscountries(act, pers_type):
    country_list=[]
    if pers_type=="rapp":
        nb_pers=nb_rapps
    elif pers_type=="resp":
        nb_pers=nb_resps
        
    for nb in range(1, nb_pers+1):
        pers=getattr(act, pers_type+"_"+str(nb))
        if pers is not None:
            country_list.append(pers.country.country_code)
        else:
            #if one resp is null, all the following are null too
            break
    return country_list

    
def get_act_type_key(act_type):
    """
    FUNCTION
    get the key of the type of the act (one of the keys of the res dictionnary, "DEC", "REG" or "DVE")
    PARAMETERS
    act_type: type of the act being processed [string]
    RETURN
    act_type: key act_type [string]
    """
    #~ print "act.type_acte", act_type
    for key in act_types_keys:
         if key in act_type:
             return key
    #~ print "key", key
    return None
    

def get_act(Model, act):
    """
    FUNCTION
    get the Act instance of the act in parameter
    PARAMETERS
    Model: current model used for the act [Act/ActIds/MinAttend model]
    act: act being processed [Act/ActIds/MinAttend instance]
    RETURN
    act: Act instance of the act [Act instance]
    """
    #ActIds or MinAttend
    if Model!=Act:
        act=act.act
    return act


def check_vars(act, act_act, check_vars_act, check_vars_act_ids, adopt_var=None, nb_adopt_var=None, query=None):
    """
    FUNCTION
    from a filter dictionary using django syntax, check whether an act respects the criteria given in the analysis (for percentage computation)
    PARAMETERS
    act: act being processed [ActIds/MinAttend instance]
    act_act: act being processed [Act instance]
    check_vars_act: checking criteria of the Act instance [dictionary]
    check_vars_act_ids: checking criteria of the ActIds instance [dictionary]
    adopt_var: 
    RETURN
    True if the act respects the criteria and False otherwise [boolean]
    """
    for key, value in check_vars_act.iteritems():
        #greater than: "nb_lectures__gt": 1
        if key[-4:]=="__gt":
            #acts.q57: Pourcentage d'actes avec plusieurs bases juridiques
            if query=="base_j":
                bj=check_bj(act_act.base_j)
                if not bj:
                    return False
            elif getattr(act_act, key[:-4])<=value:
                return False
        #greater than or equal: "nb_lectures__gte": 1
        elif key[-5:]=="__gte":
            if getattr(act_act, key[:-5])<value:
                return False
        #nb_lectures__in
        elif key[-4:]=="__in":
            if getattr(act_act, key[:-4]) not in value:
                return False
        elif getattr(act_act, key)!=value:
            return False
                
    for key, value in check_vars_act_ids.iteritems():
        #acts.q132 no_unique_type <> COD
        if key[-4:]=="__in":
            if getattr(act, key[:-4]) not in value:
                return False
        elif getattr(act, key)!=value:
            return False

    #adopt_var is not None -> check if AdoptCSContre=Y or AdoptCSAbs=Y
    #nb_adopt_var -> if not None, it means we check that AdoptCSContre=Y or AdoptCSAbs=Y AND that there is a certain number of countries (1EM, 2 EM, 3EM)
    if adopt_var is not None:
        #check that AdoptCSContre=Y or AdoptCSAbs=Y
        if nb_adopt_var is None:
            #~ print act_act
            #~ print "adopt?"
            if not getattr(act, adopt_var).exists():
                #~ print "adopt=yes"
                return False
        else:
            #check that AdoptCSContre=Y or AdoptCSAbs=Y AND that there is a certain number of countries (1EM, 2 EM, 3EM)
            #adopt_cs.q77: Pourcentage d’actes adoptés avec opposition de deux deux états
            countries=getattr(act_act, adopt_var)
            #~ print "nb_adopt_var", nb_adopt_var
            #~ print "len(countries.all())", len(countries.all())
            if len(countries.all())!=nb_adopt_var:
                return False

    return True


def get_division_res(act, num_vars, denom_vars, operation):
    """
    FUNCTION
    get the result of the division of two numbers, with up to two variables for the numerator (num_vars) and two variables for the denominator (denom_vars)
    PARAMETERS
    act: act being processed [ActIds/MinAttend instance]
    num_vars: variables to use for the numerator [list of strings]
    denom_vars: variables to use for the denominator [list of strings]
    operation: operation to perform for both the numerator and denominator if they have more than one variable (addition or soustraction) [string]
    RETURN
    res: result of the division [float]
    """
    res=0
    num=0
    denom=1

    #get the values of each variable for the act in parameter, for both the numerator and denominator
    values=[]
    values.append(getattr(act, num_vars[0]))
    values.append(getattr(act, denom_vars[0]))
    #2 variables in the numerator and 2 in the denominator
    if len(num_vars)==2:
        values.append(getattr(act, num_vars[1]))
        values.append(getattr(act, denom_vars[1]))
        
    #only one variable in the numerator and one in the denominator
    if len(num_vars)==1:
        #q111: Nombre moyen de EPComAmdtAdopt / EPComAmdtTabled
        num=values[0]
        denom=values[1]
    #2 variables in the numerator and 2 in the denominator
    else:
        #q106: Nombre moyen [(EPComAmdtAdopt+EPAmdtAdopt) / (EPComAmdtTabled+EPAmdtTabled)] 
        if operation=="+":
            num=values[0]+values[2]
            denom=values[1]+values[3]
        #q113: Nombre moyen de (amdt_adopt - com_amdt_adopt) / (amdt_tabled - com_amdt_tabled)
        else:
            num=values[0]-values[2]
            denom=values[1]-values[3]
        #~ #TEST
        #~ if num<0 or denom<0:
            #~ print "negative num or denom", act
        #if amdt=com_amdt (numerator or denominator = 0), 
        if denom==0 or num==0:
            #~ print "null num or denom", act
            num=values[0]
            denom=values[1]

    #if denom=0 -> 0    
    if denom!=0:
        res=float(num)/denom
    
    return res


def get_average_res(vals):
    """
    FUNCTION
    get the average of a set of numbers given in parameter
    PARAMETERS
    vals: set of values to be used for the average computation [list of integers]
    RETURN
    value: result of the average [float]
    """
    #~ print vals
    num=0
    denom=0

    for val in vals:
        if val>0:
            num+=val
            denom+=1

    value=float(num)/denom

    #~ print value
    
    return value
    

def get_all_pfs(act, pers_type, nb_pers):
    """
    FUNCTION
    get the different party_family variables of all the rapps or resps of the act in parameter
    PARAMETERS
    act: act being processed [Act instance]
    pers_type: "rapp" or "resp" [string]
    nb_pers: nb of rapps or resps [int]
    RETURN
    pfs: different party_family variables of all the rapps or resps of the act in parameter [list of strings]
    """
    pfs=set()
    #get all rapps or resps
    for i in range(1, nb_pers+1):
        pers=getattr(act, pers_type+"_"+str(i))
        #no more rapp or resp
        if pers is None:
            break
        else:
            pf=PartyFamily.objects.get(country=pers.country, party=pers.party).party_family.strip().encode("utf-8")
            pfs.add(pf)
    return pfs


def compare_all_rapp_resp(act):
    """
    FUNCTION
    check if all the rapps and resps of the act in parameter have the same party family
    PARAMETERS
    act: act being processed [Act instance]
    RETURN
    same: True if all the rapps and resps have the same party family, False otherwise [boolean]
    """
    pfs_rapp=get_all_pfs(act, "rapp", nb_rapps)
    pfs_resp=get_all_pfs(act, "resp", nb_resps)
    #same=True if all the rapps and resps have the same party family, False otherwise
    same=True

    #if there is at least one rapp and one resp
    if pfs_rapp and pfs_resp:
        for pf_rapp in pfs_rapp:
            #we have found at least two different parties -> exit the function
            if not same:
                break
            for pf_resp in pfs_resp:
                #if there are at least two different party families (one from the rapps, one from the resps)
                if pf_rapp!=pf_resp:
                    same=False
                    break
    return same

    
def copy_res(res):
    """
    FUNCTION
    copy the temporary result of a specific factor to evaluate (specific year and / or specific cs, specific period, etc.)
    PARAMETERS
    res: temporary result of the specific factor [int, list if ints]
    RETURN
    res_copy: copy of the subfactor temporary result [int, list if ints]
    """
    #copy data for computation
    return copy.copy(res)


def compute_no_minister(act_act, res_temp, query):
    """
    FUNCTION
    compute the result of the query q122 (Pourcentage d'actes avec au moins un EM sans statut 'M')
    PARAMETERS
    act_act: act being processed [Act instance]
    res_temp: temporary result of the specific factor [int, list if ints]
    query: name of the specific query to realize [string]
    RETURN
    res_temp: updated temporary result of the subfactor [int, list if ints]
    """
    attendances=MinAttend.objects.filter(act=act_act)
    total=0
    if attendances:
        #store statuses for each country
        statuses={}
        for attendance in attendances:
            country=attendance.country
            country_code=country.country_code
            if country_code not in statuses:
                statuses[country_code]=[]
            status=Status.objects.get(verbatim=attendance.verbatim, country=country).status
            #don't take into account "NA" and "AB" statuses
            if status not in ["NA", "AB"]:
                #nb of acts with at least one attendance
                if query=="nb_attendances":
                    res_temp+=1
                    return res_temp
                statuses[country_code].append(status)

        #counter nb countries with no M
        nb_no_m=0
        #for each country:
        for country, status_list in statuses.iteritems():
            #if there is at least one CS or CS_PR for the country:
            if status_list:
                #the act can be taken into account for the percentage computation (it has attendances and at least one M or one CS or one CS_PR)
                total=1
                #if there is no M for the country
                if "M" not in status_list:
                    #~ print "no M for country", country
                    if query=="no_minister_percent":
                        res_temp[0]+=1
                        #there is no M for at least one country -> no need to check the rest of the data and we can now check the next act
                        break
                    elif query=="no_minister_nb_1":
                        res_temp+=1
                        #there is no M for at least one country -> no need to check the rest of the data and we can now check the next act
                        break
                    elif query=="no_minister_nb_2":
                        nb_no_m+=1
                        #at least two countries have no M status
                        if nb_no_m==2:
                            res_temp+=1
                            break

    #the act can be taken into account for the percentage computation (it has attendances and at least one M or one CS or one CS_PR)
    if query=="no_minister_percent":
        res_temp[1]+=total
                        
    return res_temp


def compute_groupvote_majority(res, groupvote, variable):
    groups={"ALDE/ADLE": 66, "GREENS/EFA": 29, "GUE-NGL": 27, "IND/DEM": 15, "NI": 20, "PPE": 192, "PSE": 145, "UEN": 29}

    for group, value in groups.iteritems():
        if groupvote == group:
            res[1]+=1
            if int(variable)>=value:
                #~ print variable, value
                res[0]+=1
            break
    
    return res


def compute_groupvote(act_act, res_temp, groupvote, groupvote_var_index, query):
    groupnames=getattr(act_act, "group_vote_names")

    #there are group vote data for the current act
    if groupnames not in [None, ""]:
        index=-1
        #what's the index of the group we are looking for? (each group is separated with ";")
        groupnames=groupnames.replace("EPP", "PPE").replace("S&D", "PSE").split(";")

        #check that the group is part of the groups of the act
        for i, group in enumerate(groupnames):
            #~ print "group", group
            #~ print "groupvote", groupvote
            if group==groupvote:
                index=i
                break

        #if the group exists
        if index != -1:

            #groupgroupvote_vars: for each group: FOR; AGAINST; ABSTENTION; PRESENT; ABSENT; NON VOTERS; TOTAL MEMBERS; COHESION (semicolon-separated list)
            groupvote_vars=getattr(act_act, "group_vote_"+str(index)).split(";")
            
            variable=groupvote_vars[groupvote_var_index]
            #~ print "variable", variable

            if variable not in [None, "None", ""]:
                #query with majority requires votes higher than a given value (groupvote.q139)
                if query=="groupvote_majority":
                    res_temp=compute_groupvote_majority(res_temp, groupvote, variable)
                else:
                    res_temp[0]+=float(variable)
                    res_temp[1]+=1
                             
    return res_temp
    

def compute(Model, act_act, act, res_temp, value, count, variable=None, ok=None, same=None, res_total=None, query=None, groupvote=None, groupvote_var_index=None):
    """
    FUNCTION
    do the temporary computation of the current analysis of the current subfactor
    PARAMETERS
    Model: Model to use [Act/ActIds/MinAttend model]
    act_act: act being processed [Act instance]
    act: act being processed [ActIds instance]
    res_temp: temporary result of the specific factor [int, list if ints]
    value: value to add to the temporary result (1 if count or percentage computation, variable value if average computation) [int]
    count: True if need to count the number of occurences for percentage or average computation; False otherwise (used for simple count analysis) [boolean]
    variable: variable to use (for average computation) [string]
    ok: indicate whether an act respects the criteria of the analysis (for average computation) [boolean]
    same: indicate whether the rapps and resps variables of the current act have the same party family [boolean]
    res_total: store the temporary result of the total of each row / column (row / column analysis) [int]
    query: name of the specific query to realize [string]
    RETURN
    res_temp: updated temporary result of the subfactor [int, list if ints]
    res_total: updated temporary result of the total of each row / column (row / column analysis) [int]
    """
    #computation
    if count:
        #ministers' attendance query
        if Model==MinAttend:
            status=Status.objects.get(verbatim=act.verbatim, country=act.country).status
            if status not in ["NA", "AB"]:
                res_temp[1]+=1
                if status=="M":
                    res_temp[0]+=1
        else:
            #q122: Pourcentage d'actes avec au moins un EM sans statut 'M' (et au moins un 'CS' ou 'CS_PR')
            if query=="no_minister_percent":
                res_temp=compute_no_minister(act_act, res_temp, query)
            #acts.q138: group votes queries
            elif groupvote_var_index is not None:
                res_temp=compute_groupvote(act_act, res_temp, groupvote, groupvote_var_index, query)
            else:
                #if filter_current_act is False, don't take the act into account
                filter_current_act=True
                #acts.q108 filter nb point b is not null OR nb point a is not null
                if query=="pt_b_OR_a":
                    filter_current_act=check_var1_var2(act_act.nb_point_a, act_act.nb_point_b)

                if filter_current_act:
                    #~ print "res_temp", res_temp
                    res_temp[1]+=1
                    #check discordance: if there are at least two different party families (one from the rapps, one from the resps)
                    if same is not None:
                        if not same:
                            res_temp[0]+=value
                    elif variable is not None or ok:
                        res_temp[0]+=value
                    #~ else:
                        #~ print "pb"
    else:
        if res_total is not None and ok:
            #~ print act_act, res_total
            res_total+=1

        #q122: Nombre d'actes avec au moins un / au moins deux EM sans statut 'M' (et au moins un 'CS' ou 'CS_PR')
        if query in ["no_minister_nb_1", "no_minister_nb_2", "nb_attendances"]:
            res_temp=compute_no_minister(act_act, res_temp, query)
        elif ok:
            #~ print "youpi"
            res_temp+=value

    #~ print "get compute: res_temp", res_temp

    return res_temp, res_total


def update_res(factor, res, res_temp, cs=None, year=None, country=None):
    """
    FUNCTION
    update the dictionary subfactor
    PARAMETERS
    factor: factor of the analysis [string]
    res: subfactor dictionary [dictionary]
    res_temp: temporary result of the specific subfactor [int]
    cs: current cs subfactor if any [string]
    year: current year subfactor if any [int]
    country: current country subfactor if any [int]
    RETURN
    res: updated temporary result of the subfactor [int, list if ints]
    """
    #update res
    if factor in ["all", "periods"]:
        res=res_temp
    elif factor=="year":
        res[year]=res_temp
    elif factor=="cs":
        res[cs]=res_temp
    elif factor=="csyear":
        res[cs][year]=res_temp
    elif factor=="country":
        res[country]=res_temp
    return res


def get_all_year(factor, Model, res, act_act, act, value, count, adopt_var, variable, ok, same, res_total, query):
    """
    FUNCTION
    update the result dictionary with the current act ("all", "year" or "periods" analysis)
    PARAMETERS
    factor: factor of the analysis [string]
    Model: Model to use [Act/ActIds/MinAttend model]
    res: result dictionary [dictionary]
    act_act: act being processed [Act instance]
    act: act being processed [ActIds instance]
    value: value to add to the temporary result (1 if count or percentage computation, variable value if average computation) [int]
    count: True if need to count the number of occurences for percentage or average computation; False otherwise (used for simple count analysis) [boolean]
    adopt_var: when using adopt_cs_abs or adopt_cs_contre variables, this indicator tells the program to perform a different result computation [boolean]
    variable: variable to use (for average computation) [string]
    ok: indicate whether an act respects the criteria of the analysis (for average computation) [boolean]
    same: indicate whether the rapps and resps variables of the current act have the same party family [boolean]
    res_total: result dictionary of the total of each row / column (row / column analysis) [dictionary]
    query: name of the specific query to realize [string]
    RETURN
    res: updated result dictionary [dictionary]
    res_total: result dictionary of the total of each row / column (row / column analysis) [dictionary]
    """
    nb_css=1
    year=None
    res_subfactor=res
    
    if factor=="year":
        year=str(act_act.releve_annee)
        res_subfactor=res[year]

    #for each matching cs
    for nb in range(nb_css):
        #copy data for computation
        res_temp=copy_res(res_subfactor)
        #computation
        res_temp, res_total=compute(Model, act_act, act, res_temp, value, count, variable, ok, same, res_total=res_total, query=query)
        #copy data back to res dictionary (for final result)
        res=update_res(factor, res, res_temp, year=year)
    return res, res_total



def check_period(act_act, period):
    adopt_conseil=act_act.adopt_conseil
    if adopt_conseil>=period[1] and adopt_conseil<=period[2]:
        return True
    return False
    

def get_period(factor, Model, res, act_act, act, value, count, adopt_var, variable, ok, same, res_total, query, periods):
    #for each period
    for period in periods:
        #the act belongs to the current period -> process it
        if check_period(act_act, period):
            #copy data for computation
            res_temp=copy.copy(res[period[0]])
            #computation
            res_temp, res_total=compute(Model, act_act, act, res_temp, value, count, variable, ok, same, res_total=res_total, query=query)
            #copy data back to res dictionary (for final result)
            res[period[0]]=res_temp
    return res, res_total


def get_countries(factor, Model, res, act_act, act, value, count, adopt_var, ok, res_total):
    """
    FUNCTION
    update the result dictionary with the current act ("country" analysis)
    PARAMETERS
    factor: factor of the analysis [string]
    Model: Model to use [Act/ActIds/MinAttend model]
    res: result dictionary [dictionary]
    act_act: act being processed [Act instance]
    act: act being processed [ActIds instance]
    value: value to add to the temporary result (1 if count or percentage computation, variable value if average computation) [int]
    count: True if need to count the number of occurences for percentage or average computation; False otherwise (used for simple count analysis) [boolean]
    adopt_var: when using adopt_cs_abs or adopt_cs_contre variables, this indicator tells the program to perform a different result computation [boolean]
    ok: indicate whether an act respects the criteria of the analysis (for average computation) [boolean]
    res_total: result dictionary of the total of each row / column (row / column analysis) [dictionary]
    RETURN
    res: updated result dictionary [dictionary]
    res_total: result dictionary of the total of each row / column (row / column analysis) [dictionary]
    """
    countries=getattr(act_act, adopt_var)
    #for each country
    for country in countries.all():
        country_code=country.country_code
        #copy data for computation
        res_temp=copy_res(res[country_code])
        #computation
        res_temp, res_total=compute(Model, act_act, act, res_temp, value, count, ok=ok, res_total=res_total)
        #copy data back to res dictionary (for final result)
        res=update_res(factor, res, res_temp, country=country_code)
        
    return res, res_total


def get_cs_csyear(factor, Model, res, act_act, act, value, count, variable, ok, same, query):
    """
    FUNCTION
    update the result dictionary with the current act ("cs" or "csyear" analysis)
    PARAMETERS
    factor: factor of the analysis [string]
    Model: Model to use [Act/ActIds/MinAttend model]
    res: result dictionary [dictionary]
    act_act: act being processed [Act instance]
    act: act being processed [ActIds instance]
    value: value to add to the temporary result (1 if count or percentage computation, variable value if average computation) [int]
    count: True if need to count the number of occurences for percentage or average computation; False otherwise (used for simple count analysis) [boolean]
    variable: variable to use (for average computation) [string]
    ok: indicate whether an act respects the criteria of the analysis (for average computation) [boolean]
    same: indicate whether the rapps and resps variables of the current act have the same party family [boolean]
    query: name of the specific query to realize [string]
    RETURN
    res: updated result dictionary [dictionary]
    """
    #get all css
    css=get_all_css(act_act)

    year=None
    
    #if there is at least one non null css
    #for each cs
    for cs in css:
        res_subfactor=res[cs]
        if factor=="csyear":
            year=str(act_act.releve_annee)
            res_subfactor=res[cs][year]
        
        #copy data for computation
        res_temp=copy_res(res_subfactor)
        #computation
        res_temp, res_total=compute(Model, act_act, act, res_temp, value, count, variable, ok, same, query=query)
        #copy data back to res dictionary (for final result)
        res=update_res(factor, res, res_temp, cs=cs, year=year)

    return res


def get_act_type(factor, Model, res, act_act, act, value, count, variable, ok, same, query):
    """
    FUNCTION
    update the result dictionary with the current act ("act_type" analysis)
    PARAMETERS
    factor: factor of the analysis [string]
    Model: Model to use [Act/ActIds/MinAttend model]
    res: result dictionary [dictionary]
    act_act: act being processed [Act instance]
    act: act being processed [ActIds instance]
    value: value to add to the temporary result (1 if count or percentage computation, variable value if average computation) [int]
    count: True if need to count the number of occurences for percentage or average computation; False otherwise (used for simple count analysis) [boolean]
    variable: variable to use (for average computation) [string]
    ok: indicate whether an act respects the criteria of the analysis (for average computation) [boolean]
    same: indicate whether the rapps and resps variables of the current act have the same party family [boolean]
    query: name of the specific query to realize [string]
    RETURN
    res: updated result dictionary [dictionary]
    """
    key=get_act_type_key(act_act.type_acte)

    if key is not None:
    
        #copy data for computation
        res_temp=copy.copy(res[key])
        #computation
        res_temp, res_total=compute(Model, act_act, act, res_temp, value, count, variable, ok, same, query=query)
        #copy data back to res dictionary (for final result)
        res[key]=res_temp

    return res


def get_country_year(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query):
    countries=getattr(act_act, adopt_var)
    year=str(act_act.releve_annee)
    #for each country
    for country in countries.all():
        country_code=country.country_code
        #computation
        res[country_code][year], res_total=compute(Model, act_act, act, res[country_code][year], value, count, ok=ok, same=same, query=query)
    return res
                
def get_country_period(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, periods):
    countries=getattr(act_act, adopt_var)
    #for each country
    for country in countries.all():
        country_code=country.country_code
        for period in periods:
            if check_period(act_act, period):
                #computation
                res[country_code][period[0]], res_total=compute(Model, act_act, act, res[country_code][period[0]], value, count, ok=ok, same=same, query=query)
    return res


def get_country_cs(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query):
    countries=getattr(act_act, adopt_var)
    #get all css
    css=get_all_css(act_act)
    
    #for each country
    for country in countries.all():
        country_code=country.country_code
        for cs in css:
            #computation
            res[country_code][cs], res_total=compute(Model, act_act, act, res[country_code][cs], value, count, ok=ok, same=same, query=query)
    return res


def get_country_acttype(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query):
    key=get_act_type_key(act_act.type_acte)
    if key is not None:
        countries=getattr(act_act, adopt_var)
        #for each country
        for country in countries.all():
            country_code=country.country_code
            #computation
            res[country_code][key], res_total=compute(Model, act_act, act, res[country_code][key], value, count, ok=ok, same=same, query=query)
    return res
    

def get_dg_year(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query):
    dgs=get_all_dgs(act_act)
    year=str(act_act.releve_annee)
    #for each dg
    for dg in dgs:
        #computation
        res[dg][year], res_total=compute(Model, act_act, act, res[dg][year], value, count, ok=ok, same=same, query=query)
    return res

                
def get_dg_period(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, periods):
    dgs=get_all_dgs(act_act)
    #for each dg
    for dg in dgs:
        for period in periods:
            if check_period(act_act, period):
                #computation
                res[dg][period[0]], res_total=compute(Model, act_act, act, res[dg][period[0]], value, count, ok=ok, same=same, query=query)
    return res


def get_dg_cs(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query):
    dgs=get_all_dgs(act_act)
    #get all css
    css=get_all_css(act_act)
    
   #for each dg
    for dg in dgs:
        for cs in css:
            #computation
            res[dg][cs], res_total=compute(Model, act_act, act, res[dg][cs], value, count, ok=ok, same=same, query=query)
    return res


def get_dg_acttype(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query):
    key=get_act_type_key(act_act.type_acte)
    if key is not None:
        dgs=get_all_dgs(act_act)
        #for each dg
        for dg in dgs:
            #computation
            res[dg][key], res_total=compute(Model, act_act, act, res[dg][key], value, count, ok=ok, same=same, query=query)
    return res


def get_resppf_year(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total):
    pfs=get_all_resppfs(act_act)
    year=str(act_act.releve_annee)
    #for each pf
    for pf in pfs:
        #computation
        res[pf][year], res_total[year]=compute(Model, act_act, act, res[pf][year], value, count, ok=ok, same=same, query=query, res_total=res_total[year])
    return res, res_total

                
def get_resppf_period(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, periods, res_total):
    pfs=get_all_resppfs(act_act)
    #for each pf
    for pf in pfs:
        for period in periods:
            if check_period(act_act, period):
                #computation
                res[pf][period[0]], res_total[period[0]]=compute(Model, act_act, act, res[pf][period[0]], value, count, ok=ok, same=same, query=query, res_total=res_total[period[0]])
    return res, res_total


def get_resppf_cs(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total):
    pfs=get_all_resppfs(act_act)
    #get all css
    css=get_all_css(act_act)
    
    #for each pf
    for pf in pfs:
        for cs in css:
            #computation
            res[pf][cs], res_total[cs]=compute(Model, act_act, act, res[pf][cs], value, count, ok=ok, same=same, query=query, res_total=res_total[cs])
    return res, res_total


def get_resppf_acttype(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total):
    key=get_act_type_key(act_act.type_acte)
    if key is not None:
        pfs=get_all_resppfs(act_act)
        #for each pf
        for pf in pfs:
            #computation
            res[pf][key], res_total[key]=compute(Model, act_act, act, res[pf][key], value, count, ok=ok, same=same, query=query, res_total=res_total[key])
    return res, res_total


def get_perscountry_year(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total, pers):
    countries=get_all_perscountries(act_act, pers)
    year=str(act_act.releve_annee)
    #for each country
    for country in countries:
        #computation
        res[country][year], res_total[year]=compute(Model, act_act, act, res[country][year], value, count, ok=ok, same=same, query=query, res_total=res_total[year])
    return res, res_total

                
def get_perscountry_period(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, periods, res_total, pers):
    countries=get_all_perscountries(act_act, pers)
    #for each country
    for country in countries:
        for period in periods:
            if check_period(act_act, period):
                #computation
                res[country][period[0]], res_total[period[0]]=compute(Model, act_act, act, res[country][period[0]], value, count, ok=ok, same=same, query=query, res_total=res_total[period[0]])
    return res, res_total


def get_perscountry_cs(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total, pers):
    countries=get_all_perscountries(act_act, pers)
    #get all css
    css=get_all_css(act_act)
    
    #for each country
    for country in countries:
        for cs in css:
            #computation
            res[country][cs], res_total[cs]=compute(Model, act_act, act, res[country][cs], value, count, ok=ok, same=same, query=query, res_total=res_total[cs])
    return res, res_total


def get_perscountry_acttype(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total, pers):
    key=get_act_type_key(act_act.type_acte)
    if key is not None:
        countries=get_all_perscountries(act_act, pers)
        #for each country
        for country in countries:
            #computation
            res[country][key], res_total[key]=compute(Model, act_act, act, res[country][key], value, count, ok=ok, same=same, query=query, res_total=res_total[key])
    return res, res_total


def get_rappgroup_year(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total):
    groups=get_all_rappgroups(act)
    year=str(act_act.releve_annee)
    #for each group
    for group in groups:
        #computation
        res[group][year], res_total[year]=compute(Model, act_act, act, res[group][year], value, count, ok=ok, same=same, query=query, res_total=res_total[year])
    return res, res_total

                
def get_rappgroup_period(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, periods, res_total):
    groups=get_all_rappgroups(act)
    #for each group
    for group in groups:
        for period in periods:
            if check_period(act_act, period):
                #computation
                res[group][period[0]], res_total[period[0]]=compute(Model, act_act, act, res[group][period[0]], value, count, ok=ok, same=same, query=query, res_total=res_total[period[0]])
    return res, res_total


def get_rappgroup_cs(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total):
    groups=get_all_rappgroups(act)
    #get all css
    css=get_all_css(act_act)
    
    #for each group
    for group in groups:
        for cs in css:
            #computation
            res[group][cs], res_total[cs]=compute(Model, act_act, act, res[group][cs], value, count, ok=ok, same=same, query=query, res_total=res_total[cs])
    return res, res_total


def get_rappgroup_acttype(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total):
    key=get_act_type_key(act_act.type_acte)
    if key is not None:
        groups=get_all_rappgroups(act)
        #for each group
        for group in groups:
            #computation
            res[group][key], res_total[key]=compute(Model, act_act, act, res[group][key], value, count, ok=ok, same=same, query=query, res_total=res_total[key])
    return res, res_total

    
def get_groupvote_year(factor, Model, res, act_act, act, value, count, variable, ok, same, query, groupvote_var_index):

    year=str(act_act.releve_annee)
    for groupvote in groupvotes:

        #~ print "year", year
        #~ print "groupvote", groupvote
        
        #copy data for computation
        res_temp=copy.copy(res[groupvote][year])
        #computation
        res_temp, res_total=compute(Model, act_act, act, res_temp, value, count, variable, ok, same, query=query, groupvote=groupvote, groupvote_var_index=groupvote_var_index)
        #copy data back to res dictionary (for final result)
        res[groupvote][year]=res_temp

    return res


def get_groupvote_period(factor, Model, res, act_act, act, value, count, variable, ok, same, query, groupvote_var_index, periods):
    for groupvote in groupvotes:
        for period in periods:
            if check_period(act_act, period):
                #copy data for computation
                res_temp=copy.copy(res[groupvote][period[0]])
                #computation
                res_temp, res_total=compute(Model, act_act, act, res_temp, value, count, variable, ok, same, query=query, groupvote=groupvote, groupvote_var_index=groupvote_var_index)
                #copy data back to res dictionary (for final result)
                res[groupvote][period[0]]=res_temp

    return res


def get_groupvote_cs(factor, Model, res, act_act, act, value, count, variable, ok, same, query, groupvote_var_index):
    #get all css
    css=get_all_css(act_act)
    
    for groupvote in groupvotes:
        for cs in css:
            #computation
            res_temp, res_total=compute(Model, act_act, act, res[groupvote][cs], value, count, variable, ok, same, query=query, groupvote=groupvote, groupvote_var_index=groupvote_var_index)
            #copy data back to res dictionary (for final result)
            res[groupvote][cs]=res_temp

    return res


def get_groupvote_acttype(factor, Model, res, act_act, act, value, count, variable, ok, same, query, groupvote_var_index):
    key=get_act_type_key(act_act.type_acte)
    if key is not None:
        for groupvote in groupvotes:
            #computation
            res[groupvote][key], res_total=compute(Model, act_act, act, res[groupvote][key], value, count, variable, ok, same, query=query, groupvote=groupvote, groupvote_var_index=groupvote_var_index)
    return res


    
def check_var1_var2(val_1, val_2):
    """
    FUNCTION
    check that at least one of the two values in parameters contains a real value (not None and greater than zero)
    PARAMETERS
    val_1: first value to check [int]
    val_2: second value to check [int]
    RETURN
    check: True if there is at least one not none and greater than 0 value, False otherwise [boolean]
    """
    if val_1 in [None, 0] and val_2 in [None, 0]:
        return False
    return True
    

def get(factor, res, Model=Act, count=True, variable=None, variable_2=None, excluded_values=[None, ""], filter_vars_acts={}, filter_vars_acts_ids={}, exclude_vars_acts={},check_vars_acts={}, check_vars_acts_ids={}, query=None, adopt_var=None, nb_adopt_var=None, num_vars=None, denom_vars=None, operation=None, res_total=None, periods=None, groupvote_var_index=None, pers=None):
    """
    FUNCTION
    update and get the result dictionary with all the acts
    PARAMETERS
    factor: factor of the analysis [string]
    res_init: initialized result dictionary [dictionary]
    Model: Model to use [Act/ActIds/MinAttend model]
    count: True if need to count the number of occurences for percentage or average computation; False otherwise (used for simple count analysis) [boolean]
    variable: variable to use (for average computation) [string]
    variable_2: second variable to use (for average computation) [string]
    excluded_values: when a variable is used for the analyse, check that its value is not to be excluded [list]
    filter_vars_acts: filtering criteria from the Act model [dictionary]
    filter_vars_acts_ids: filtering criteria from the ActIds model [dictionary]
    exclude_vars_acts: excluding criteria from the Act model [dictionary]
    check_vars_acts: checking criteria from the Act model [dictionary]
    check_vars_acts_ids: checking criteria from the ActIds model [dictionary]
    query: name of the specific query to realize [string]
    adopt_var: when using adopt_cs_abs or adopt_cs_contre variables, this indicator tells the program to perform a different result computation [boolean]
    nb_adopt_var is: we check that AdoptCSContre=Y or AdoptCSAbs=Y AND that there is a certain number of countries (1EM, 2 EM, 3EM)
    num_vars: for division queries, list of numerator variables [list of strings]
    denom_vars: for division queries, list of denominator variables [list of strings]
    operation: for division queries, operation to perform for the numerator and the denominator [string]
    res_total_init: result dictionary of the total of each row / column (row / column analysis) [dictionary]
    periods: periods to use for the periods analysis [tuple of tuples of strings]
    RETURN
    res: final result dictionary [dictionary]
    """
    same=None

    filter_vars=get_include_filter(Model, filter_vars_acts=filter_vars_acts, filter_vars_acts_ids=filter_vars_acts_ids)
    exclude_vars=get_exclude_filter(Model, factor, exclude_vars_acts, exclude_vars_acts_ids={})

    #for each act
    #~ print "filter_vars", filter_vars
    #~ print "exclude_vars", exclude_vars
    #~ print Model.objects.filter(**filter_vars).exclude(**exclude_vars).query
    for act in Model.objects.filter(**filter_vars).exclude(**exclude_vars):
        ok=True
        act_act=get_act(Model, act)

        value=1
        if variable is not None:
            value=getattr(act, variable)
            if variable_2 is not None:
                value_2=getattr(act, variable_2)
                ok=check_var1_var2(value, value_2)
        if (value not in excluded_values and ok) or (variable_2 not in excluded_values and ok):
            ok=check_vars(act, act_act, check_vars_acts, check_vars_acts_ids, adopt_var, nb_adopt_var, query=query)
            #~ print act_act
            #~ print ok
            #~ print ""

            #division mode, res=num/denom -> q111: #Nombre moyen de EPComAmdtAdopt / EPComAmdtTabled
            if num_vars is not None:
                value=get_division_res(act_act, num_vars, denom_vars, operation)
            #"1+2" with at least one non null value -> q100: Moyenne EPVotesFor1-2
            elif variable_2 is not None:
                value=get_average_res([value, value_2])
            #get percentage of different political families for rapp1 and resp1
            elif query=="discordance":
                same=compare_all_rapp_resp(act_act)

            if factor in ["all", "year"]:
                res, res_total=get_all_year(factor, Model, res, act_act, act, value, count, adopt_var, variable, ok, same, res_total, query)

            elif factor=="period":
                res, res_total=get_period(factor, Model, res, act_act, act, value, count, adopt_var, variable, ok, same, res_total, query, periods)
                
            elif factor=="country":
                res, res_total=get_countries(factor, Model, res, act_act, act, value, count, adopt_var, ok, res_total)
                
            elif factor in ["cs", "csyear"]:
                res=get_cs_csyear(factor, Model, res, act_act, act, value, count, variable, ok, same, query)
                
            elif factor=="act_type":
                res=get_act_type(factor, Model, res, act_act, act, value, count, variable, ok, same, query)


            elif factor=="country_year":
                res=get_country_year(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query)

            elif factor=="country_period":
                res=get_country_period(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, periods)

            elif factor=="country_cs":
                res=get_country_cs(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query)

            elif factor=="country_acttype":
                res=get_country_acttype(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query)


            elif factor=="dg_year":
                res=get_dg_year(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query)

            elif factor=="dg_period":
                res=get_dg_period(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, periods)

            elif factor=="dg_cs":
                res=get_dg_cs(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query)

            elif factor=="dg_acttype":
                res=get_dg_acttype(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query)


            elif factor=="resppf_year":
                res, res_total=get_resppf_year(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total)

            elif factor=="resppf_period":
                res, res_total=get_resppf_period(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, periods, res_total)

            elif factor=="resppf_cs":
                res, res_total=get_resppf_cs(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total)

            elif factor=="resppf_acttype":
                res, res_total=get_resppf_acttype(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total)


            elif factor=="perscountry_year":
                res, res_total=get_perscountry_year(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total, pers)

            elif factor=="perscountry_period":
                res, res_total=get_perscountry_period(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, periods, res_total, pers)

            elif factor=="perscountry_cs":
                res, res_total=get_perscountry_cs(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total, pers)

            elif factor=="perscountry_acttype":
                res, res_total=get_perscountry_acttype(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total, pers)


            elif factor=="rappgroup_year":
                res, res_total=get_rappgroup_year(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total)

            elif factor=="rappgroup_period":
                res, res_total=get_rappgroup_period(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, periods, res_total)

            elif factor=="rappgroup_cs":
                res, res_total=get_rappgroup_cs(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total)

            elif factor=="rappgroup_acttype":
                res, res_total=get_rappgroup_acttype(factor, Model, res, act_act, act, value, count, adopt_var, ok, same, query, res_total)

                
            elif factor=="groupvote_year":
                res=get_groupvote_year(factor, Model, res, act_act, act, value, count, variable, ok, same, query, groupvote_var_index)

            elif factor=="groupvote_period":
                res=get_groupvote_period(factor, Model, res, act_act, act, value, count, variable, ok, same, query, groupvote_var_index, periods)

            elif factor=="groupvote_cs":
                res=get_groupvote_cs(factor, Model, res, act_act, act, value, count, variable, ok, same, query, groupvote_var_index)

            elif factor=="groupvote_acttype":
                res=get_groupvote_acttype(factor, Model, res, act_act, act, value, count, variable, ok, same, query, groupvote_var_index)

    print "res", res
        
    if res_total is not None:
        return res, res_total
    
    return res


#NOT UP-TO-DATE!!!
def get_month(res, variable, count=True, filter_vars_acts={}):
    """
    FUNCTION
    update and get the result dictionary with all the acts for a months analysis
    PARAMETERS
    res: initialized result dictionary [dictionary]
    variable: variable to use (for average computation) [string]
    count: True if need to count the number of occurences for percentage or average computation; False otherwise (used for simple count analysis) [boolean]
    filter_vars_acts: filtering criteria from the Act model [dictionary]
    RETURN
    res: final result dictionary [dictionary]
    """
    for act_id in ActIds.objects.filter(src="index", act__validated=2, **filter_vars_acts):
        act=act_id.act
        value=getattr(act, variable)
        if value>0:
            month=str(act.releve_mois)
            if count:
                res[month][1]+=1
                res[month][0]+=value
            else:
                res[month]+=value

    print "res", res
    return res


#NOT UP-TO-DATE!!!
def get_list_pers_year(res, pers_type, max_nb, filter_vars_acts={}):
    """
    FUNCTION
    get the list of persons with their related data and number of occurences for the year analysis (q91 and q92)
    PARAMETERS
    res: initialized result dictionary [dictionary]
    pers_type: "rapp" or "resp" [string]
    max_nb: number of rapps or resps [int]
    filter_vars_acts: filtering criteria from the Act model [dictionary]
    RETURN
    res: final result dictionary [dictionary]
    """
    for act_ids in ActIds.objects.filter(act__validated=2, src="index", **filter_vars_acts):
        act=act_ids.act
        year=str(act.releve_annee)
        #loop over each pers
        for nb in range(1, max_nb+1):
            pers=getattr(act, pers_type+"_"+str(nb))
            if pers not in [None, 0]:
                if pers not in res[year]:
                    res[year][pers]=1
                else:
                    res[year][pers]+=1
    return res


#NOT UP-TO-DATE!!!
def get_list_pers_cs(res, pers_type, max_nb, year_var=False, filter_vars_acts={}):
    """
    FUNCTION
    get the list of persons with their related data and number of occurences for the cs and csyear analysis (q91 and q92)
    PARAMETERS
    res: initialized result dictionary [dictionary]
    pers_type: "rapp" or "resp" [string]
    max_nb: number of rapps or resps [int]
    year_var: True if year is a subfactor (csyear analysis), False otherwise [boolean]
    filter_vars_acts: filtering criteria from the Act model [dictionary]
    RETURN
    res: final result dictionary [dictionary]
    """
    for act_ids in ActIds.objects.filter(act__validated=2, src="index", **filter_vars_acts):
        act=act_ids.act
        #loop over each cs
        for nb in range(1,nb_css+1):
            code_sect=getattr(act, "code_sect_"+str(nb))
            if code_sect is not None:
                cs=get_cs(code_sect.code_sect)
                year=str(act.releve_annee)

                #loop over each pers
                for nb in range(1, max_nb+1):
                    pers=getattr(act, pers_type+"_"+str(nb))
                    #by cs and by year
                    if year_var:
                        if pers not in [None, 0]:
                            if pers not in res[cs][year]:
                                res[cs][year][pers]=1
                            else:
                                res[cs][year][pers]+=1
                    #by cs
                    else:
                        if pers not in [None, 0]:
                            if pers not in res[cs]:
                                res[cs][pers]=1
                            else:
                                res[cs][pers]+=1
    return res


def get_pf(pers):
    """
    FUNCTION
    get the party_family variable of the person (rapp or resp) in parameter
    PARAMETERS
    pers: "rapp" or "resp" instance [Person instance]
    RETURN
    party_family: party_family of the person [string]
    """
    return PartyFamily.objects.get(country=pers.country, party=pers.party).party_family.encode("utf-8")


def get_stat(var, pers):
    """
    FUNCTION
    get the party_family or country variable of the person (rapp or resp) in parameter
    PARAMETERS
    var: "pf" or "country" [string]
    pers: "rapp" or "resp" instance [Person instance]
    RETURN
    stat: party_family or country code of the person [string]
    """
    #statistics on party family
    if var=="pf":
        stat=get_pf(pers)
    #statistics on country
    else:
        stat=pers.country.country_code
    return stat


#NOT UP-TO-DATE!!!
def get_percent_pers_year(res, pers_type, max_nb, var="pf", filter_vars={}):
    """
    FUNCTION
    get percentage of each party family or country for Rapporteurs and RespPropos for the year analysis (q93 and q94)
    PARAMETERS
    res: initialized result dictionary [dictionary]
    pers_type: "rapp" or "resp" [string]
    max_nb: number of rapps or resps [int]
    var: "pf" or "country" [string]
    filter_vars_acts: filtering criteria from the Act model [dictionary]
    RETURN
    res: final result dictionary [dictionary]
    """
    #year only
    filter_vars=get_validated_acts(ActIds, filter_vars)
    for act_ids in ActIds.objects.filter(**filter_vars):
        act=act_ids.act
        year=str(act.releve_annee)
        #loop over each pers
        for nb in range(1, max_nb+1):
            pers=getattr(act, pers_type+"_"+str(nb))
            if pers is not None:
                stat=get_stat(var, pers)
                res[year]["total"]+=1
                if stat not in res[year]:
                    res[year][stat]=1
                else:
                    res[year][stat]+=1
    print "res", res
    return res
    

#NOT UP-TO-DATE!!!
def get_percent_pers_cs(res, pers_type, max_nb, var="pf", year_var=False, filter_vars={}):
    """
    FUNCTION
    get percentage of each party family or country for Rapporteurs and RespPropos for the cs or csyear analysis (q93 and q94)
    PARAMETERS
    res: initialized result dictionary [dictionary]
    pers_type: "rapp" or "resp" [string]
    max_nb: number of rapps or resps [int]
    var: "pf" or "country" [string]
    year_var: True if year is a subfactor (csyear analysis), False otherwise [boolean]
    filter_vars_acts: filtering criteria from the Act model [dictionary]
    RETURN
    res: final result dictionary [dictionary]
    """
    #cs only / cs and year
    filter_vars=get_validated_acts(ActIds, filter_vars)
    for act_ids in ActIds.objects.filter(**filter_vars):
        act=act_ids.act
        #loop over each cs
        for nb in range(1,nb_css+1):
            code_sect=getattr(act, "code_sect_"+str(nb))
            if code_sect is not None:
                cs=get_cs(code_sect.code_sect)
                year=str(act.releve_annee)

                #loop over each pers
                for nb in range(1, max_nb+1):
                    pers=getattr(act, pers_type+"_"+str(nb))
                    if pers is not None:
                        stat=get_stat(var, pers)
                        #by cs and by year
                        if year_var:
                            res[cs][year]["total"]+=1
                            if stat not in res[cs][year]:
                                res[cs][year][stat]=1
                            else:
                                res[cs][year][stat]+=1
                        #by cs
                        else:
                            res[cs]["total"]+=1
                            if stat not in res[cs]:
                                res[cs][stat]=1
                            else:
                                res[cs][stat]+=1
    print "res", res
    return res


def check_bj(base_j):
    """
    FUNCTION
    check if the base_j field contains only one or many bases juridiques (q121)
    PARAMETERS
    base_j: base_j field [string]
    RETURN
    True if th field countains many bases juridiques, False otherwise [boolean]
    """
    if base_j.find(';')>0:
        return True
    return False
    

def get_list_acts(Model, search, cs, fields):
    """
    FUNCTION
    get a list of fields of acts matching searching criteria (q120, q121)
    PARAMETERS
    Model: model to use for the query [Act/ActIds model]
    search: acts with a specific cs OR with many bases juridiques
    cs: specific cs to analyze [string]
    fields: fields of the acts to retrive [list of strings]
    RETURN
    acts: list of the fields of acts matching searching criteria [list of ints or integers]
    """
    acts=[]
    filter_vars=get_validated_acts(Model)
    if search=="cs":
        css=[cs]
    
    for act in Model.objects.filter(**filter_vars):
        act_act=get_act(Model, act)
        #search for acts with a specific cs
        if search=="cs":
            #if there is at least one matching cs
            ok=check_css(act_act, css)
        #search for acts with multiple bases juridiques
        elif search=="bj":
            ok=check_bj(act_act.base_j)

        if ok:
            act_fields=[]

            #act ids
            act_fields.extend([act_act.releve_annee, act_act.releve_mois, act_act.no_ordre])
            
            for field in fields:
                #ActIds
                if field=="propos_origine":
                    act_field=getattr(act, field)
                #Act
                else:
                    #NP
                    if field=="np":
                        act_field=act_act.np_set.all()
                        #~ print act_field
                    else:
                        act_field=getattr(act_act, field)
                        #accents problems
                        if field=="titre_rmc":
                            act_field=act_field.encode("utf-8")
                    #adopt_cs variables
                    if ("adopt_cs" in field or field=="np") and act_field is not None:
                        temp=""
                        for country in act_field.all():
                            if field=="np":
                                country=country.np
                            temp+=country.country_code+"; "
                        act_field=temp[:-2]
                act_fields.append(act_field)
            acts.append(act_fields)

    return acts


def get_list_acts_by_year_and_dg_or_resp(res, var_name, nb):
    Model=Act
    filter_vars=get_validated_acts(Model)
    #adoption_propos_origine: from 2006 to 2013
    filter_vars["adopt_propos_origine__gte"]= str_to_date("2006-01-01")
    filter_vars["adopt_propos_origine__lte"]= str_to_date("2013-12-31")

    for act in Model.objects.filter(**filter_vars):
        act_act=get_act(Model, act)
        year=str(act_act.adopt_propos_origine.year)
        titre=act_act.titre_rmc.encode("utf-8")
        
        for index in range(1, nb+1):
            num=str(index)
            var=getattr(act_act, var_name+"_"+num)
            if var is not None:
                if var_name=="dg":
                    var=var.dg
                elif var_name=="resp":
                    var=var.name
                var=var.encode("utf-8")
                    
                if var not in res[year]:
                    res[year][var]=[titre]
                else:
                    res[year][var].append(titre)
                    
    return res
    
