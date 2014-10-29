/* #########################################################################
# Project:     ControlIES
# Module:     	utils.js
# Purpose:     Util functions
# Language:    javascript
# Copyright:   2009-2010 - Manuel Mora Gordillo <manuito @nospam@ gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
############################################################################## */

function getActiveTab(){
	var active = $('#tabsHosts').tabs('option','selected');
	return active;
}

function selectAll(){	
	$("#selectable"+getActiveTab()+" li").addClass("ui-selected");
}

function selectNone(){
	$("#selectable"+getActiveTab()+" li").removeClass("ui-selected");
}

function computersSelected(){
	var selected = Array();
	var activeTab = getActiveTab();
	
	var j=0;
	
	$("#selectable"+activeTab+" li").each(function(i, item){
		if($("#"+item.id).hasClass('ui-selected')==true){
			selected[j] = $("#"+item.id + ":eq(0) > #pcName").html();
			j++;
		}
	});
	return selected;
}

function connection(url,data,action){

	var dataString = $.JSON.encode(data);
//	alert(dataString);
	$.ajax({ 
		url : url , 
		type: 'POST',
		data : dataString,
		dataType: 'json',
		success: function (result) { 
			switch(result.success){
				case "true":{
					break;
				}
			}
		},
      error:function (result){
			if(url!="errorLog"){
				modalAlert("Surgi&oacute; un error");
				setTimeout('$( "#dialogAlert" ).dialog( "close" )',1000);
			}
		} 
  });
}

function sendOrderSelected(url,args,action){

	var selected = computersSelected();
	if(selected.length==0){
		modalAlert("Para realizar la acci&oacute;n debe seleccionar al menos un equipo");
		return;
	}

	var hosts = {
		pclist : selected,
		args : args
	}
	connection(url,hosts,action);
}

function sendOrder(url,args,action){

	var classroom = {
		"args" : args
	}

	var dataString = $.JSON.encode(classroom);
	connection(url,dataString,action);
}



function modalAlert(message){

	$("#dialogAlertMessage").html(message);

	$("#dialogAlert")
		.dialog({
			modal: true,
			width: 350,
			resizable: false,
			hide: "explode",
			buttons: {
				Ok: function() { $( this ).dialog( "close" ); }
			}
		})
		.dialog('open'); 

	return true;
}

function modalConfirm(message, funct){

	$("#dialogAlertMessage").html(message);

	$("#dialogAlert")
		.dialog({
			modal: true,
			width: 350,
			resizable: false,
			buttons: {
				"Si": function() { eval(funct); },
				"No": function() { $( this ).dialog( "close" ); }
			}
		})
		.dialog('open'); 

	return true;
}

function printDialog(text){
    jQuery( "#dialog-alerts p" ).html(text);
    jQuery( "#dialog-alerts" ).dialog({
        resizable: false,
        height:150,
        width:290,
        modal: true,
        buttons: { "Aceptar": function() { $( this ).dialog( "close" ); }}
    }).dialog('open');
    return false;
}

function rowsSelected(max=666){ 
	var uid = jQuery("#list").jqGrid('getGridParam','selarrrow');

    if( uid.length == 0){
    	printDialog("Debe seleccionar al menos un registro.");
    }

    if( uid.length > 1 && max==1){
    	printDialog("Debe seleccionar un único registro.");
    }
    return uid;
}    

jQuery(document).ready(function(){
    $.datepicker.regional['es'] = {
        closeText: 'Cerrar',
        prevText: '<Ant',
        nextText: 'Sig>',
        currentText: 'Hoy',
        monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        monthNamesShort: ['Ene','Feb','Mar','Abr', 'May','Jun','Jul','Ago','Sep', 'Oct','Nov','Dic'],
        dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
        dayNamesShort: ['Dom','Lun','Mar','Mié','Juv','Vie','Sáb'],
        dayNamesMin: ['Do','Lu','Ma','Mi','Ju','Vi','Sá'],
        weekHeader: 'Sm',
        dateFormat: 'dd/mm/yy',
        firstDay: 1,
        isRTL: false,
        showMonthAfterYear: false,
        yearSuffix: ''
    };
    $.datepicker.setDefaults($.datepicker.regional['es']);
}); 

function zeroFill( number, width )
{
  width -= number.toString().length;
  if ( width > 0 )
  {
    return new Array( width + (/\./.test( number ) ? 2 : 1) ).join( '0' ) + number;
  }
  return number + ""; // always return a string
}