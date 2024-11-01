class HttpClient {
  constructor(baseUrl, token) {
    this.baseURL = baseUrl
    this.token = token
  }

  async postGetToken(path, email, password) {
    let body;
  
    const response = await fetch(`${this.baseURL}${path}`, {
      method: 'POST', 
      headers: {
        'Content-Type': 'application/json', 
      },
      body: JSON.stringify({ // Converta o objeto em JSON
        email,
        password,
      }),
    });
  
    if (response.ok) {
      body = await response.json(); 
      this.token = body.access
      return body; 

    } else {
      throw new Error('Erro na requisição');
    }
  }

  async get(path) {
    let body;
    this.token = localStorage.getItem('token')
    const response = await fetch(`${this.baseURL}${path}`, {
      method: 'GET', 
      headers: {
        "Authorization": `Bearer ${this.token}`
      }
    });

    const contentType = response.headers.get("Content-Type");

    if (contentType.includes("application/json")) {
      body = await response.json();
    }

    if (response.ok) {
      return body;
    }
  }


}

export default HttpClient