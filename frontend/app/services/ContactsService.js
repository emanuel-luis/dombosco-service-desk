import HttpClient from "./httpClient";

class ContactsServices {
  constructor() {
    this.httpClient = new HttpClient("http://localhost:8000");
  }

  async getToken(email, password) {
    return this.httpClient.post('/api/v1/auth/login/', email, password)
  }

  async listForms(id) {
    return this.httpClient.get(`/api/v1/forms/parent/?id=${id}`);
  }

  async listStatus() {
    return this.httpClient.get("/api/v1/forms/parent/choices");
  }

  async listUsers() {
    return this.httpClient.get("/api/v1/auth/user")
  }

  async listAplications() {
    return this.httpClient.get('/api/v1/admin/applications/')
  }
}

const formsServices = new ContactsServices()

export default formsServices;
