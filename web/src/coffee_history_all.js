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
		xmlHttp.open("GET", "?api=orders", true);
		xmlHttp.onreadystatechange = function() {
			if ((xmlHttp.readyState==4) && (xmlHttp.status==200)) { //process is completed and http status is OK
				//alert(xmlHttp.responseText);
				//alert(xmlHttp.responseXML);
				var pole = JSON.parse(xmlHttp.responseText);
				document.getElementById("dataArea").innerHTML = "";
				var pom = "<table>"
				pom +='<tr>\
								<th>username</th>\
								<th>cardID</th>\
								<th>count</th>\
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
						pom += '<td>'+pole[i][0]+'</td>';
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
			}
		}
		xmlHttp.send(null);	
	} catch (e) {
				alert(e.toString());
		}
}

//// put your code here
var pole_time_old = 0;
setInterval("downloadData()", 3000);
downloadData();
