/*  This component is the primary component which unifies and displays all the
 other components for search, stats ans so on.
*/
import React, {useState ,useRef, useEffect} from "react";
import {AppBar,Toolbar,
    CssBaseline,Typography,
    makeStyles,Paper, Button,Slider,Box,
    Dialog,DialogActions,DialogTitle,
    DialogContent,CircularProgress,Backdrop} from "@material-ui/core";
import AutoComplete from "./AutoComplete";
import ToggleButton from '@material-ui/lab/ToggleButton';
import ToggleButtonGroup from '@material-ui/lab/ToggleButtonGroup';
import logo from '../assets/bic.png';
import mapLogo from '../assets/maps-icon.png';
import Parser from 'html-react-parser';
import StatsComponent from "./StatsComponent";

/* Theming required for the components*/
const useStyles = makeStyles((theme) => ({

    appbar:{
        background: '#276221',
        color:'#ffffff'
    },
    navlinks: {
      marginLeft: theme.spacing(10),
      display: "flex",
    },
    content: {
        flexGrow: 1,
        padding: theme.spacing.unit * 3,
        height: '100vh',
        overflow: 'auto',
        padding: 0
      },
   divStyle :{
        display: 'flex',
        flexDirection: 'row',
      },
   logo: {
      marginLeft:650,
      width:120,
      cursor: "pointer",
    },
    link: {
      textDecoration: "none",
      color: "white",
      fontSize: "20px",
      marginLeft: theme.spacing(20),
      "&:hover": {
        color: "yellow",
        borderBottom: "1px solid white",
      },
    },
    root:{
        display:'flex'
    },
    form:{
        flexDirection: 'row',
        width:900,
    },
    textFieldSource: {
        position: 'relative',
        marginLeft: 20,
        marginRight: 10,
        marginTop: 50,
        marginBottom: 30
      },
      textFieldDestination: {
        position: 'relative',
        marginLeft: 20,
        marginRight: 10,
        marginTop: 50,
        marginBotom: 30
      },
      map:{
        width:300,
        height:200
      },
      submit:{
        position: 'relative',
        marginTop: 100,
      }
  }));

