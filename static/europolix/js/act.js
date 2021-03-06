/* act ids and data javascript functions */

//reset act form
function reset_act_form(result, mode)
{
    if (mode=="display")
    {
        //display act
        $('#act_form_div').html(result);

        /* if javascript activated, hide person update button (act data) */
        $('.update_person').hide();
        //display button to choose countries for adopt variables
        display_adopt_variables();
    }
    else
    {
        //reset form
        $('#act_form_div').load($("#reset_form_path").text(), function()
        {
            //on save: form valid -> displays success message
            if (mode=="save")
            {
                display_save_message(result);

                //go to the bottom of the page
                $('#top_anchor').click();

                /* if javascript activated, hide person update button (act data) */
                $('.update_person').hide();
            }
            
            //display button to choose countries for adopt variables
            display_adopt_variables();
        });
    }
    
}


//show django errors
function display_errors(errors, action)
{
    for (var key in errors)
    {
        if (key=="__all__")
        {
            $field=$("#id_"+action+key+"errors");
        }
        else
        {
            //~ alert(key);
            $field=$("#id_"+key+"_errors");
        }
        $field.html('<ul class="errorlist"><li>'+errors[key]+'</li></ul>');
    }
}

/* get maximum height of a set of elements */
function get_max_height_divs(elements)
{
    return Math.max.apply(null, elements.map(function ()
    {
        //~ alert($(this).attr("id") + " " + $(this).height());
        return $(this).height();
    }).get());
}


//handle django view return (act ids and act data) when displaying an act from the drop down list (add form) or mdifying an act (modif form)
function display_or_update_result(result, action, ids)
{
    //add mode -> an act has been selected in the drop down list
    if (action=="add_act")
    {
        //reset add and modif form
        reset_add("errors", "no");
        reset_modif("all");
    }
    else if(action=="modif_act")
    {
        //reset add and modif form
        reset_add("all", "no");
        reset_modif("errors");
    }

    //validation errors
    if(result.hasOwnProperty(action+'_errors'))
    {
        //reset act form except if click on update button
        if(!result.update_act_errors)
        {
            //reset act form
            reset_act_form(result, "reset");
        }

        //append current errors to the html form
        errors=eval(result[action+"_errors"]);
        display_errors(errors, action);

        //ajust height divs for the modif
        if (action=="modif_act")
        {
            /* releve ids or propos ids to modify an act? */
            error_div=".modif_errors_"+ids
            max_height=get_max_height_divs($(error_div))
            //update height radio button
            $("#"+ids+"_ids "+error_div).height(max_height);
            
             //~ alert("radio: "+ids+", max height: "+max_height);
            
            
            /* using propos ids to modify an act */
            if (ids=="propos")
            {
                /*height for the modif button*/
                max_height=max_height/2;
            }

            //update height  modif button
            $("#modif_act_button_div "+error_div).height(max_height);

        }
    }
    else
    {
        //display act in act form
        if(!result.modif_act_errors)
        {
            reset_act_form(result, "display");
        }
    }
    
    var adopts=["cs_contre", "pc_contre", "cs_abs", "pc_abs"]
    //populate the multiple select list (gentleSelect plugin) with the countries selected in the drop down lists, for each adopt variables
    $.each(adopts , function(i) 
    { 
        txt=""
        $(".adopt_"+adopts[i]+"_ :selected").each(function(index) 
        {
            //~ console.log(i, adopts[i]);
            if(this.value!="")
            {
                 $("#"+adopts[i]+"_div .gentleselect-dialog li:contains("+$(this).text()+")").toggleClass("selected");
                txt+=$(this).text()+", "
            }
        });
            if(txt!="")
                $("#"+adopts[i]+"_div .gentleselect-label").html(txt.slice(0, -2));
    });
  
}


//handle django view return (act ids and act data) when saving an act
function save_result(result)
{
    //form not valid -> displays errors
    if (result.save_act_errors)
    {
        if (result.mode=="add")
        {
            //reset modif form
            reset_modif("all");
        }

        //append current errors to the html form
        errors=result.save_act_errors;
        display_errors(errors, "update_act");
        display_save_message(result);
    }
    else
    {
        //display act in act form
        reset_act_form(result, "save");
        //reset add and modif form
        if (result.mode=="add")
        {
            reset_add("all", "yes");
        }
        else
        {
            reset_add("all", "no");
        }
        reset_modif("all");
    }
}

/* add of an act (selection from drop down list) */
$("#id_act_to_validate").change(function(event)
{
    display_or_update_act("add_act", event);
});


