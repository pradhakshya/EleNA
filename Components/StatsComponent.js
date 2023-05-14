/*  This component is used to display the elevation based stats
*/

import * as React from 'react';
import { Card, CardContent,CardMedia, Typography,CardActionArea } from '@material-ui/core';
import image from '../assets/cycleman.jpg'




export default function StatsComponent({stats}) {
  return (
    <Card style={{marginLeft:70,marginTop:120,height:350,width:400, backgroundColor: '#86d63d'}}>
      <CardActionArea>
        <CardMedia
          component="img"
          height="250"
          image={image}
          alt="green iguana"
        />
        <CardContent>
          <Typography gutterBottom variant="h5" component="div">
            Elevation: {stats.elevationGain}m
          </Typography>
          <Typography gutterBottom variant="h5" component="div">
            Distance: {stats.pathLength}m
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}