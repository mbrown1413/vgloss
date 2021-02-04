import Vue from 'vue';

export function getCookie(name) {
  // https://docs.djangoproject.com/en/3.1/ref/csrf/#ajax
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
  }
  return null;
}

export async function apiRequest(method, url, data=null) {
  let request = new Request(url);
  let options = {
    method: method,
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
  };
  if(method === "POST") {
    options.headers["X-CSRFToken"] = getCookie("csrftoken");
    if(data !== null) {
      options.body = data;
    }
  }

  let response;
  try {
    response = await fetch(request, options);
  } catch(e) {
    throw "Network error: "+e;
  }

  if(response.ok) {
    return response;
  } else {
    throw response.statusText;
  }
}

/* Helper class for making query requests.
 *
 * The constructor takes a query method, which should be an async method
 * returning data. The request() method takes the parameters to call the query
 * method with and returns a promise. It will be resolved with the return data
 * from the query, or rejected with an error message, or rejected with `null`
 * if the request was canceled.
 *
 * Features:
 *   * Only the most recent request made is resolved. Stale requests are
 *     rejected with `null`.
 *   * Observable state for loading and error messages.
 *
 * Basic usage:
 *
 *     requester = new ApiRequester(queryMethod);
 *     requester.request(params).then((data) => {
 *       // Save data
 *     });
 *
 * You can add this in your vue component's data to display loading and error
 * state:
 *
 *     // Template
 *     <div v-if="filesRequester.error" class="error">
 *       {{ filesRequester.error }}
 *     </div>
 *     <div v-if="filesRequester.loading" class="loading-spinner"></div>
 *
 *     // Component data
 *     data() {
 *       return {
 *         filesRequester: new ApiRequester(queryFileList),
 *       };
 *     }
 */
export class ApiRequester {
  constructor(queryMethod) {
    this.queryMethod = queryMethod;
    this.loading = Vue.observable(false);
    this.error = Vue.observable(null);
    this._counter = 0;
  }

  async request(queryParams) {
    //TODO: Actually cancel request instead of ignoring result.
    this._counter += 1;
    let localCounter = this._counter;

    this.loading = true;
    this.error = null;

    let data;
    try {
      data = await this.queryMethod(queryParams);
    } catch(e) {
      if(localCounter === this._counter) {
        this.loading = false;
        this.error = e;
        throw e;
      } else {
        throw null;  // Canceled
      }
    }
    if(localCounter === this._counter) {
      this.loading = false;
      this.error = null;
      return data;
    } else {
      throw null;  // Canceled
    }
  }
}
