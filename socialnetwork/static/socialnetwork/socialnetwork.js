"use strict"

function loadQueries(url) {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updateQueries(xhr)
    }

    xhr.open("GET", url, true)
    xhr.send()
}


async function initMap() {
  // The location of Uluru
  const position = { lat: -25.344, lng: 131.031 };
  // Request needed libraries.
  //@ts-ignore
  const { Map } = await google.maps.importLibrary("maps");
  const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

  // The map, centered at Uluru
  map = new Map(document.getElementById("map"), {
    zoom: 4,
    center: position,
    mapId: "DEMO_MAP_ID",
  });

  // The marker, positioned at Uluru
  const marker = new AdvancedMarkerElement({
    map: map,
    position: position,
    title: "Uluru",
  });
}

function updateQueries(xhr) {
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        insertQuery(response)
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

function displayError(message) {
    let errorElement = document.getElementById("error")
    errorElement.innerHTML = message
}

function add_underscores(name) {
  let words = name.split(" ")
  let id_tag = words.join("_")
  return id_tag
}

function addLANote(act_name) {
  console.log('here')
  let act_tag = add_underscores(act_name)
  let itemTextElement = document.getElementById(`id_input_${act_tag}`)
  let itemTextValue   = itemTextElement.value

  // Clear input box and old error message (if any)
  location.reload()
  itemTextElement.value = ''
  displayError('')

  let xhr = new XMLHttpRequest()

  xhr.open("POST", "/socialnetwork/add_la_note", true)
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhr.send(`la_note=${itemTextValue}&act_name=${act_name}&csrfmiddlewaretoken=${getCSRFToken()}`)
}

function delLA(act_name) {
  location.reload()

  let xhr = new XMLHttpRequest()

  xhr.open("POST", "/socialnetwork/del_la", true)
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhr.send(`act_name=${act_name}&csrfmiddlewaretoken=${getCSRFToken()}`)
}

function addLATrip(act_name) {
  // console.log('how about now')
  location.reload()
  // console.log('adding la trip')
  let trip_id_elem = document.getElementById("id_trip_hidden")
  let trip_id  = trip_id_elem.value
  // console.log('trip id', trip_id)

  let xhr = new XMLHttpRequest()

  xhr.open("POST", "/socialnetwork/add_la_trip", true)
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhr.send(`act_name=${act_name}&trip_id=${trip_id}&csrfmiddlewaretoken=${getCSRFToken()}`)
}

function makeLAHTML(act) {
  let la_div = document.createElement("div")
  let act_tag = add_underscores(act.name)
  la_div.id = `id_la_${act_tag}`

  let la_span = document.createElement("span")
  la_span.className = "id_la_title"
  la_span.innerHTML = `${act.name}`

  let notes_input = document.createElement("input")
  notes_input.id = `id_input_${act_tag}`
  notes_input.setAttribute('type', 'text')
  notes_input.setAttribute('name', 'notes_input')
  notes_input.setAttribute('placeholder', 'Enter note...')
  notes_input.className = "la_notes_input"
  notes_input.placeholder = "Enter text..."
  notes_input.value = act.note

  let notes_button = document.createElement('button')
  notes_button.textContent = 'Add note'
  notes_button.id = `id_button_${act_tag}`
  notes_button.setAttribute('onclick', `addLANote('${act.name}')`)
  notes_button.className = "la_notes_button"
  
  let del_button = document.createElement('button')
  del_button.setAttribute('onclick', `delLA('${act.name}')`)
  del_button.id = "dislike_button"
  var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("width", "24");
  svg.setAttribute("height", "24");

  var path = document.createElementNS("http://www.w3.org/2000/svg", "path")
  path.setAttribute("d", "M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z")
  path.setAttribute("fill", "#ff0000")

  let del_label = document.createElement("span")
  del_label.innerText = " Dislike"

  svg.append(path);
  del_button.append(svg);
  del_button.append(del_label);

  let add_trip_button = document.createElement('button')
  if (act.add_to_trip) {
    add_trip_button.textContent = 'Remove from trip'
  } else {
    add_trip_button.textContent = 'Add to trip'
  }
  add_trip_button.id = `id_trip_button_${act_tag}`
  add_trip_button.setAttribute('onclick', `addLATrip('${act.name}')`)
  add_trip_button.className = "la_notes_button"

  la_div.append(la_span)
  la_div.append(notes_input)
  la_div.append(notes_button)
  la_div.append(add_trip_button)
  la_div.append(del_button)

  return la_div
}

function insertQuery(response) {
  let list = document.getElementById("queries-col")
  let queries = response['gemini_queries']
  for (let i = 0; i < queries.length; i++) {
    let query = queries[i]
    if (!document.getElementById(`id_gem_${query.id}`)) {
      let new_query = makeQueryHTML(query)
      list.prepend(new_query) // ordering newest first
    }
  }

  let act_list = document.getElementById("gem-liked_activities")
  let activities = response['liked_activities']
  for (let i = 0; i < activities.length; i++) {
    let act = activities[i]
    let act_tag = add_underscores(act.name)
    if (!document.getElementById(`id_la_${act_tag}`)) {
      let new_la = makeLAHTML(act)
      act_list.prepend(new_la) // ordering newest first
    }
  }
}

function getBulletName(li) {
  let strong_list = li.split(/<\/strong>/)
  let activities = null
  if (strong_list.length == 3) {
    activities = strong_list[1]
  } else {
    activities = strong_list[0]
  }
  let activity_list = activities.split(/<strong>/)
  let activity = activity_list[1]
  // let activity_name = null
  try {
    let activity_name = activity.replace(":", "")
    return activity_name
  } catch (error) {
    return "Cannot parse Gemini output"
  }
}

function likeGemActivity(activity_name) {
  let xhr = new XMLHttpRequest()

  let trip_id_elem = document.getElementById("id_trip_hidden")
  let trip_id  = trip_id_elem.value
  console.log('trip id', trip_id)

  xhr.open("POST", "/socialnetwork/add_liked_gem_activity", true)
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhr.send(`liked_gem_activity=${activity_name}&trip_id=${trip_id}&csrfmiddlewaretoken=${getCSRFToken()}`)
}

function clean_li(li) {
  let clean_li = li.replace("*", "<li>")
  clean_li += "</li>"
  return clean_li
}
function getGemSpan(query) {
  let gemini_span = document.createElement("span")
  gemini_span.className = `id_gemini_text_${query.id}`
  
  // extract all </li>
  let text = query.gemini_text
  // console.log('text', text)
  let li_s = text.split(/<\/li>/) // "/<" = "<", "\/" = "/", ...

  let res_array = []
  for (let i = 0; i < li_s.length-1; i++) {
    let li = li_s[i]
    let activity_name = getBulletName(li)
    if (activity_name == "Cannot parse Gemini output") {
      // console.log('in crashing case')
      gemini_span.innerHTML = "<p style='color: red; font-weight: bold;'>Cannot parse Gemini output :( </p>"
      return gemini_span
    }
    // need to extract name of li elem, add onclick to register favorited item
    let button_elem = `</li><button id='id_fav_button_${activity_name}' class="heart-btn" onclick="likeGemActivity('${activity_name}')"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="#ff0000"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg> Like </button>`
    let new_elem = clean_li(li) + button_elem
    res_array.push(new_elem)
  }
  let res = res_array.join("")

  gemini_span.innerHTML = res
  if (res == "") {
    gemini_span.innerHTML = "<p style='color: red; font-weight: bold;'>Cannot parse Gemini output :( </p>"
  }
  return gemini_span
}
function makeQueryHTML(query) {
  let query_div = document.createElement("div")
  query_div.id = `id_gem_${query.id}`

  let query_text = document.createElement("div")
  query_text.className = "post_by_query"
  let gemini_text = document.createElement("div")
  gemini_text.className = "post_by_gemini"

  // making query text -> easy
  let query_span = document.createElement("span")
  query_span.className = `id_gemini_text_${query.id}`
  query_span.innerHTML = `${query.query_text}`

  // generating gemini text with added button for each li
  let gemini_span = getGemSpan(query)

  query_text.append(query_span)
  gemini_text.append(gemini_span)

  query_div.append(query_text)
  query_div.append(gemini_text)

  return query_div
}

function generate_profile_link(post) {
  let a = document.createElement("a")
  let cur_username = post.cur_username
  let req_username = post.req_username
  if (cur_username == req_username) {
    a.href = "/socialnetwork/profile"
  } else {
    a.href = `/socialnetwork/other/${post.user_id}`
  }
  a.className = 'post_prof_link'
  a.innerText = `${post.first_name} ${post.last_name}`
  a.id = `id_post_profile_${post.id}`
  return a
}

// function generate_profile_link_comment(comment) {
//   let a = document.createElement("a")
//   let cur_username = comment.cur_username
//   let req_username = comment.req_username
//   if (cur_username == req_username) {
//     a.href = "/socialnetwork/profile"
//   } else {
//     a.href = `/socialnetwork/other/${comment.user_id}`
//   }
//   a.className = 'post_prof_link'
//   a.innerText = `${comment.first_name} ${comment.last_name}`
//   a.id = `id_comment_profile_${comment.id}`
//   return a
// }


// function generate_date(post) {
//   let date = document.createElement("span")
//   date.className = "date_class"
//   date.id = `id_post_date_time_${post.id}`
//   const d = new Date(post.post_time)
//   let date_str = d.toLocaleDateString()
//   let time_str = d.toLocaleTimeString()
//   time_str = remove_seconds(time_str)
//   let date_time = date_str + " " + time_str
//   date.innerText = `${date_time}`
//   return date
// }

// "9:06:13 PM"
// function remove_seconds(time_str) {
//   let elems = time_str.split(" ")
//   let time = elems[0]
//   let am_pm = elems[1]
//   let time_elems = time.split(":")
//   let no_sec = time_elems.splice(0, 2)
//   no_sec = no_sec.join(":")
//   let res = no_sec + " " + am_pm
//   return res
// }

// function generate_comment_date(comment) {
//   let date = document.createElement("span")
//   date.className = "date_class"
//   date.id = `id_comment_date_time_${comment.id}`
//   const d = new Date(comment.comment_time)
//   let date_str = d.toLocaleDateString()
//   let time_str = d.toLocaleTimeString()
//   time_str = remove_seconds(time_str)
//   let date_time = date_str + " " + time_str
//   console.log('timestr', time_str)
//   date.innerText = `${date_time}`
//   return date
// }

// function generate_new_comment(post) {
//   let new_comment = document.createElement("div")
//   new_comment.id = `new_comment_${post.id}`

//   let label = document.createElement("LABEL")
//   label.htmlFor = `new_comment_${post.id}`
//   label.innerHTML = 'Comment:'
//   new_comment.append(label)

//   let input = document.createElement("INPUT");
//   input.setAttribute("type", "text");
//   input.id = `id_comment_input_text_${post.id}`
//   input.name = `new_comment_${post.id}`
//   new_comment.append(input)

//   let button = document.createElement("BUTTON");
//   button.className = 'button_class'
//   button.id = `id_comment_button_${post.id}`
//   button.setAttribute("onclick", `addComment(${post.id})`);
//   button.innerHTML = 'Submit'
//   new_comment.append(button)

//   return new_comment

// }

function addGemQuery() {
  let itemTextElement = document.getElementById("id_gem_query")
  let itemTextValue   = itemTextElement.value
  console.log('query', itemTextValue)

  let trip_id_elem = document.getElementById("id_trip_hidden")
  let trip_id  = trip_id_elem.value
  console.log('trip id', trip_id)

  // Clear input box and old error message (if any)
  itemTextElement.value = ''
  displayError('')

  let xhr = new XMLHttpRequest()
  xhr.onreadystatechange = function() {
      if (xhr.readyState !== 4) return
      updateQueries(xhr)
  }

  console.log('csrf', getCSRFToken())

  xhr.open("POST", "/socialnetwork/add_query", true)
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhr.send(`gem_query_item=${itemTextValue}&trip_id=${trip_id}&csrfmiddlewaretoken=${getCSRFToken()}`)
}

// function addComment(id) {
//   let itemTextElement = document.getElementById(`id_comment_input_text_${id}`)
//   let itemTextValue   = itemTextElement.value

//   // Clear input box and old error message (if any)
//   itemTextElement.value = ''
//   displayError('')

//   let xhr = new XMLHttpRequest()
//   xhr.onreadystatechange = function() {
//       if (xhr.readyState !== 4) return
//       updatePosts(xhr)
//   }
  
//   xhr.open("POST", "/socialnetwork/add-comment", true)
//   xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
//   xhr.send(`comment_text=${itemTextValue}&post_id=${id}&csrfmiddlewaretoken=${getCSRFToken()}`)
// }

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown"
}
