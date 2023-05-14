/*  This component is used to search the source and destination with the google maps api
*/

import { useRef, useEffect, useState } from "react";
import React from 'react';
const AutoComplete = ({inputRef,onChange,placeHolder}) => {
 const autoCompleteRef = useRef();
 const options = {
  componentRestrictions: { country: "usa" },
  fields: ["address_components", "geometry", "icon", "name"],
  types: ["establishment"]
 };
 useEffect(() => {
  autoCompleteRef.current = new window.google.maps.places.Autocomplete(
   inputRef.current,
   options
  );

 autoCompleteRef.current.addListener("place_changed", async function () {
    const place = await autoCompleteRef.current.getPlace();
    onChange('('+place.geometry.location.lat()+', '+place.geometry.location.lng()+')');
   });
  }, []);

 return (
  <div>
   <input ref={inputRef} className='field' placeholder={placeHolder}/>
  </div>
 )
};
export default AutoComplete;