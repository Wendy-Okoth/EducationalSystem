import { Calendar } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';

// Make sure this runs after DOM is ready
document.addEventListener('DOMContentLoaded', function (){
const calendarEl = document.getElementById('calendar');

if (calendarEl) {   // ✅ only run if element exists
  const calendar = new Calendar(calendarEl, {
    plugins: [dayGridPlugin],
    initialView: 'dayGridMonth',
    height: 'auto',   // ✅ makes the calendar expand properly
    events: [
    ],
  });
  calendar.render();
}
});