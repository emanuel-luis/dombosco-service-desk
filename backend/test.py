<<<<<<< HEAD
from urllib.parse import urljoin, urlencode
import requests

ENDPOINTS = {
    "AUTH": {
        "REGISTRATION": "http://localhost:8000/api/v1/auth/registration/",
        "LOGIN": "http://localhost:8000/api/v1/auth/login/",
    },
    "FORMS": {
        "PARENTS": "http://localhost:8000/api/v1/forms/parent/",
        "STAFF": "http://localhost:8000/api/v1/forms/staff/",
        "UPDATE-STATUS": "http://localhost:8000/api/v1/forms/parent/update-status/",
        "COMMENT": "http://localhost:8000/api/v1/forms/comment/",
    },
}
admin = {"login": {"email": "admin@admin.com", "password": "123"}}

staff = {
    "email": "tiov4d3r@gmail.com",
    "register": {
        "email": "tiov4d3r@gmail.com",
        "password1": "123@teste",
        "password2": "123@teste",
        "first_name": "Emanuel",
        "last_name": "Luis (STAFF)",
        "mobile_phone": "98985531598",
        "groups": ["Colaborador"],
    },
    "login": {
        "email": "tiov4d3r@gmail.com",
        "password": "123@teste",
    },
    "forms": {
        "school_advice": "Manda o muleque revidar e os krl dta ligado KJKJKJKJ",
        "action_taken": "Nao fiz nada",
        "final_notes": "O muleque ta fudido",
    },
}

parent = {
    "email": "emanuel.filho08@gmail.com",
    "register": {
        "email": "emanuel.filho08@gmail.com",
        "password1": "123@teste",
        "password2": "123@teste",
        "first_name": "Emanuel",
        "last_name": "Luis (PARENT)",
        "mobile_phone": "98985531598",
        "groups": ["Pais"],
    },
    "login": {
        "email": "emanuel.filho08@gmail.com",
        "password": "123@teste",
    },
    "forms": {
        "requested_by": "0",
        "student_name": "Joaquim Freire Neto",
        "student_birth_date": "2014-10-01",
        "student_grade_year": "8",
        "student_class_name": "8A",
        "relationship_to_student": "0",
        "issue_description": "O muleke ta sofrendo bullying :(",
    },
}


def post(url, data={}, headers: dict = {}, token=None):
    if token:
        headers.update({"Authorization": f"Bearer {token}"})
    response = requests.post(url, json=data, headers=headers)
    return response


def get(url, params={}, headers: dict = {}, token=None):
    if token:
        headers.update({"Authorization": f"Bearer {token}"})

    response = requests.get(url, params=params, headers=headers)
    return response


def put(url, params={}, data={}, headers: dict = {}, token=None):
    if token:
        headers.update({"Authorization": f"Bearer {token}"})
    response = requests.put(url, params=params, json=data, headers=headers)
    return response


for user in [staff, parent]:
    register_response = post(ENDPOINTS["AUTH"]["REGISTRATION"], user["register"])
    login_response = post(ENDPOINTS["AUTH"]["LOGIN"], user["login"])

    user["token"] = login_response.json()["access"]

# Create a form as a parent and then answer it as a staff
response = post(ENDPOINTS["FORMS"]["PARENTS"], parent["forms"], token=parent["token"])
response.raise_for_status()
parent_form = response.json()
parent_form_id = parent_form["id"]
assert parent_form["status"] == 0

staff["forms"]["parent_form_id"] = parent_form_id
response = post(ENDPOINTS["FORMS"]["STAFF"], staff["forms"], token=staff["token"])
response.raise_for_status()
staff_form = response.json()

response = get(ENDPOINTS["FORMS"]["PARENTS"], {"id": parent_form_id}, token=parent["token"])
parent_form = response.json()
assert parent_form["status"] == 1

# Do some comments
comment = {
    "comment": "Muleque ta sofrendo bullying, o que a escola vai fazer?",
    "parent_form_id": parent_form_id,
}

response = post(ENDPOINTS["FORMS"]["COMMENT"], comment, token=parent["token"])

comment = {
    "comment": "Vou ver com a coordenação pra dar uma coça nos moleques",
    "parent_form_id": parent_form_id,
}

response = post(ENDPOINTS["FORMS"]["COMMENT"], comment, token=staff["token"])

comment = {
    "comment": "Por favor, não faça isso. Vamos conversar com os pais dos alunos envolvidos.",
    "parent_form_id": parent_form_id,
}
response = post(ENDPOINTS["FORMS"]["COMMENT"], comment, token=parent["token"])

comment = {
    "comment": "Ok, vou falar com os pais.",
    "parent_form_id": parent_form_id,
}
response = post(ENDPOINTS["FORMS"]["COMMENT"], comment, token=staff["token"])

comment = {
    "comment": "Pais informados, aguardando retorno.",
    "parent_form_id": parent_form_id,
}
response = post(ENDPOINTS["FORMS"]["COMMENT"], comment, token=staff["token"])

response = get(ENDPOINTS["FORMS"]["COMMENT"], {"id": parent_form_id}, token=parent["token"])
comments = response.json()
print(comments)


# Update the status of the form
response = put(ENDPOINTS["FORMS"]["UPDATE-STATUS"], {"id": parent_form_id}, data={"status": 2}, token=staff["token"])
print(response.json())
=======
from urllib.parse import urljoin, urlencode
import requests