const MainComponent =()=>{
   /*State variables 
   */
    const [directions, setDirections] = useState(null);
    const [map, setMap] = useState(undefined);
    const [alignment, setAlignment] = useState('max');
    const [source,setSource] = useState(undefined);
    const [dest,setDest] = useState(undefined);
    const [percentage,setPercentage] = useState(110);
    const [steps,setSteps] = useState('');
    const [dialog,setDialog] = useState(false);
    const [route,setRoute] = useState([]);
    const [isLoading,setLoading] = useState(false);
    const [mapRoute, setMapRoute] = useState(undefined);
    const [sourceMarker,setsourceMarker] = useState(undefined);
    const [destMarker,setDestMarker] = useState(undefined);
    const [stats,setStats] = useState(undefined)
    const inputRef1 = useRef();
    const inputRef2 = useRef();

    const classes = useStyles();
    const center = {
        lat:42.38027778,
        lng:-72.51972222
      };

     /* Method to handle type of elevation
   */
    const handleChange = (event, newAlignment) => {
        setAlignment(newAlignment);
    };

     /* useEffect to load initial map
   */
    useEffect(()=>{
      createMap();
    },[]);

    /* useEffect to assemble and plot directions on the map 
   */
    useEffect(()=>{
      if(route.length>0){
        map.panTo(new L.LatLng(
            (route[route.length-1][0] + route[0][0]) / 2, 
            (route[route.length-1][1] + route[0][1]) / 2
          ))
          if(mapRoute)
             mapRoute.remove();
          var newRouteLine = L.polyline(route)
          newRouteLine.setStyle({color:'red'})
          newRouteLine.addTo(map)
          setMapRoute(newRouteLine);
          if(sourceMarker)
             sourceMarker.remove();
          let orgMarker = new L.Marker(route[0]);
          orgMarker.addTo(map);
          setsourceMarker(orgMarker);
          if(destMarker)
             destMarker.remove();
          let desMarker = new L.Marker(route[route.length-1]);
           desMarker.addTo(map);
           setDestMarker(desMarker);
           
        } 
    },[route]);

    /* Method to load the OSM map
   */
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
        setMap(map);
      }
      
         /* Method to pre-process the api data
   */
    const handleSubmit=()=>{
        var request = {
          'origin': source,
          'destination': dest,
          'distance': percentage+'',
          'elevation':alignment=='max'?'maximal':'minimal',
          'graph': 'bounded'
        }
        let formData = new FormData();
        formData.append('origin', source);
        formData.append('destination', dest);
        formData.append('distance', percentage+'');
        formData.append('elevation',alignment=='max'?'maximal':'minimal' );
        formData.append('graph', 'bounded');
        apiCall(formData);
    }

    /* Method to request an api call to the backend and fetch the response
   */
    const apiCall = (request)=>{
      setLoading(true);
      fetch("/get_route/", {
        method: 'POST',
        body: request
      })
      .then(res => res.json())
      .then(data => {
        let waypoints = data['route'];
        let stats = data['stats']['resultPath']
        if(waypoints.length==0){
          waypoints = data['shortRoute'];
          stats = data['stats']['shortestPath']
        }
        setRoute(waypoints);
        setLoading(false);
        setStats(stats)
    });
  }

    const sourceChange = (latLng)=>{
       setSource(latLng);
    }

    const destinationChange = (latLng)=>{
        setDest(latLng);
     }

      /* Method to handle reset and empty the field content
   */
     const handleReset = ()=>{
         setSource(undefined);
         setDest(undefined);
         inputRef1.current.value = '';
         inputRef2.current.value = '';
         setAlignment('max');
         setPercentage(110);
         setDirections(null);
         setStats(undefined);
         if(mapRoute)
             mapRoute.remove();
        if(sourceMarker)
            sourceMarker.remove();
        if(destMarker)
          destMarker.remove();

     }

    /* Rendering UI for the ELENA dashboard
   */
 
    return (
      <div>
        <AppBar class={classes.appbar} position="static">
          <CssBaseline />
          <Toolbar>
            <Typography variant="h3" className={classes.logo}>
              Elena
            </Typography>
            <img style={{ marginLeft: 15, width: 70, height: 60 }} src={logo} />
          </Toolbar>
        </AppBar>
        <Paper class={classes.root}>
          <Paper
            style={{
              flexDirection: "column",
              width: 900,
              background: "#f5fade",
            }}
          >
            <AutoComplete
              inputRef={inputRef1}
              onChange={sourceChange}
              placeHolder="Source"
            />
            <AutoComplete
              inputRef={inputRef2}
              onChange={destinationChange}
              placeHolder="Destination"
            />
            <ToggleButtonGroup
              color="primary"
              value={alignment}
              exclusive
              onChange={handleChange}
              className="toggle"
            >
              <ToggleButton value="max">Maximum</ToggleButton>
              <ToggleButton value="min">Minimum</ToggleButton>
            </ToggleButtonGroup>
            <Box width={300} className="slider">
              <Typography id="input-slider" gutterBottom>
                {percentage}% of shortest distance
              </Typography>
              <Slider
                min={100}
                max={200}
                defaultValue={110}
                aria-label="Default"
                valueLabelDisplay="auto"
                value={percentage}
                onChange={(e, val) => setPercentage(val)}
                style={{ color: "green" }}
              />
            </Box>
            <Button
              style={{
                background: "#BAFF39",
                color: "#000000",
                width: 70,
                position: "relative",
                float: "left",
                marginLeft: 160,
                marginTop: 50,
                marginBotom: 30,
              }}
              variant="contained"
              onClick={handleSubmit}
            >
              Start
            </Button>
            <Button
              style={{
                background: "#BAFF39",
                color: "#000000",
                width: 70,
                position: "relative",
                float: "left",
                marginLeft: 30,
                marginRight: 50,
                marginTop: 50,
                marginBotom: 30,
              }}
              variant="contained"
              onClick={handleReset}
            >
              Reset
            </Button>
            {isLoading && (
              <CircularProgress className="progress" color="'#4D148C'" />
            )}
            {!isLoading && stats && (
              <div>
                <StatsComponent stats={stats} />
              </div>
            )}
          </Paper>
          <div class={classes.map} style={{ height: "100vh", width: "100%" }}>
            <div id="map"></div>
            <Dialog open={dialog}>
              <DialogTitle>Directions</DialogTitle>
              <DialogContent>{Parser(steps)}</DialogContent>
              <DialogActions>
                <Button
                  onClick={() => {
                    setDialog(false);
                  }}
                  color="primary"
                  autoFocus
                >
                  Close
                </Button>
              </DialogActions>
            </Dialog>
          </div>
        </Paper>
      </div>
    );
};

export default MainComponent;

