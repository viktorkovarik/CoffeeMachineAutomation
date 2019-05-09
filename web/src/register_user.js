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

function addZeroBefore(n) {
	return (n < 10 ? '0' : '') + n;
}


function downloadData() {
	document.getElementById("status").innerHTML = "downloadData()";
	
	//// put your code here
	try {
		var xmlHttp = createXmlHttpRequestObject();
		xmlHttp.open("GET", "?api=unregistered_users", true);
		xmlHttp.onreadystatechange = function() {
			if ((xmlHttp.readyState==4) && (xmlHttp.status==200)) { //process is completed and http status is OK
				//alert(xmlHttp.responseText);
				//alert(xmlHttp.responseXML);
				var pole = JSON.parse(xmlHttp.responseText);
				document.getElementById("dataArea").innerHTML = "";
				var pom = "<table>"
				pom +='<tr>\
								<th>id</th>\
								<th>cardID</th>\
								<th>time</th>\
								<th>username</th>\
							</tr>';
					console.log(pom);
				for ( var i in pole ) {
					//console.log(pole[i]);
					//pole[i].id
					//if (Date.parse(pole[i].timestamp) > pole_time_old) {
						console.log(pole[i]);
						var datum = new Date(pole[i][2]*1000)
						var den = datum.getDate();
						var mesic = datum.getMonth();
						var rok = datum.getFullYear();
						var hodiny = addZeroBefore(datum.getHours());
						var minuty = addZeroBefore(datum.getMinutes());
						pom += '<tr>';
						pom += '<td>'+pole[i][0]+'</td>';
						pom += '<td>'+pole[i][1]+'</td>';
						pom += '<td>'+den+'. '+mesic+'. '+ rok + ' '+ hodiny + ':' + minuty + '</td>';
						pom += '<td>'+pole[i][3]+'</td>';

						pom += '</tr>';

						//document.getElementById("dataArea").innerHTML += " DeviceID: " + pole[i].deviceID + " SensorID: " + pole[i].sensorID + " " + pole[i].sensorType + ":"+ "&emsp;&emsp;" +  pole[i].value + jednotka +" </br>";
						//document.getElementById("dataArea").innerHTML += "Last data received on: " + pole[i].timestamp + " </br>";

						//document.getElementById('dataArea').scrollTop = document.getElementById('dataArea').scrollHeight;
						if ( pole_time_old != 0) {
							pole_time_old = pole[i][2];
						}
						if ( pole_time_old == 0 && i == 4) {
							pole_time_old = pole[i][2];
						}
					//}
				}
			}
			pom +='	</table>';
			document.getElementById("dataArea").innerHTML = pom;

			//document.getElementById("dataArea2").innerHTML = "";
			var pom = ""
			pom +='<form action="" method="post">\
				';
			for ( var i in pole ) {
				//console.log(pole[i]);
				//pole[i].id
				//if (pole[i].timestamp > pole_time_old) {
					pom += '<input type=\"radio\" name=\"cardid\" value=\"'+pole[i][1]+'\" required>'+ pole[i][1] +'<br>';

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
			}
			pom += 'User name: <input type="text" name="username" required>';
			pom += '<input type="submit">';
			pom += '</form>';
			console.log(pom);
			if (loaded == false && pole_time_old !=0) {
				document.getElementById("dataArea2").innerHTML = pom;
				loaded = true;
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