ENDPOINTS = {
    "AUTH": {
        "REGISTRATION": "http://localhost:8000/api/v1/auth/registration/",
        "LOGIN": "http://localhost:8000/api/v1/auth/login/",
    },
    "FORMS": {
        "PARENTS": "http://localhost:8000/api/v1/forms/parent/",
        "STAFF": "http://localhost:8000/api/v1/forms/staff/",
        "UPDATE-STATUS": "http://localhost:8000/api/v1/forms/parent/update-status/",
        "COMMENT": "http://localhost:8000/api/v1/forms/comment/",
    },
}
admin = {"login": {"email": "admin@admin.com", "password": "123"}}

staff = {
    "email": "tiov4d3r@gmail.com",
    "register": {
        "email": "tiov4d3r@gmail.com",
        "password1": "123@teste",
        "password2": "123@teste",
        "first_name": "Emanuel",
        "last_name": "Luis (STAFF)",
        "mobile_phone": "98985531598",
        "groups": ["Colaborador"],
    },
    "login": {
        "email": "tiov4d3r@gmail.com",
        "password": "123@teste",
    },
    "forms": {
        "school_advice": "Manda o muleque revidar e os krl dta ligado KJKJKJKJ",
        "actions_taken": "Nao fiz nada",
        "final_notes": "O muleque ta fudido",
    },
}

parent = {
    "email": "emanuel.filho08@gmail.com",
    "register": {
        "email": "emanuel.filho08@gmail.com",
        "password1": "123@teste",
        "password2": "123@teste",
        "first_name": "Emanuel",
        "last_name": "Luis (PARENT)",
        "mobile_phone": "98985531598",
        "groups": ["Pais"],
    },
    "login": {
        "email": "emanuel.filho08@gmail.com",
        "password": "123@teste",
    },
    "forms": {
        "requested_by": "0",
        "student_name": "Joaquim Freire Neto",
        "student_birth_date": "2014-10-01",
        "student_grade_year": "8",
        "student_class_name": "8A",
        "relationship_to_student": "0",
        "issue_description": "O muleke ta sofrendo bullying :(",
    },
}


def post(url, data={}, headers: dict = {}, token=None):
    if token:
        headers.update({"Authorization": f"Bearer {token}"})
    response = requests.post(url, json=data, headers=headers)
    return response


def get(url, params={}, headers: dict = {}, token=None):
    if token:
        headers.update({"Authorization": f"Bearer {token}"})

    response = requests.get(url, params=params, headers=headers)
    return response


def put(url, params={}, data={}, headers: dict = {}, token=None):
    if token:
        headers.update({"Authorization": f"Bearer {token}"})
    response = requests.put(url, params=params, json=data, headers=headers)
    return response


for user in [staff, parent]:
    register_response = post(ENDPOINTS["AUTH"]["REGISTRATION"], user["register"])
    login_response = post(ENDPOINTS["AUTH"]["LOGIN"], user["login"])

    user["token"] = login_response.json()["access"]

# Create a form as a parent and then answer it as a staff
response = post(ENDPOINTS["FORMS"]["PARENTS"], parent["forms"], token=parent["token"])
response.raise_for_status()
parent_form = response.json()
parent_form_id = parent_form["id"]
assert parent_form["status"] == 0

staff["forms"]["parent_form_id"] = parent_form_id
response = post(ENDPOINTS["FORMS"]["STAFF"], staff["forms"], token=staff["token"])
response.raise_for_status()
staff_form = response.json()

response = get(ENDPOINTS["FORMS"]["PARENTS"], {"id": parent_form_id}, token=parent["token"])
parent_form = response.json()
assert parent_form["status"] == 1

# Do some comments
comment = {
    "comment": "Muleque ta sofrendo bullying, o que a escola vai fazer?",
    "parent_form_id": parent_form_id,
}

response = post(ENDPOINTS["FORMS"]["COMMENT"], comment, token=parent["token"])

comment = {
    "comment": "Vou ver com a coordenação pra dar uma coça nos moleques",
    "parent_form_id": parent_form_id,
}

response = post(ENDPOINTS["FORMS"]["COMMENT"], comment, token=staff["token"])

comment = {
    "comment": "Por favor, não faça isso. Vamos conversar com os pais dos alunos envolvidos.",
    "parent_form_id": parent_form_id,
}
response = post(ENDPOINTS["FORMS"]["COMMENT"], comment, token=parent["token"])

comment = {
    "comment": "Ok, vou falar com os pais.",
    "parent_form_id": parent_form_id,
}
response = post(ENDPOINTS["FORMS"]["COMMENT"], comment, token=staff["token"])

comment = {
    "comment": "Pais informados, aguardando retorno.",
    "parent_form_id": parent_form_id,
}
response = post(ENDPOINTS["FORMS"]["COMMENT"], comment, token=staff["token"])

response = get(ENDPOINTS["FORMS"]["COMMENT"], {"id": parent_form_id}, token=parent["token"])
comments = response.json()
print(comments)


# Update the status of the form
response = put(ENDPOINTS["FORMS"]["UPDATE-STATUS"], {"id": parent_form_id}, data={"status": 2}, token=staff["token"])
print(response.json())
>>>>>>> 0244151 (change: ...)
