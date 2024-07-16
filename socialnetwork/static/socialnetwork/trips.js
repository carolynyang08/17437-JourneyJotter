"use strict"

function getTrips() {
    console.log("getTrips...")
    let other_user = document.getElementById('other_user_id')
    let other_user_id
    if (other_user){
        other_user_id = other_user.value
    }

    let on_global_page = document.getElementById('on_global_page')
    let on_global_page_bool 
    if (on_global_page){
        on_global_page_bool = on_global_page.value
    }

   
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updateTripsPage(xhr)
    }
    if (other_user && other_user_id){
        xhr.open("GET", "/socialnetwork/get-trips?other_user_id="+other_user_id, true)
    }
    else if (on_global_page && (on_global_page_bool == 'true')){
        xhr.open("GET", "/socialnetwork/get-trips?on_global_page="+on_global_page_bool, true)
    }
    else{
        xhr.open("GET", "/socialnetwork/get-trips", true)
        
    }
    xhr.send()
}

async function updateTripsPage(xhr) {
    console.log("update trips page...")
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        await updateTrips(response.trips)
        return
    }

    if (xhr.status === 0) {
        displayError("Cannot connect to server")
        return
    }


    if (!xhr.getResponseHeader('content-type') === 'application/json') {
        displayError(`Received status = ${xhr.status}`)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }

    displayError(response)
}

async function addTripToPage(xhr) {
    console.log("update trips page...")
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        await addNewTrip(response.trips)
        return
    }

    if (xhr.status === 0) {
        displayError("Cannot connect to server")
        return
    }


    if (!xhr.getResponseHeader('content-type') === 'application/json') {
        displayError(`Received status = ${xhr.status}`)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }

    displayError(response)
}

async function makeTrip() {
    console.log(cityID)
    if (!cityID) {
        displayError("Please select a city to continue.")
        return
    }

    let tripDestinationElement = document.getElementById(`id_trip_input_text`)

    let tripStartElement = document.getElementById(`id_trip_input_startdate`)
    let tripStartValue   = tripStartElement.value

    let tripEndElement = document.getElementById(`id_trip_input_enddate`)
    let tripEndValue   = tripEndElement.value

    if (tripStartValue > tripEndValue) {
        displayError("Invalid trip dates.")
        return
    }

    // Clear input box and old error message (if any)
    tripDestinationElement.value = ''
    tripStartElement.value = ''
    tripEndElement.value = ''
    displayError('')

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
        //updateTripsPage(xhr)
        addTripToPage(xhr)
    }

    let tripURL = makeTripURL()

    xhr.open("POST", tripURL, true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`destination=${destination}&destination_id=${cityID}&picture=${pic}&common_name=${commonName}&start_date=${tripStartValue}&end_date=${tripEndValue}&csrfmiddlewaretoken=${getCSRFToken()}`)
}

async function addNewTrip(trips) {
    console.log("Prepending...")
    const currDate = new Date().getTime();

    let stream = document.getElementById("trips")

    await trips.forEach (async trip => {
        const tripDate = new Date(trip.end_date).getTime();
        if ((document.getElementById(`id_trip_div_${trip.id}`) == null) && (tripDate >= currDate)) {
            let element = document.createElement('div')
            stream.prepend(element)
            await makeNewTripHTML(trip, element)
        }
    })

    let stream_past = document.getElementById("trips-past")

    await trips.forEach (async trip => {
        const tripDate = new Date(trip.end_date).getTime();
        if ((document.getElementById(`id_trip_div_${trip.id}`) == null) && (tripDate < currDate)) {
            let element = document.createElement('div')
            stream_past.prepend(element)
            await makeNewTripHTML(trip, element)
        }
    })
}

