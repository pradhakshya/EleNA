/*  This component is used to search the source and destination with the google maps api
*/

import { useRef, useEffect, useState } from "react";
import React from 'react';

const AutoComp = ({inputRef,onChange,placeHolder}) => {
 const AutoCompRef = useRef();
 const options = {
  componentRestrictions: { country: "usa" },
  fields: ["address_components", "geometry", "icon", "name"],
  types: ["establishment"]
 };
 useEffect(() => {
  AutoCompRef.current = new window.google.maps.places.AutoComp(
   inputRef.current,
   options
  );

 AutoCompRef.current.addListener("place_changed", async function () {
    const place = await AutoCompRef.current.getPlace();
    onChange('('+place.geometry.location.lat()+', '+place.geometry.location.lng()+')');
   });
  }, []);

 return (
  <div>
   <input ref={inputRef} className='field' placeholder={placeHolder}/>
  </div>
 )
};
export default AutoComp;