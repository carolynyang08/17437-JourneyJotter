"use strict"

let map;
let infowindow;
let place;

let activityMarkers = {}


async function getActivities() {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = async function() {
        if (this.readyState !== 4) return
        await updateActivitiesPage(xhr)
    }

    let getURL = getActivitiesURL(tripID)

    xhr.open("GET", getURL, true)
    xhr.send()
}

async function updateActivitiesPage(xhr) {
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        await updateActivities(response.activities)
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

function makeActivity() {

    let activityNameValue   = place.name
    let activityAddressValue   = place.formatted_address
    let activityPlaceId = place.place_id

    // Clear input box and old error message (if any)
    displayError('')

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = async function() {
        if (xhr.readyState !== 4) return
        await updateActivitiesPage(xhr)
    }

    let activityURL = makeActivityURL()

    xhr.open("POST", activityURL, true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`trip_id=${tripID}&name=${activityNameValue}&address=${activityAddressValue}&place_id=${place.place_id}&csrfmiddlewaretoken=${getCSRFToken()}`)
}



async function updateMarker(activity) {
        const { Place } = await google.maps.importLibrary("places");

        const place = new Place({
            id: activity.place_id,
            requestedLanguage: "en", // optional
        });

        await place.fetchFields({
            fields: ["displayName", "formattedAddress", "location", "photos"],
            });

        // Create Marker
        const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

        if (!map) {
            updateMarker(activity);
            return;
          }

        const marker = new AdvancedMarkerElement({
            map,
            position: place.location,
            title: place.displayName,
            content: markerContentHTML(place),
        });

        let box = document.getElementById(`id_activity_div_${activity.id}`);

        box.addEventListener("click", () => {
            toggleHighlight(marker, place);
        })

        marker.addListener("click", () => {
            toggleHighlight(marker, place);
          });
}

function toggleHighlight(markerView, place) {
    if (markerView.content.classList.contains("highlight")) {
        markerView.content.classList.remove("highlight");
        markerView.zIndex = null;
    } else {
        markerView.content.classList.add("highlight");
        markerView.zIndex = 1;
    }
}

function markerContentHTML(place) {
    const element = document.createElement("div");

    element.classList.add("activityMarker");
    element.innerHTML = `
    <div class="icon">
        
    </div>
    <div class="details">
        <div class="title">${place.displayName}</div>
        <div class="address">${place.formattedAddress}</div>
    </div>
    `;
    return element;
}

function searchContentHTML(place) {
    const element = document.createElement("div");

    element.classList.add("activityMarker");
    element.innerHTML = `
    <div class="icon">
        
    </div>
    <div class="details">
        <div class="title">${place.displayName}</div>
        <div class="address">${place.formattedAddress}</div>
        <div>
        <button onclick="makeActivity()"id="id_activity_button">Add Activity</button>
        </div>
    </div>
    `;
    return element;
}

async function updateActivities(activities) {

    let stream = document.getElementById("activities")

    // Add activities that are not generated yet
    await activities.forEach(async activity => {
        if (document.getElementById(`id_activity_div_${activity.id}`) == null) {
            let element = document.createElement('div')
            stream.append(element)
            await makeActivityHTML(activity, element)
            updateMarker(activity)
        }
    })


}

function deleteActivity(id) {
    let xhr = new XMLHttpRequest()
    
    window.location.reload()

    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
    }

    xhr.open("POST", deleteActivityURL(id), true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`csrfmiddlewaretoken=${getCSRFToken()}`)
}

// HTML Generation

async function makeActivityHTML(item, element) {
    let details = await makeActivityDetailsHTML(item)
    
    element.id = `id_activity_div_${item.id}`
    element.className = 'activity'
    element.innerHTML = `${details}`
}

async function makeActivityDetailsHTML(item) {
    const { Place } = await google.maps.importLibrary("places");

    const place = new Place({
        id: item.place_id,
        requestedLanguage: "en", // optional
    });

    await place.fetchFields({
        fields: ["displayName", "formattedAddress", "location", "photos", "editorialSummary"],
        });
        
    let url = place.photos[0].getURI({
        maxWidth: 4800,
        maxHeight: 4800,
    });

    let summary = place.editorialSummary;
    let summaryBox = '';

    if (summary != null) {
        summaryBox = `<div class="activity-summary"> ${place.editorialSummary} </div>`;
    }

    let usertrips = document.getElementById("user-trips");

    let deleteButton

    if ((item.creator === myUser) || (myUser in usertrips)){
        
        deleteButton = `
        <div>
        <button class="delete-button" onclick='deleteActivity(${item.id})'></button>
        </div>`;
     
    } else {
        deleteButton = `<div>
        <button style='visibility: hidden'></button>
        </div>`
    }

    let details = `
    ${deleteButton}
    <div class="activity-details">
        <div class="activity-name"> ${place.displayName} </div>
        <div class="activity-address"> ${place.formattedAddress} </div>
        ${summaryBox}
    </div>
    <div class="activity-pic">
        <img class="activity-img" src="${url}">
    </div>    
    `
    return details;
}

function makeActivityNameHTML(item) {
    let name = item.name

    let details = 
        `<span id="id_activity_name_${item.id}"> ${name}</span>`
    return details
}

function makeActivityAddressHTML(item) {
    let address = item.address

    let details = 
        `<span id="id_activity_address_${item.id}">${address}</span>`
    return details
}

function addFriends() {

    let emailElement = document.getElementById(`id_add_friend_input_text`)
    let emailValue   = emailElement.value

    // Clear input box and old error message (if any)
    emailElement.value = ''
    displayError('')

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = async function() {
        if (xhr.readyState !== 4) return
        await updateActivitiesPage(xhr)
    }

    let friendURL = addFriendURL(emailValue)

    xhr.open("POST", friendURL, true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`csrfmiddlewaretoken=${getCSRFToken()}`)
}

///////////////////////////////////

// Google Places - Autofill & Map

///////////////////////////////////


async function tripMap() {

    // Get place details
    const { Place } = await google.maps.importLibrary("places");
    // Create Marker
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    //@ts-ignore
    const destination = new Place({
        id: placeID,
        requestedLanguage: "en", // optional
      });

    await destination.fetchFields({
        fields: ["displayName", "formattedAddress", "location", "photos"],
        });

    // Initialize Map
    const { Map } = await google.maps.importLibrary("maps");

    map = new Map(document.getElementById("map"), {
        center: destination.location,
        zoom: 13,
        mapTypeControl: false,
        mapId: '89a476d11d14c5cd'
      });


    // Initialize Autocomplete
    const activityInput = document.getElementById("id_activity_input_text");
    const options = {
    };

    const autocomplete = new google.maps.places.Autocomplete(activityInput, options);

    // Bind the map's bounds (viewport) property to the autocomplete object,
    // so that the autocomplete requests use the current map bounds for the
    // bounds option in the request.
    autocomplete.bindTo("bounds", map);

    await autocomplete.addListener("place_changed", async () => {
        place = autocomplete.getPlace();

        if (!place.geometry || !place.geometry.location) {
            // User entered the name of a Place that was not suggested and
            // pressed the Enter key, or the Place Details request failed.
            window.alert("No details available for input: '" + place.name + "'");
            return;
        }


        // get place as Place (New) API element.
        const search = await new Place ({
            id: place.place_id,
            requestedLanguage: "en", // optional
        })

        await search.fetchFields({
            fields: ["displayName", "formattedAddress", "location", "photos"],
            });

        // If the place has a geometry, then present it on a map.
        map.setCenter(search.location);
        map.setZoom(13);

        makeActivity()




    });
}

window.tripMap = tripMap;