const senderId = localStorage.getItem('user_id');
let profileId = null


function getProfile() {
    const url = `/api/profile_form/?user_id=${senderId}`;
    fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
    })
    .then(response => response.json())
    .then(data => {
         const formPhoto = document.querySelector('.form-profile')
         let photo = document.getElementById('photoProfile');
         let photoFile = document.getElementById('photo_input');
         let name_of_user = document.getElementById('name_input');
         let date_birth = document.getElementById('date_birth_input');
         let bio = document.getElementById('bio_input');
         name_of_user.value = data.name;
         date_birth.value = data.date_birth;
         bio.value = data.bio;
         photo.src = data.photo;
         photo.style.width = '150px';
         photo.style.height = '150px';
         formPhoto.appendChild(photo)
       });
    }

function saveProfile(photo, name, date_birth, bio) {
   const formData = new FormData();
   if (photo_input.files.length > 0) {
      for (let i = 0; i < photo_input.files.length; i++) {
          console.log(photo_input.files[i])
          formData.append('photo', photo_input.files[i]);
      }
   }
   formData.append('name', name);
   formData.append('date_birth', date_birth);
   formData.append('bio', bio);
   const url = `/api/profile_form/`;
   fetch(url, {
       method: 'PUT',
       headers: {
           'Authorization': 'Bearer ' + localStorage.getItem('access_token')
       },
       body: formData
   })
   .then(response => response.text)
}

getProfile()