import HttpClient from "./httpClient";

class ContactsServices {
  constructor() {
    this.httpClient = new HttpClient("http://localhost:8000")
  }

  async getToken(email, password) {
    return this.httpClient.postGetToken('/api/v1/auth/login/', email, password)
  }

  async updateFormStatus(id, status) {
    return this.httpClient.put(`/api/v1/forms/parent/update-status/?id=${id}`, status)
  }

  async createForm(params) {
    return this.httpClient.post('/api/v1/forms/parent/', params)
  }

  async createFormStaff(params) {
    return this.httpClient.postFormByStaff('/api/v1/forms/staff/', params)
  }

  async listFormsByUser() {
    return this.httpClient.get(`/api/v1/forms/parent/`);
  }

  async listStatus() {
    return this.httpClient.get("/api/v1/forms/parent/choices");
  }

  async listUser() {
    return this.httpClient.get("/api/v1/auth/user")
  }

  async listAplications() {
    return this.httpClient.get('/api/v1/admin/applications/')
  }

  async listChoices() {
    return this.httpClient.get('/api/v1/forms/parent/choices/')
  }
  
  async listStaffForms() {
    return this.httpClient.get('/api/v1/forms/staff/')
  }

  async deleteForms(id) {
    return this.httpClient.delete(`/api/v1/forms/parent/?id=${id}`)
  }

}

const formsServices = new ContactsServices()

export default formsServices;
