//Eventually our URL for grabbing the data will go Here
//var weatherURL = ""

//renderMap(WeatherURL);

//function renderMap(weatherURL) {}
  d3.json("sevenday_filtered.json", function(response) {
    console.log(response);

  // Loop through our data...
    for (var i = 0; i < response.length; i++) {
    // set the data location property to a variable
      var data = response[i]
      var lat = +data.latitude;
      var lon = +data.longitude;
      var temp = +data.temp;
      var day = data.timeOfDay;
      var date = data.day;
      var icon = data.icon;
      var longfore = data.longForecast;
      var shortfore = data.shortForecast;
      var weatherIcon = L.icon({
        iconUrl: icon,
        iconSize: [50, 50],
      });
      function forEachForecastLayer(data, layer) {
      var marker = L.marker([lat, lon], {icon: weatherIcon})
    };
    function forEachForecast(data, layer) {
      layer.bindPopup("<h3>Temperature  " + temp + "<h3>Date:  " + day +","+ date + "<h3>Forecast:  " + longfore + "</h3>");
    };
    //Below closes out the for loop
      var timelineLayer = L.timeline(data, {
        getInterval: function(data) {
          return {
            start: day + date,
            end: day + date
          };
        },
        pointToLayer: forEachForecastLayer,
        onEachFeature: forEachForecast
      });
// the above timeline layer code is now closed
    };
    createMap(timelineLayer);
  });
//Below closes out our d3 function that runs on the sevenday_filtered JSON data

//createMap();
//Adding function to create our map which is called above
function createMap(timelineLayer) {
    var outdoors = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/outdoors-v10/tiles/256/{z}/{x}/{y}?" +
    "access_token=pk.eyJ1IjoiYm9nb3Jkb244NiIsImEiOiJjamViam45ZWIwZ3NhMnhsYWV2MXJscXBiIn0." +
    "vkP7IgE8o4eX6nIZeVtV0Q");

    var light = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?" +
    "access_token=pk.eyJ1IjoiYm9nb3Jkb244NiIsImEiOiJjamViam45ZWIwZ3NhMnhsYWV2MXJscXBiIn0." +
    "vkP7IgE8o4eX6nIZeVtV0Q");

    var satellite = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/256/{z}/{x}/{y}?" +
    "access_token=pk.eyJ1IjoiYm9nb3Jkb244NiIsImEiOiJjamViam45ZWIwZ3NhMnhsYWV2MXJscXBiIn0." +
    "vkP7IgE8o4eX6nIZeVtV0Q");

    var baseMaps = {
      "Light": light,
      "Outdoors": outdoors,
      "Satellite": satellite
    };
    // var overlayMaps = {
    //   "Weather Data": weather
    // }
    var map = L.map("map", {
      center: [38.91, -77.0369],
      zoom: 12,
      layers: satellite
    });

    L.control.layers(baseMaps, {
      collapsed: true
    }).addTo(map);

    var timelineControl = L.timelineSliderControl({
      //formatOutput: function(date) {
      //return new Date(date).toString();}
    });
    timelineControl.addTo(map);
    timelineControl.addTimelines(timelineLayer);
    timelineLayer.addTo(map);
//Below closes out function createMap
};
//This function fixes the issue with the map not loading after Bootstrap in HTML
var mapmargin = 50;
$('#map').css("height", ($(window).height() - mapmargin));
$(window).on("resize", resize);
resize();
function resize(){

    if($(window).width()>=980){
        $('#map').css("height", ($(window).height() - mapmargin));
        $('#map').css("margin-top",50);
    }else{
        $('#map').css("height", ($(window).height() - (mapmargin+12)));
        $('#map').css("margin-top",-21);
    }
    //resizes the map after Bootstrap so it will fit the window
    //map.invalidateSize();
}





// // function createMap() {
// // // Here we create a variable to store our url to mapbox to pull in the light map
// //       var light = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?" +
// //       "access_token=pk.eyJ1IjoiYm9nb3Jkb244NiIsImEiOiJjamViam45ZWIwZ3NhMnhsYWV2MXJscXBiIn0.vkP7IgE8o4eX6nIZeVtV0Q");
// //
// //       var dark = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/dark-v9/tiles/256/{z}/{x}/{y}?" +
// //       "access_token=pk.eyJ1IjoiYm9nb3Jkb244NiIsImEiOiJjamViam45ZWIwZ3NhMnhsYWV2MXJscXBiIn0.vkP7IgE8o4eX6nIZeVtV0Q");
// // // Darkmap layer
// //       var outdoors = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/outdoors-v10/tiles/256/{z}/{x}/{y}?" +
// //       "access_token=pk.eyJ1IjoiYm9nb3Jkb244NiIsImEiOiJjamViam45ZWIwZ3NhMnhsYWV2MXJscXBiIn0." +
// //       "vkP7IgE8o4eX6nIZeVtV0Q");
// //

// //
// // // Creating map object
//       var myMap = L.map("map", {
//         center: [38.91, -77.036],
//         zoom: 11,
//         layers: outdoors
//       });
//
//       L.control.layers(baseMaps).addTo(myMap);
// }
//this resizes the map after the initial load and fixes it
resize();
