"use strict"

function loadFlights(departing_airport, arriving_airport) {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (this.readyState !== 4) return
        updatePosts(xhr)
    }
    url = "https://serpapi.com/search.json?engine=google_flights&departure_id=PEK&arrival_id=AUS&outbound_date=2024-03-16&return_date=2024-03-22&currency=USD&hl=en"
    xhr.open("GET", url, true)
    xhr.send()
}

function updatePosts(xhr) {
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        insertPost(response)
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

function insertPost(response) {
  let list = document.getElementById("my-posts")
  let posts = response['posts']
  let comments = response['comments']
  // processing posts first THEN comments
  for (let i = 0; i < posts.length; i++) {
    let post = posts[i]
    if (!document.getElementById(`id_post_div_${post.id}`)) {
      let new_post = makePostHTML(post)
      list.prepend(new_post)
    }
  }

  for (let j=0; j < comments.length; j++) {
    let comment = comments[j]
    let comment_list = document.getElementById(`comments_for_${comment.post_id}`)
    if (!document.getElementById(`id_comment_div_${comment.id}`)) { // id is unique
      let new_comment = makeCommentHTML(comment)
      comment_list.append(new_comment)
    }
  }
}

function makeCommentHTML(comment) {
  let comment_div = document.createElement("div")
  comment_div.id = `id_comment_div_${comment.id}`
  comment_div.className = "comment_div"

  let comment_by = generate_comment_by()
  comment_div.append(comment_by)

  let profile_link = generate_profile_link_comment(comment)
  comment_div.append(profile_link)

  let sep1 = generate_separator()
  comment_div.append(sep1)

  let text = generate_comment_text(comment)
  comment_div.append(text)

  let sep2 = generate_separator()
  comment_div.append(sep2)

  let date = generate_comment_date(comment)
  comment_div.append(date)

  return comment_div
}

function generate_comment_text(comment) {
  let text = document.createElement("span")
  text.id = `id_comment_text_${comment.id}`
  text.innerText = `${comment.text}`
  return text
}

function generate_separator() {
  let sep = document.createElement("span")
  sep.innerText = " -- "
  return sep
}

function makePostHTML(post) {
  let post_div = document.createElement("div")
  post_div.id = `id_post_div_${post.id}`
  post_div.className = "post_div"

  let post_by = generate_post_by()
  post_div.append(post_by)

  let profile_link = generate_profile_link(post)
  post_div.append(profile_link)

  let sep1 = generate_separator()
  post_div.append(sep1)

  let text = generate_text(post)
  post_div.append(text)

  let sep2 = generate_separator()
  post_div.append(sep2)

  let date = generate_date(post)
  post_div.append(date)

  let comment_div = document.createElement("div")
  comment_div.id = `comments_for_${post.id}`
  comment_div.className = "comment_div"

  let new_comment = generate_new_comment(post)
  comment_div.append(new_comment)
  post_div.append(comment_div)

  return post_div
}

function generate_post_by() {
  let post_by = document.createElement("span")
  post_by.innerText = "Post by "
  post_by.className = 'post_by'
  return post_by
}

function generate_comment_by() {
  let comment_by = document.createElement("span")
  comment_by.className = "post_by"
  comment_by.innerText = "Comment by "
  return comment_by
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

function generate_profile_link_comment(comment) {
  let a = document.createElement("a")
  let cur_username = comment.cur_username
  let req_username = comment.req_username
  if (cur_username == req_username) {
    a.href = "/socialnetwork/profile"
  } else {
    a.href = `/socialnetwork/other/${comment.user_id}`
  }
  a.className = 'post_prof_link'
  a.innerText = `${comment.first_name} ${comment.last_name}`
  a.id = `id_comment_profile_${comment.id}`
  return a
}

function generate_text(post) {
  let text = document.createElement("span")
  text.id = `id_post_text_${post.id}`
  text.innerText = `${post.text}`
  return text
}

function generate_date(post) {
  let date = document.createElement("span")
  date.className = "date_class"
  date.id = `id_post_date_time_${post.id}`
  const d = new Date(post.post_time)
  let date_str = d.toLocaleDateString()
  let time_str = d.toLocaleTimeString()
  time_str = remove_seconds(time_str)
  let date_time = date_str + " " + time_str
  date.innerText = `${date_time}`
  return date
}

// "9:06:13 PM"
function remove_seconds(time_str) {
  let elems = time_str.split(" ")
  let time = elems[0]
  let am_pm = elems[1]
  let time_elems = time.split(":")
  let no_sec = time_elems.splice(0, 2)
  no_sec = no_sec.join(":")
  let res = no_sec + " " + am_pm
  return res
}

function generate_comment_date(comment) {
  let date = document.createElement("span")
  date.className = "date_class"
  date.id = `id_comment_date_time_${comment.id}`
  const d = new Date(comment.comment_time)
  let date_str = d.toLocaleDateString()
  let time_str = d.toLocaleTimeString()
  time_str = remove_seconds(time_str)
  let date_time = date_str + " " + time_str
  console.log('timestr', time_str)
  date.innerText = `${date_time}`
  return date
}

function generate_new_comment(post) {
  let new_comment = document.createElement("div")
  new_comment.id = `new_comment_${post.id}`

  let label = document.createElement("LABEL")
  label.htmlFor = `new_comment_${post.id}`
  label.innerHTML = 'Comment:'
  new_comment.append(label)

  let input = document.createElement("INPUT");
  input.setAttribute("type", "text");
  input.id = `id_comment_input_text_${post.id}`
  input.name = `new_comment_${post.id}`
  new_comment.append(input)

  let button = document.createElement("BUTTON");
  button.className = 'button_class'
  button.id = `id_comment_button_${post.id}`
  button.setAttribute("onclick", `addComment(${post.id})`);
  button.innerHTML = 'Submit'
  new_comment.append(button)

  return new_comment

}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}

function addPost() {
  let itemTextElement = document.getElementById("id_post_input_text")
  let itemTextValue   = itemTextElement.value

  // Clear input box and old error message (if any)
  itemTextElement.value = ''
  displayError('')

  let xhr = new XMLHttpRequest()
  xhr.onreadystatechange = function() {
      if (xhr.readyState !== 4) return
      updatePosts(xhr)
  }

  xhr.open("POST", "/socialnetwork/add_post", true)
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhr.send(`post_item=${itemTextValue}&csrfmiddlewaretoken=${getCSRFToken()}`)
}

function addComment(id) {
  let itemTextElement = document.getElementById(`id_comment_input_text_${id}`)
  let itemTextValue   = itemTextElement.value

  // Clear input box and old error message (if any)
  itemTextElement.value = ''
  displayError('')

  let xhr = new XMLHttpRequest()
  xhr.onreadystatechange = function() {
      if (xhr.readyState !== 4) return
      updatePosts(xhr)
  }
  
  xhr.open("POST", "/socialnetwork/add-comment", true)
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhr.send(`comment_text=${itemTextValue}&post_id=${id}&csrfmiddlewaretoken=${getCSRFToken()}`)
}

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
