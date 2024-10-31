class HttpClient {
  constructor(baseUrl, token) {
    this.baseURL = baseUrl
    this.token = token
  }

  async get(path) {
    let body;

    const response = await fetch(`${this.baseURL}${path}`, {
      method: 'GET', // Especifique o método correto aqui
      headers: {
        "Authorization": "Bearer"
      }
    });

    const contentType = response.headers.get("Content-Type");

    if (contentType.includes("application/json")) {
      body = await response.json();
    }

    // Status code between 200-299
    if (response.ok) {
      return body;
    }
  }

  async post(path, email, password) {
    let body;
  
    const response = await fetch(`${this.baseURL}${path}`, {
      method: 'POST', // Especifique o método correto aqui
      headers: {
        'Content-Type': 'application/json', // Defina o cabeçalho
      },
      body: JSON.stringify({ // Converta o objeto em JSON
        email,
        password,
      }),
    });
  
    if (response.ok) {
      body = await response.json(); // Aguarde a resposta em JSON
      return body; // Retorne o corpo da resposta
    } else {
      // Trate o erro aqui, se necessário
      throw new Error('Erro na requisição');
    }
  }

}

export default HttpClient