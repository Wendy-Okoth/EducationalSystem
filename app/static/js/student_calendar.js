import { Calendar } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import listPlugin from '@fullcalendar/list';
import interactionPlugin from '@fullcalendar/interaction';

// Make sure this runs after DOM is ready
document.addEventListener('DOMContentLoaded', function (){
    const calendarEl = document.getElementById('calendar');

    if (calendarEl) {
        const calendar = new Calendar(calendarEl, {
            plugins: [dayGridPlugin, timeGridPlugin, listPlugin, interactionPlugin],
            headerToolbar: {
              left: 'prev,next today',
              center: 'title',
              right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
            },
            initialView: 'dayGridMonth',
            navLinks: true,
            editable: false,
            dayMaxEvents: true,
            height: 'auto',

            // This is the core logic to load assignments from your API
            events: function(fetchInfo, successCallback, failureCallback) {
                fetch('/student/api/assignments')
                    .then(response => response.json())
                    .then(data => {
                        successCallback(data);
                    })
                    .catch(error => {
                        console.error('Error fetching student assignments:', error);
                        failureCallback(error);
                    });
            }
        });
        calendar.render();
    }
});