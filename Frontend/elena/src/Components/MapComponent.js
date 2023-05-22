/*  This component is used to render the maps display
*/

import React, { Component, useEffect } from 'react';
import L from 'leaflet';
import Routing from 'leaflet-routing-machine';

export default function MapComponent(props){
    useEffect(()=>{
      createMap();
    });
const createMap=()=>{
    let map = L.map('map', {
        center: [42.373222, -72.519852],
        zoom: 15,
        weight: 10,
        layers: [
          // L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png')
          L.tileLayer("https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png")
          // L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png")
        ]
      });
      if(props.route){
        map.panTo(new L.LatLng(
            (route[route.length-1][0] + route[0][0]) / 2, 
            (route[route.length-1][1] + route[0][1]) / 2
          ))
          newRouteLine = L.polyline(route)
          newRouteLine.setStyle({color:'red'})
          newRouteLine.addTo(map)
        } 
      return map;
    }

 return (
    
 <div id='map'></div>);
 
};