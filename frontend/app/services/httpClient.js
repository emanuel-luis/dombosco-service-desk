import formsServices from "./ContactsService";

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
    const tokenJwt = localStorage.getItem('token')
  
    const response = await fetch(`${this.baseURL}${path}`, {
      method: 'GET', 
      headers: {
        "Authorization": `Bearer ${tokenJwt}`
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

  async post(path, params) {
    let body;
    
    const tokenJwt = localStorage.getItem('token')
  
    const response = await fetch(`${this.baseURL}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${tokenJwt}`
      },
      body: JSON.stringify(params)
    })

    if (response.ok) {
      body = await response.json();
      return true
    } else {
      const errorDetails = await response.json();
      console.log("Erro de resposta:", errorDetails);
      return false
    }
  }

  async postFormByStaff(path, params) {
    let body;
    
    const tokenJwt = localStorage.getItem('token')
    console.log(params, 'na req de formby staff')
    const payload = {
      "parent_form_id": params.data[0].id,
      "parent_form": params.user.pk,  
      "school_advice": params.values.collaboratorResponse, 
      "actions_taken": params.values.actionToTake,
      "final_notes": params.values.measuresToTake,
  };
  
    const response = await fetch(`${this.baseURL}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${tokenJwt}`
      },
      body: JSON.stringify(payload)
    })

    if (response.ok) {
      body = await response.json();
      return true
    } else {
      const errorDetails = await response.json();
      console.log("Erro de resposta:", errorDetails);
      return false
    }
  }

}

export default HttpClient