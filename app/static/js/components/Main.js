import React from 'react'
import { Switch, Route } from 'react-router-dom'
import Home from './Home'
import SelectShifts from './managerPlanner/SelectShifts'
import StudentDashboard from './StudentDash'
import ManagerDashboard from './ManagerDash'
import ManagerProfile from './ManagerProfile'
import StudentProfile from './StudentProfile'
import StudentSchedule from './StudentSchedule'
import ManagerSchedule from './ManagerSchedule'
import Login from './Login'
import Signup from './Signup'
import SelectWeek from './managerPlanner/SelectWeek'
import SelectSchedule from './managerPlanner/SelectSchedule'
import ManagerViewAvailability from './ManagerViewAvailability'
import ResetPassword from './ResetPassword';
import ErrorPage from './ErrorPage'


const Main = () => (
  <main>
    <Switch>
      <Route exact path='/' component={Home}/>
      <Route path='/login' component={Login}/>
      <Route path='/signup' component={Signup}/>
      <Route path='/studentdashboard' component={StudentDashboard}/>
      <Route path='/managerdashboard' component={ManagerDashboard}/>
      <Route path='/studentschedule' component={StudentSchedule}/>
      <Route exact path='/managerschedule/:startDate/:scheduleIndex' component={ManagerSchedule}/>
      <Route exact path='/managerschedule/:startDate' component={ManagerSchedule}/>
      <Route exact path='/managerschedule' component={ManagerSchedule}/>
      <Route exact path='/viewavailability/:username/:name' component={ManagerViewAvailability}/>
      <Route exact path='/resetPassword/:username/:password' component = {ResetPassword}/>
      <Route path='/studentprofile' component={StudentProfile}/>
      <Route path='/managerprofile' component={ManagerProfile}/>
      <Route path='/selectweek' component={SelectWeek}/>
      <Route path='/selectshifts/:startDate' component={SelectShifts} />
      <Route path='/selectschedule/:startDate' component={SelectSchedule}/>
      <Route path='/error' component={ErrorPage}/>
    </Switch>
  </main>
)

export default Main