/* modification or update of an act (act ids form) */
$('#act_form').on('click', '#modif_act, #update_act', function(event)
{
    var ids;
    if ($(this).attr('name')=="modif_act")
    {
        //tells the view we are trying to modif an act
        $('#modif_button_clicked').val('yes');
        /* releve ids or propos ids ? */
        ids=$("input:radio[name=ids_radio]:checked").val();
    }
    display_or_update_act($(this).attr('name'), event, ids);
});


/* display/modif or update the ids/datas of the selected act */
function display_or_update_act(button_name, event, ids)
{
    //do not follow the href link
    event.preventDefault();

    //show loading gif
    $("#loading_gif_"+button_name).show();
    
    form=$('#act_form');
    var form_data=form.serialize();
    form_data+="&"+button_name+"=''";
    
    //~ alert("add act display function begin");
      
    xhr=$.ajax
    ({
        type: "POST",
        url: form.attr('action'),
        //~ dataType: 'html',
        data: form_data
    })
    .done(function(result) 
    {
        //if an act has been selected, either from the add form or the modif form
        if (result!="")
        {
            //display or mpdify an act
            display_or_update_result(result, button_name, ids);
        }
        //hide loading gif
        $("#loading_gif_"+button_name).hide();
        //~ alert("add act display function success end");
    })
    .fail(function() 
    {
        //~ alert( "ajax failure!");
        window.console&&console.log("ajax failure!");
    });
    
    //don't submit the form
    return false;
}


/* save an act*/
$('#act_form').on('click', '#save_act', function(event)
{
    save_act_form($("#act_form"), $(this), event);
});


//submit the act ids or data form to save it or display validation errors
function save_act_form(form, button, event)
{
    //do not follow the href link
    event.preventDefault();

    //loading state for the button (use bootstrap function)
    button.button('loading');
    //remove previous errors (from the previous run) -> modif form
    $('.errorlist').each(function()
    {
        $(this).remove();
    });
    
    if(form.hasClass( "data"))
    {
        var adopts=["cs_contre", "pc_contre", "cs_abs", "pc_abs"]
        //populate drop down lists of adopt variables with the countries chosen in the multiple select list, for each adopt variable
        $.each(adopts , function(i) 
        { 
            //get all the countries to be selected
            countries=$("#"+adopts[i]+"_div .gentleselect-label").html().split(",");
            
            //unselect previous countries
            $( ".adopt_"+adopts[i]+"_" ).val([])
            
            //select new countries
            $.each(countries , function(nb) 
            { 
                $("#id_adopt_"+adopts[i]+"_"+(nb+1)+" option:contains("+$.trim(countries[nb])+")").prop('selected',true);
            });
        });
    }

    var form_data=form.serialize();
    form_data+="&"+button.attr("id")+"=''";
    $.ajax
    ({
        type: 'POST',
        url: form.attr('action'),
        dataType: 'json',
        data: form_data,
        success: function(result)
        {
            //if an act has been selected, either from the add form or the modif form
            if (result!="")
            {
                //display success or error message
                save_result(result);
            }
            //stops the loading state of the button
            button.button('reset');
        }
    });

    //don't submit the form
    return false;
}


/* bind the event to update code_sects with the associated drop down list */
$('#act_form').on('change', '#code_sect_1_id, #code_sect_2_id, #code_sect_3_id, #code_sect_4_id', function()
{
    update_code_sect(this.id, this.value);
});

/* bind the event to update rapps with the associated drop down list */
$('#act_form').on('change', '#rapp_1_id, #rapp_2_id, #rapp_3_id, #rapp_4_id, #rapp_5_id', function()
{
    update_person(this.id, this.value, "rapp");
});

/* bind the event to update a dg with the associated drop down list */
$('#act_form').on('change', '#dg_1_id, #dg_2_id', function()
{
    update_dg(this.id, this.value);
});

/* bind the event to update resps with the associated drop down list */
$('#act_form').on('change', '#resp_1_id, #resp_2_id, #resp_3_id', function()
{
    update_person(this.id, this.value, "resp");
});

/* bind the event to update durations with the associated reload button (image) */
$('#act_form').on('click', '#update_durations', function(e)
{
    /* don't submit the form */
    e.preventDefault();
    /* make the button rotate and update the durations */
    update_durations(this.id);
});



/* update the code_agenda when a different code_sect is selected from the drop down list */
function update_code_sect(name, value)
{
    $.ajax
    ({
        type: 'POST',
        url: $("#code_sect").text(),
        dataType: 'json',
        data: "code_sect_id="+value,
        success: function(result)
        {
            //get the number of code_sect (code_sect_1_id, code_sect_2_id, code_sect_3_id, code_sect_4_id)
            id=name.slice(-4,-3);
            //get name of the variable
            code_aggenda_name=$("#code_agenda_"+id).text()
            code_aggenda_name=code_aggenda_name.substr(0, code_aggenda_name.indexOf('=')+1); 
            $("#code_agenda_"+id).text(code_aggenda_name+result.code_agenda);
        }
    });
}

