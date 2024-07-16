"use strict"

let map;
let marker;
let infowindow;
let place;


function getActivities() {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updateActivitiesPage(xhr)
    }

    let getURL = getActivitiesURL(tripID)

    xhr.open("GET", getURL, true)
    xhr.send()
}

function updateActivitiesPage(xhr) {
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        updateActivities(response.activities)
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

    // Clear input box and old error message (if any)
    displayError('')

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
        updateActivitiesPage(xhr)
    }

    let activityURL = makeActivityURL()

    xhr.open("POST", activityURL, true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`trip_id=${tripID}&name=${activityNameValue}&address=${activityAddressValue}&csrfmiddlewaretoken=${getCSRFToken()}`)
}

function updateActivities(activities) {

    let stream = document.getElementById("activities")

    // if (document.getElementsByClassName("gm-style-iw gm-style-iw-c") != null) {
    //     let boxes = document.getElementsByClassName("gm-style-iw gm-style-iw-c")
    //     let dialogBox = boxes[1]
    //     dialogBox.append(`<button onclick="makeActivity()"id="id_activity_button">Add Activity</button>`)
    // }
    // Add activities that are not generated yet
    activities.forEach(activity => {
        if (document.getElementById(`id_activity_div_${activity.id}`) == null) {
            stream.append(makeActivityHTML(activity))
        }
    })
}

function deleteActivity(id) {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
        document.getElementById(`id_activity_div_${id}`).remove()
        updateActivitiesPage(xhr)
    }

    xhr.open("POST", deleteActivityURL(id), true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`csrfmiddlewaretoken=${getCSRFToken()}`)
}

// HTML Generation

function makeActivityHTML(item) {
    // let id_text = maketripIdHTML(item)
    let deleteButton
    console.log(item)
    console.log(item.creator)
    if (item.creator === myUser) {
        deleteButton = `<button onclick='deleteActivity(${item.id})'>X</button>`
    } else {
        deleteButton = `<button style='visibility: hidden'>X</button>`
    }

    let name = makeActivityNameHTML(item)
    let address = makeActivityAddressHTML(item)
    // let details = maketripDetailsHTML(item)
    
    let element = document.createElement('div')
    element.id = `id_activity_div_${item.id}`
    element.className = 'activity'
    element.innerHTML = `${deleteButton} ${name} ${address}`

    return element
}

function makeActivityNameHTML(item) {
    let name = item.name

    let details = 
        `<span id="id_activity_name_${item.id}"> ${name}</a>`
    return details
}

function makeActivityAddressHTML(item) {
    let address = item.address

    let details = 
        `<span id="id_activity_address_${item.id}">${address}</span>`
    return details
}

///////////////////////////////////

// Google Places - Autofill & Map

///////////////////////////////////


document.addEventListener('DOMContentLoaded', function() {
const activityInput = document.getElementById("id_activity_input_text");

let service;
function tripMap() {

    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 40.749933, lng: -73.98633 },
        zoom: 13,
        mapTypeControl: false,
      });

    const options = {
    };

    const autocomplete = new google.maps.places.Autocomplete(activityInput, options);

    // Bind the map's bounds (viewport) property to the autocomplete object,
    // so that the autocomplete requests use the current map bounds for the
    // bounds option in the request.
    autocomplete.bindTo("bounds", map);

    infowindow = new google.maps.InfoWindow();
    const infowindowContent = document.getElementById("infowindow-content");

    infowindow.setContent(infowindowContent);

    marker = new google.maps.Marker({
        map,
        anchorPoint: new google.maps.Point(0, -29),
    });

    //////////////
    // Listen for clicks of default locations
    //////////////

    map.addListener("click", (event) => {

        infowindow.close();
        marker.setVisible(false);

        // const coords = event.latLng;

        // console.log("Clicked Coordinates:", coords.lat(), coords.lng());

        // const request = {
        //     location: coords,
        //     radius: '100',
        //   };
        
        //   service = new google.maps.places.PlacesService(map);
        //   service.findPlaceFromQuery(request, (results, status) => {
        //     if (status === google.maps.places.PlacesServiceStatus.OK && results) {
        //         console.log("Place name: ", results[0].name);
        //         createMarker(results[0]);
        //       }
        
        //       map.setCenter(results[0].geometry.location);
        //     });

        // if (!place.geometry || !place.geometry.location) {
        //     // User entered the name of a Place that was not suggested and
        //     // pressed the Enter key, or the Place Details request failed.
        //     window.alert("No details available for input: '" + place.name + "'");
        //     return;
        // }

        // // If the place has a geometry, then present it on a map.
        // if (place.geometry.viewport) {
        //     map.fitBounds(place.geometry.viewport);
        // } else {
        //     map.setCenter(place.geometry.location);
        //     map.setZoom(17);
        // }
        // marker.setPosition(place.geometry.location);
        // marker.setVisible(true);
        // infowindowContent.children["place-name"].textContent = place.name;
        // infowindowContent.children["place-address"].textContent =
        // place.formatted_address;
        infowindow.open(map, marker);
    });

    autocomplete.addListener("place_changed", () => {
        console.log("place changed");
        infowindow.close();
        marker.setVisible(false);

        place = autocomplete.getPlace();

        if (!place.geometry || !place.geometry.location) {
            // User entered the name of a Place that was not suggested and
            // pressed the Enter key, or the Place Details request failed.
            window.alert("No details available for input: '" + place.name + "'");
            return;
        }

        // If the place has a geometry, then present it on a map.
        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(17);
        }
        marker.setPosition(place.geometry.location);
        marker.setVisible(true);
        infowindowContent.children["id_place_name"].textContent = place.name;
        infowindowContent.children["id_place_address"].textContent =
        place.formatted_address;
        infowindow.open(map, marker);
    });

}

window.tripMap = tripMap;
});