//ManagerCal.js
import axios from 'axios';
import moment from 'moment'; 
import HTML5Backend from 'react-dnd-html5-backend'; 

import React, { Component } from 'react';
import BigCalendar from 'react-big-calendar'; 
import { DragDropContext } from 'react-dnd'
import withDragAndDrop from 'react-big-calendar/lib/addons/dragAndDrop';

import 'react-big-calendar/lib/css/react-big-calendar.css'; 

BigCalendar.setLocalizer(
  BigCalendar.momentLocalizer(moment)
);
var origin = window.location.origin;

const DragAndDropCalendar = withDragAndDrop(BigCalendar);

function convertEvent(event) {
  return {
    title: event.title,
    start: new Date(event.start),
    end: new Date(event.end),
    hexColor: event.hexColor
  }
}

class ManagerCal extends Component {
  constructor() {
    super();
    
    let timeRangeFormat = ({ start, end }, culture, local)=>
    local.format(start, 'h:mm', culture) +
      '-' + local.format(end,  'h:mm', culture)
    let dayFormat = 'ddd MM/DD'; 
    let formats = {
      dayFormat:dayFormat,
      eventTimeRangeFormat: timeRangeFormat
    }; 

    let scrollToTime = new Date().setHours(7); 

     
    this.state = {
      format: formats,
      scrollTime : scrollToTime,
      events: [{}]
    };

    this.retrieveEvents = this.retrieveEvents.bind(this);
    this.addEvent = this.addEvent.bind(this); 
    this.eventStyleGetter = this.eventStyleGetter.bind(this); 
    this.moveEvent = this.moveEvent.bind(this); 
    this.retrieveEvents(); 
  }  

  retrieveEvents() {
    console.log("Before Axios call"); 
    var url =  origin + '/api/calendar';  
    axios.get(url)
    .then(res => {
      var jsevents = res.data.events.map(
                        event => convertEvent(event)); 
      var newevents = this.state.events.concat(jsevents); 
      this.setState({ events: newevents }); 
    })
    .catch(function (error) {
      console.log(error);
    });  
  }

  addEvent(slotInfo) { 
    if (slotInfo.action == 'select') { 
      const theEvent = this.props.formCalInt(slotInfo);   
    }
  }

  addEditEvent(event) { 
      const theEvent = this.props.shiftToEdit(event);   
  }

  eventStyleGetter(event) {
    var backgroundColor = event.hexColor;
    var style = {
        backgroundColor: backgroundColor,
        borderRadius: '0px',
        opacity: 0.8,
        color: 'black',
        border: '0px',
        display: 'block'
    };
    return {
        style: style
    };
  }

  moveEvent({ event, start, end }) {
    var config = { headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'}
    }
    const theEvents = this.state.events;
    const idx = theEvents.indexOf(event); 
    event.start = start; 
    event.end = end; 
    theEvents.splice(idx, 1, event); 

    this.setState({
      events: theEvents
    })
    //alert(`${event.title} was dropped onto ${event.start}`);

    axios.post('/api/moveEvent', {
      myEvent: event
    }, config) 
    .then( (response) => {
      //alert('event posted to db'); 
    })
    .catch(function (error) {
      console.log(error);
    }); 
  }

  render() {
    const now = moment(); 
    return (
      <div height="100px">
        <h6>Drag a slot on the calendar to create a shift. Click an existing shift to delete.</h6>
        <DragAndDropCalendar
          selectable
          defaultView='week'
          popup='true'
          step = {15}
          timeslots = {4}
          style={{height: 550}}
          events={this.state.events}
          formats={this.state.format}
          scrollToTime={this.state.scrollTime}
          onSelectEvent={event => this.addEditEvent(event)}
          onSelectSlot={(slotInfo) => this.addEvent(slotInfo)}
          eventPropGetter={(this.eventStyleGetter)}
          onEventDrop={this.moveEvent}
        />
      </div>
    )
  }
}


export default ManagerCal; 