async function updateTrips(trips) {
    console.log("update trips...")
    let stream = document.getElementById("trips")

    if (document.getElementById(`id_TripBox`) == null)
        stream.append(makeTripBoxHTML())
    console.log("entering loop")

    const currDate = new Date().getTime();

    await trips.forEach (async trip => {

        const tripDate = new Date(trip.end_date).getTime();

        if ((document.getElementById(`id_trip_div_${trip.id}`) == null) && (tripDate >= currDate)) {
            console.log(`appending ${trip.destination}`)
            let element = document.createElement('div')
            stream.append(element)
            console.log(`created div for ${trip.destination}`)
            await makeTripHTML(trip, element)
            console.log(`done appending ${trip.destination}`)
        }
    })

    let stream_past = document.getElementById("trips-past")

    await trips.forEach (async trip => {
        const tripDate = new Date(trip.end_date).getTime();
        if ((document.getElementById(`id_trip_div_${trip.id}`) == null) && (tripDate < currDate)) {
            console.log(`appending ${trip.destination}`)
            let element = document.createElement('div')
            stream_past.append(element)
            console.log(`created div for ${trip.destination}`)
            await makeTripHTML(trip, element)
            console.log(`done appending ${trip.destination}`)
        }
    })

    let stream_global = document.getElementById("trips-global")

    await trips.forEach (async trip => {
        if ((document.getElementById(`id_trip_div_${trip.id}`) == null)) {
            console.log(`appending ${trip.destination}`)
            let element = document.createElement('div')
            stream_global.append(element)
            console.log(`created div for ${trip.destination}`)
            await makeTripHTML(trip, element)
            console.log(`done appending ${trip.destination}`)
        }
    })
}


function deleteTrip(id) {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
        document.getElementById(`id_trip_div_${id}`).remove()
        updateTripsPage(xhr)
    }

    xhr.open("POST", deleteTripURL(id), true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`csrfmiddlewaretoken=${getCSRFToken()}`)
}

function leaveTrip(id) {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
        document.getElementById(`id_trip_div_${id}`).remove()
        updateTripsPage(xhr)
    }

    xhr.open("POST", leaveTripURL(id), true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`csrfmiddlewaretoken=${getCSRFToken()}`)
}

// HTML Generation

async function makeTripDetailsHTML(item) {
    let other_user = document.getElementById('other_user_id')

    const { Place } = await google.maps.importLibrary("places");

    const place = new Place({
        id: item.destination_id,
        requestedLanguage: "en", // optional
    });

    let dates = makeTripDatesHTML(item)

    await place.fetchFields({
        fields: ["displayName", "formattedAddress", "location", "photos", "editorialSummary"],
        });
        
    let url = place.photos[0].getURI({
        maxWidth: 4800,
        maxHeight: 4800,
    });

    let tripURL = tripPageURL(item.id);

    let goButton = `
    <div class="buttonBox">
    <a href="${tripURL}" class="go-button" id="id_trip_destination_${item.id}" class="profile">View Trip ➜</a>
    </div>
    `;


    let leaveButton

    let tripString = userTrips

    let userTripsList = tripString.replace('[', '')

    userTripsList = userTripsList.replace(']', '')

    userTripsList.split(', ')

    console.log(userTripsList)



    if ((item.creator === myUser) || (userTripsList.includes(item.id))){
        leaveButton = `
        <div>
        <button class="trip-leave-button" onclick='leaveTrip(${item.id})'>Leave Trip</button>
        </div>`;
    } else {
        
        leaveButton = `<div>
        <button style='visibility: hidden'></button>
        </div>`;
    }

    let creator
    if ((item.creator === myUser) || (userTripsList.includes(item.id))){
        creator = `<div style='visibility: hidden'></div>`;
        
    } else {
        creator = `<div class="trip-creator">Created by ${item.creator}</div>`;
     
    }
    

    let details = `
    <div class="trip-pic">
        <img class="trip-img" src="${url}"><br>
    </div>  
    <div class="trip-details">
        <div class="trip-name"> ${place.displayName} </div>
        ${dates}
        ${goButton}
        ${leaveButton}
        ${creator}
    </div>
    `
    return details;
}

async function makeNewTripHTML(item, element) {
    
    let deleteButton
    if (item.creator === myUser) {
        deleteButton = `
        <div>
        <button class="trip-delete-button" onclick='deleteTrip(${item.id})'></button>
        </div>`
    } else {
        deleteButton = `<div>
        <button style='visibility: hidden'>X</button>
        </div>`
    }

    let details = await makeTripDetailsHTML(item);

    element.id = `id_trip_div_${item.id}`
    element.className = 'trip'
    element.innerHTML = `
    <div class="new-tag"> New </div>
    <div class=trip-delete>
            ${deleteButton} 
        <div class="trip-widget">
            ${details}
        </div>
    </div>`
}

