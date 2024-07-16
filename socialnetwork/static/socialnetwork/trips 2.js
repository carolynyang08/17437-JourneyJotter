"use strict"

function getTrips() {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updateTripsPage(xhr)
    }

    xhr.open("GET", "/socialnetwork/get-trips", true)
    xhr.send()
}

function updateTripsPage(xhr) {
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        updateTrips(response.trips)
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

function makeTrip() {

    let tripDestinationElement = document.getElementById(`id_trip_input_text`)
    let tripDestinationValue   = tripDestinationElement.value

    let tripStartElement = document.getElementById(`id_trip_input_startdate`)
    let tripStartValue   = tripStartElement.value

    let tripEndElement = document.getElementById(`id_trip_input_enddate`)
    let tripEndValue   = tripEndElement.value

    // Clear input box and old error message (if any)
    tripDestinationElement.value = ''
    tripStartElement.value = ''
    tripEndElement.value = ''
    displayError('')

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) return
        updateTripsPage(xhr)
    }

    let tripURL = makeTripURL()

    xhr.open("POST", tripURL, true)
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhr.send(`destination=${tripDestinationValue}&start_date=${tripStartValue}&end_date=${tripEndValue}&csrfmiddlewaretoken=${getCSRFToken()}`)
}

function updateTrips(trips) {

    let stream = document.getElementById("trips")

    if (document.getElementById(`id_TripBox`) == null)
        stream.append(makeTripBoxHTML())

    trips.forEach(trip => {
        if (document.getElementById(`id_trip_div_${trip.id}`) == null) {
            stream.append(makeTripHTML(trip))
        }
    })
}

// HTML Generation

function makeTripHTML(item) {
    // let id_text = maketripIdHTML(item)
    let destination = makeTripDestinationHTML(item)
    let dates = makeTripDatesHTML(item)
    // let details = maketripDetailsHTML(item)
    
    let element = document.createElement('div')
    element.id = `id_trip_div_${item.id}`
    element.className = 'trip'
    element.innerHTML = `${destination} ${dates}`

    return element
}

function makeTripIdHTML(item) {
    let tripURL = tripPageURL(item.id)

    let details = 
        `<span> Comment by </span>
        <a href="${profileURL}" id="id_comment_profile_${item.id}" class="profile"> ${item.first_name} ${item.last_name}</a>
        <span> - </span>`
    return details
}

function makeTripDestinationHTML(item) {
    let tripURL = tripPageURL(item.id)

    let destination = sanitize(item.destination)

    let details = 
        `<a href="${tripURL}" id="id_trip_destination_${item.id}" class="profile"> ${destination}</a>`
    return details
}

function makeTripDatesHTML(item) {
    let s = new Date(item.start_date)
    let e = new Date(item.end_date)
    let start = s.toLocaleDateString()
    let end = e.toLocaleDateString()
    let details = 
        `<span id="id_trip_dates_${item.id}" class="datetime">${start} - ${end}</span>`
    return details
}

///////////////////////////////////

// Google Places - Autofill

///////////////////////////////////


document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById("id_trip_input_text");
    function autofill() {
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
          return;
        }
      });

    }

    window.autofill = autofill;
  });