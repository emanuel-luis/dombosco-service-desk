import HttpClient from "./httpClient";

class ContactsServices {
  constructor() {
    this.httpClient = new HttpClient("http://localhost:8000");
  }

  async getToken(email, password) {
    return this.httpClient.postGetToken('/api/v1/auth/login/', email, password)
  }

  async listForms(email) {
    return this.httpClient.get(`/api/v1/forms/parent/?id=${email}`);
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