async function makeTripHTML(item, element) {
    console.log("make trip HTML...");
    let other_user = document.getElementById('other_user_id')

    let deleteButton
    if (other_user){
        deleteButton = `<div>
        <button style='visibility: hidden'>X</button>
        </div>`
    }
    else{
        if (item.creator === myUser) {
            deleteButton = `
            <div>
            <button class="trip-delete-button" onclick='deleteTrip(${item.id})'></button>
            </div>`
        } else {
            deleteButton = `<div>
            <button style='visibility: hidden'>X</button>
            </div>`
        }
    }
    
    let details = await makeTripDetailsHTML(item);

    element.id = `id_trip_div_${item.id}`
    element.className = 'trip'
    element.innerHTML = `
    <div class=trip-delete>
            ${deleteButton} 
        <div class="trip-widget">
            ${details}
        </div>
    </div>`
}

function makeAddFriendsButtonHTML(item) {
    let details = `
    <input id="id_add_friend_input_text_${item.id}" type="text" placeholder="Enter email address" name="address"> 
    <button class="id_trip_button" onclick="addFriends()"id="id_add_friends_button_${item.id}">+ Add Friends</button>`
    return details
}

async function makeTripImageHTML(item) {
    const { Place } = await google.maps.importLibrary("places");

    const place = new Place({
        id: item.destination_id,
        requestedLanguage: "en", // optional
      });

    await place.fetchFields({
        fields: ["photos"],
        });

    let url = place.photos[0].getURI({
        maxWidth: 4800,
        maxHeight: 4800,
    });

    console.log(url)

    let details = `<img class="location_img" src="${url}">`
    return details
}

function makeTripIdHTML(item) {
    let tripURL = tripPageURL(item.id)

    let details = 
        `<span> Comment by </span>
        <a href="${profileURL}" id="id_comment_profile_${item.id}" class="profile"> ${item.first_name} ${item.last_name}</a>
        <span> - </span>`
    return details
}

async function makeTripDestinationHTML(item) {
    let tripURL = tripPageURL(item.id)
    console.log(item)

    const { Place } = await google.maps.importLibrary("places");

    const place = new Place({
        id: item.destination_id,
        requestedLanguage: "en", // optional
      });

    await place.fetchFields({
        fields: ["displayName", "formattedAddress", "location", "photos"],
        });

    console.log(place.displayName);
    console.log(place.formattedAddress);

    let destination = place.displayName;

    let details = 
        `<a href="${tripURL}" class="trip_title" id="id_trip_destination_${item.id}" class="profile"> ${destination}</a>`
    return details
    }
function makeTripDatesHTML(item) {
    let s = new Date(item.start_date)
    let e = new Date(item.end_date)
    let start = s.toLocaleDateString()
    let end = e.toLocaleDateString()
    let details = 
        `<div id="id_trip_dates_${item.id}" class="trip-dates">${start} - ${end}</div>`
    return details
}

///////////////////////////////////

// Google Places - Autofill

///////////////////////////////////



document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById("id_trip_input_text");
    async function autofill() {
      const options = {
      types: ["(cities)"]
      };

      const autocomplete = new google.maps.places.Autocomplete(input, options);

      autocomplete.addListener("place_changed", () => {

        const place = autocomplete.getPlace();

        if (!place.geometry || !place.geometry.location) {
          // User entered the name of a Place that was not suggested and
          // pressed the Enter key, or the Place Details request failed.
          window.alert("No details available for input: '" + place.name + "'");
          citySelected = false;
          return;
        }
        citySelected = true;
        cityID = place.place_id;
        commonName = place.name;
        destination = place.formatted_address;
        pic = place.photos[0];
        console.log(cityID);
        console.log(commonName);
        console.log(destination);
        console.log(pic);
      });

    }

    window.autofill = autofill;
  });

// async function autofill() {
//     //@ts-ignore
//     const [{ Map }] = await Promise.all([google.maps.importLibrary("places")]);

//     //@ts-ignore
//     const placeAutocomplete = new google.maps.places.PlaceAutocompleteElement();

//     //@ts-ignore
//     document.getElementById('autocomplete').appendChild(placeAutocomplete);
//     }

//     window.autofill = autofill;
