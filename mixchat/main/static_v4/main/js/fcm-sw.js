import { getMessaging, getToken, deleteToken } from "https://www.gstatic.com/firebasejs/12.10.0/firebase-messaging.js";

const messaging = getMessaging();

getToken(messaging, {vapidKey: 'BISnUtSCVp9xdEpjULSIJVAmSSxDpZyjddQdR7NHlko2tAZNX7apnVL5feKslk1iS71cMQ8xJuH5_lx0O_Yx3UM'}).then((currentToken) => {
  if (currentToken) {
    fetch('/api/save_fcm/', {
       method: 'PUT',
       headers: {
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
       },
       body: JSON.stringify({"token": currentToken})
   })
  } else {
    console.log('No registration token available. Request permission to generate one.');
  }
}).catch((err) => {
  console.log('An error occurred while retrieving token. ', err);
});


