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

    const user = await formsServices.listUser()

    console.log(user)

    const payload = {
      "requested_by": 0, // WARNING
      "student_name": params.nomeAluno,  
      "student_birth_date": params.dataNascimento, 
      "student_grade_year": params.serie,
      "student_class_name": params.turma,
      "relationship_to_student": params.parentesco,
      "issue_description": params.tratativa
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
    }
  }


}

export default HttpClient