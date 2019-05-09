/***
  * XMLHttpRequest object constructor (for compatibility with various browsers)
  */

  function createXmlHttpRequestObject() {
	var xmlhttp;
	try {
		xmlHttp = new XMLHttpRequest(); //should work on all browsers except IE6 or older
	} catch (e) { 
		try {
			xmlHttp = new ActiveXObject("Microsoft.XMLHttp"); //browser is IE6 or older
		} catch (e) {
			// ignore error
		}
	}
	if (!xmlHttp) {
		alert ("Error creating the XMLHttpRequest object.");
	} else {
		return xmlHttp;
	}
}

function downloadData() {
	document.getElementById("status").innerHTML = "downloadData()";
	
	//// put your code here
	try {
		var xmlHttp = createXmlHttpRequestObject();
		xmlHttp.open("GET", "?api=configure", true);
		xmlHttp.onreadystatechange = function() {
			if ((xmlHttp.readyState==4) && (xmlHttp.status==200)) { //process is completed and http status is OK
				//alert(xmlHttp.responseText);
				//alert(xmlHttp.responseXML);
				var pole = JSON.parse(xmlHttp.responseText);
				document.getElementById("dataArea").innerHTML = "";
				var pom = "<table>"
				pom +='<tr>\
								<th>price per coffee</th>\
								<th>grams per coffee</th>\
							</tr>';
					console.log(pom);
				for ( var i in pole ) {
					//console.log(pole[i]);
					//pole[i].id
					//if (Date.parse(pole[i].timestamp) > pole_time_old) {
						console.log(pole[i]);
				
						pom += '<tr>';
						/*var datum = new Date(pole[i][0]*1000)
						var den = datum.getDate();
						var mesic = datum.getMonth();
						var rok = datum.getFullYear();
						var hodiny = datum.getHours();
						var minuty = datum.getMinutes();*/
						pom += '<td>'+pole[i][1]+'</td>';
						pom += '<td>'+pole[i][2]+'</td>';
						
						pom += '</tr>';

						//document.getElementById("dataArea").innerHTML += " DeviceID: " + pole[i].deviceID + " SensorID: " + pole[i].sensorID + " " + pole[i].sensorType + ":"+ "&emsp;&emsp;" +  pole[i].value + jednotka +" </br>";
						//document.getElementById("dataArea").innerHTML += "Last data received on: " + pole[i].timestamp + " </br>";

						//document.getElementById('dataArea').scrollTop = document.getElementById('dataArea').scrollHeight;
						if ( pole_time_old != 0) {
							pole_time_old = pole[i][0];
						}
						if ( pole_time_old == 0 && i == 4) {
							pole_time_old = pole[i][0];
						}
					//}
				}
				pom +='	</table>';
				document.getElementById("dataArea").innerHTML = pom;

				var pom = ""
				pom +='<form action="" method="post">\
					';
				//for ( var i in pole ) {
					//console.log(pole[i]);
					//pole[i].id
					//if (pole[i].timestamp > pole_time_old) {
						pom += "price" +'<input type=\"text\" name=\"price\" value=\"'+pole[0][1]+'\" required>'+'<br>';
						pom += "price" +'<input type=\"text\" name=\"grams\" value=\"'+pole[0][2]+'\" required>'+'<br>';
						//document.getElementById("dataArea").innerHTML += " DeviceID: " + pole[i].deviceID + " SensorID: " + pole[i].sensorID + " " + pole[i].sensorType + ":"+ "&emsp;&emsp;" +  pole[i].value + jednotka +" </br>";
						//document.getElementById("dataArea").innerHTML += "Last data received on: " + pole[i].timestamp + " </br>";

						//document.getElementById('dataArea').scrollTop = document.getElementById('dataArea').scrollHeight;
						if ( pole_time_old != 0) {
							pole_time_old = pole[i][2];
						}
						if ( pole_time_old == 0) {
							pole_time_old = pole[i][2];
						}
					//}
				//}
				pom += '<input type="submit">';
				pom += '</form>';
				console.log(pom);
				if (loaded == false && pole_time_old !=0) {
					document.getElementById("dataArea2").innerHTML = pom;
					loaded = true;
				}

			}
		}
		xmlHttp.send(null);	
	} catch (e) {
				alert(e.toString());
		}
}

//// put your code here
var pole_time_old = 0;
var loaded = false;
setInterval("downloadData()", 3000);
downloadData();
