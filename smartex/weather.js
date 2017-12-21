var request = require('request')
const keys = require('./keys.js')
const APIKEY = "43d598a94b9187f68479b1eb85ad68ee"

const citylist = {
    'Kolkata':'1275004',
    'Asansol': '1278314',
    'Durgapur': '1272175',
    'Baharampur': '1277820',
    'Habra': '1270568',
    'Kharagpur': '1266976',
    'Shantipur': '1256639',
    'Ranaghat': '1258546',
    'Haldia': '1344377',
    'Raiganj': '1259009',
    'Krishnanagar': '1265859',
    'Medinipur': '1263220',
    'Jalpaiguri': '1269388',
    'Balurghat': '1277508',
    'Bankura': '1277264',
    'Jangipur': '1269247',
    'Bangaon': '1277324'
}

//success is the function called on data json, fail is called on response json
function getCurrentWeather(params,success,fail) {
    payload= {
        appid: APIKEY
    }
    if (params.id) {
        payload.id = params.cityid;
    } else if (params.cityname) {
        payload.id = citylist[params.cityname];
    } else if (params.lat && params.lon) {
        payload.lat = params.lat;
        payload.lon = params.lon;
    }
	request({
            url: 'https://api.openweathermap.org/data/2.5/weather',
            method: 'GET',
            qs: payload
        }, function (error, response, body) {
            if (error) {
                console.log('Error: ', error);
                fail(response);
            } else {
            	success(response.body);
            }
        });
}
//success is the function called on data json, fail is called on response json
function getForecast(params,success,fail) {
    payload= {
        appid: APIKEY
    }
    if (params.id) {
        payload.id = params.cityid;
    } else if (params.cityname) {
        payload.id = citylist[params.cityname];
    } else if (params.lat && params.lon) {
        payload.lat = params.lat;
        payload.lon = params.lon;
    }
	request({
            url: 'https://api.openweathermap.org/data/2.5/forecast',
            method: 'GET',
            qs: payload
        }, function (error, response, body) {
            if (error) {
                console.log('Error: ', error);
                fail(response);
            } else {
            	success(response.body);
            }
        });
}


//Testing
/*
const example_params = {
    cityname: 'Kolkata'
 }
getCurrentWeather(example_params,console.log,console.log);
*/