/* update the code_sect variables when a different code_sect is selected from the drop down list */
function update_person(name, value, src)
{
    $.ajax
    ({
        type: 'POST',
        url: $("#person").text(),
        dataType: 'json',
        data: "person_id="+value+"&src="+src,
        success: function(result)
        {
            //get the number of person (1, 2, 3)
            id=name.slice(-4,-3);
            $("#"+src+"_country_"+id).text(result.country);
            $("#"+src+"_party_"+id).text(result.party);
            $("#"+src+"_party_family_"+id).text(result.party_family);
        }
    });
}

/* update the dg_sigle when a different dg is selected from the drop down list */
function update_dg(name, value)
{
    $.ajax
    ({
        type: 'POST',
        url: $("#dg").text(),
        dataType: 'json',
        data: "dg_id="+value,
        success: function(result)
        {
            //get the number of dg (dg_1_id, dg_2_id)
            id=name.slice(-4,-3);
            $("#dg_sigle_"+id).text(result.dg_sigle);
        }
    });
}


/* make an image rotate for a few seconds (used for the loading wheel) */
function rotation(element)
{

    angle=0
    //make it turn
    reload=setInterval(function ()
    {
        angle += 5;
        element.rotate(angle);
    }, 20);


    //stop
    setTimeout(function()
    {
        clearInterval(reload);
    }, 1440);

}

/* update duration fields when click on the reload image next to the AdoptionConseil field */
function update_durations(element)
{
    rotation($("#"+element));
    //~ $("#update_durations").rotate(300);

    $.ajax
    ({
        type: 'POST',
        /* url of the view */
        url: $("#url_view_durations").text(),
        dataType: 'json',
        data: "duree_adopt_trans="+$("#id_duree_adopt_trans").val()+"&duree_proc_depuis_prop_com="+$("#id_duree_proc_depuis_prop_com").val()+"&duree_proc_depuis_trans_cons="+$("#id_duree_proc_depuis_trans_cons").val()+"&duree_tot_depuis_prop_com="+$("#id_duree_tot_depuis_prop_com").val()+"&duree_tot_depuis_trans_cons="+$("#id_duree_tot_depuis_trans_cons").val()+"&transm_council="+$("#id_transm_council").val()+"&adopt_propos_origine="+$("#id_adopt_propos_origine").val()+"&adopt_conseil="+$("#id_adopt_conseil").val()+"&sign_pecs="+$("#id_sign_pecs").val(),
        success: function(result)
        {
            $("#id_duree_adopt_trans").val(result.duree_adopt_trans);
            $("#id_duree_proc_depuis_prop_com").val(result.duree_proc_depuis_prop_com);
            $("#id_duree_proc_depuis_trans_cons").val(result.duree_proc_depuis_trans_cons);
            $("#id_duree_tot_depuis_prop_com").val(result.duree_tot_depuis_prop_com);
            $("#id_duree_tot_depuis_trans_cons").val(result.duree_tot_depuis_trans_cons);
        }
    });
}



/* modal add dg / resp*/

/* bind the event to update a dg / rapp / resp with the associated drop down list */
$('#act_form').on('click', '.add_dg_js, .add_rapp_js, .add_resp_js', function()
{
    //fill the hidden div with the name of the drop down list to update (if add a record with the modal)
    field_id=this.id;
    field_id=field_id.substr(field_id.indexOf("_") + 1);
    $("#modal_field").html(field_id);

    variables = $(this).data('id').split(";");
    field=variables[0]
    name=variables[1]
    //~ url="db_mgmt/form_add.html/"+field+"/"
    url=$("#link_add_"+field).html();
    //~ alert(url);

    $.get(url, function(data)
    {
        $('#modal_add')
        .find('#modal_title').html("Add a new "+name)
        .end()
        .find('#modal_content').html($(data))
        .end()
        .find('#div_button_add').hide()
        .end()
        .find("#var_id").html(field_id)
    });
});

$(document).on('load', '#act_form', function()
{
    alert("load");
});

/* bind the event to update resps with the associated drop down list */
$('#act_form').on('change', '#resp_1_id, #resp_2_id, #resp_3_id', function()
{
    update_person(this.id, this.value, "resp");
});


/* display select button with hidden drop down lists for adopt variables */
function display_adopt_variables()
{
    $('#cs_contre, #pc_contre, #cs_abs, #pc_abs').html($('#id_countries').html());
    $('#cs_contre').gentleSelect();
    $('#pc_contre').gentleSelect();
    $('#cs_abs').gentleSelect();
    $('#pc_abs').gentleSelect();
}

$(document).ready(function() 
{
    display_adopt_variables();   
});
