import requests
from auth import get_token, save_token


BASE_URL = "http://localhost:8000"


TIMEOUT = 500



def auth_headers():

    token = get_token()

    return {

        "Authorization": f"Bearer {token}"

    }



def check_response(response):


    if response.ok:


        content_type = response.headers.get(
            "Content-Type",
            ""
        )


        if (
            "application/json" 
            in content_type
        ):

            return response.json()


        return response.content



    try:

        error = response.json()

        raise Exception(
            error.get(
                "detail",
                "Unknown error"
            )
        )


    except ValueError:

        raise Exception(
            response.text
        )



# ===========================
# Authentication
# ===========================


def register(
    email,
    password,
    full_name
):

    response = requests.post(

        f"{BASE_URL}/auth/register",

        json={

            "email": email,

            "password": password,

            "full_name": full_name

        },

        timeout=TIMEOUT

    )


    return check_response(response)


def login(email, password):

    response = requests.post(
        f"{BASE_URL}/auth/login",

        data={
            "username": email,
            "password": password
        },

        timeout=TIMEOUT
    )

    if response.status_code == 200:

        data = response.json()

        token = data.get("access_token")

        if token:
            save_token(token)

        return token, response

    return None, response


# ===========================
# Projects
# ===========================


def get_projects():


    response = requests.get(

        f"{BASE_URL}/projects",

        headers=auth_headers(),

        timeout=TIMEOUT

    )


    return check_response(response)

def create_project(name, description=""):
    payload = {"name": name}
    if description:
        payload["description"] = description

    response = requests.post(
        f"{BASE_URL}/projects",
        json=payload,
        headers=auth_headers(),
        timeout=TIMEOUT
    )

    return check_response(response)


# ===========================
# Tenders
# ===========================


def get_tenders(
    project_id
):


    response = requests.get(

        f"{BASE_URL}/tenders/project/{project_id}",

        headers=auth_headers(),

        timeout=TIMEOUT

    )


    return check_response(response)


def upload_tender(
    project_id,
    file
):

    response = requests.post(

        f"{BASE_URL}/tenders/upload/{project_id}",

        files={

            "file": (

                file.name,

                file.getvalue(),

                file.type

            )

        },

        headers=auth_headers(),

        timeout=500

    )


    return check_response(response)

# ===========================
# Chat
# ===========================
def generate_report(
    tender_id,
    report_type
):

    response = requests.post(

        f"{BASE_URL}/reports/{tender_id}",

        headers=auth_headers(),

        json={
            "report_type": report_type.lower()
        },

        timeout=300
    )

    response.raise_for_status()

    return response.json()

def chat(
    tender_id,
    question
):


    response = requests.post(

        f"{BASE_URL}/chat",

        json={

            "tender_id": tender_id,

            "question": question

        },


        headers=auth_headers(),

        timeout=TIMEOUT

    )


    return check_response(response)



# ===========================
# Compare
# ===========================


def compare_tenders(
    tender_one,
    tender_two
):


    response = requests.post(

        f"{BASE_URL}/compare",

        json={

            "tender_id_1": tender_one,

            "tender_id_2": tender_two

        },


        headers=auth_headers(),

        timeout=TIMEOUT

    )


    return check_response(response)



# ===========================
# Export
# ===========================


def export_report(
    content,
    filename
):


    response = requests.post(

        f"{BASE_URL}/export/",

        json={

            "content": content,

            "filename": filename

        },


        headers=auth_headers(),

        timeout=60

    )


    return check_response(response)