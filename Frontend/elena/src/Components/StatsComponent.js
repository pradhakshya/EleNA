/*  This component is used to display the elevation based stats
*/

import * as React from 'react';
import { Card, CardContent,CardMedia, Typography,CardActionArea } from '@material-ui/core';
import image from '../assets/cycling.webp'

export default function StatsComponent({stats}) {
  return (
    <Card style={{marginLeft:70,marginTop:120,height:250,width:400}}>
      <CardActionArea>
        <CardMedia
          component="img"
          height="150"
          image={image}
          alt="green iguana"
        />
        <CardContent>
          <Typography gutterBottom variant="h5" component="div">
            Elevation Gain: {stats.elevationGain}m
          </Typography>
          <Typography gutterBottom variant="h5" component="div">
            Route Length: {stats.pathLength}m
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}