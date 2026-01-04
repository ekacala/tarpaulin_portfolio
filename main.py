from flask import Flask, request, jsonify, send_file
from google.cloud import datastore, storage

import secrets
from secrets import *

import requests
import json
import io

from six.moves.urllib.request import urlopen
from jose import jwt
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'

client = datastore.Client()

URL = 'https://ekacala-tarpaulin-portfolio.uc.r.appspot.com'
PHOTO_BUCKET = 'ekacala_avatars_tarpaulin'
USERS = 'users'
COURSES = 'courses'
STUDENTS = 'students'
AVATAR = 'avatar'
ERROR_INVALID = {'Error': 'The request body is invalid'}
ERROR_UNAUTHORIZED = {'Error': 'Unauthorized'}
ERROR_PERMISSIONS = {'Error': "You don't have permission on this resource"}
ERROR_NOT_FOUND = {'Error': 'Not found'}
ERROR_INVALID_ENROLLMENT = {'Error': 'Enrollment data is invalid'}

# Update the values of the following 3 variables
CLIENT_ID = secrets.CLIENT_ID
CLIENT_SECRET = secrets.CLIENT_SECRET
DOMAIN = secrets.DOMAIN

ALGORITHMS = ["RS256"]

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    api_base_url="https://" + DOMAIN,
    access_token_url="https://" + DOMAIN + "/oauth/token",
    authorize_url="https://" + DOMAIN + "/authorize",
    client_kwargs={
        'scope': 'openid profile email',
    },
)

# This code is adapted from https://auth0.com/docs/quickstart/backend/python/01-authorization?_ga=2.46956069.349333901.1589042886-466012638.1589042885#create-the-jwt-validation-decorator

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

# Verify the JWT in the request's Authorization header
def verify_jwt(request):
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization'].split()
        token = auth_header[1]
    else:
        raise AuthError({"code": "no auth header",
                            "description":
                                "Authorization header is missing"}, 401)
    
    jsonurl = urlopen("https://"+ DOMAIN+"/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Invalid header. "
                            "Use an RS256 signed JWT Access Token"}, 401)
    if unverified_header["alg"] == "HS256":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Invalid header. "
                            "Use an RS256 signed JWT Access Token"}, 401)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=CLIENT_ID,
                issuer="https://"+ DOMAIN+"/"
            )
        except jwt.ExpiredSignatureError:
            raise AuthError({"code": "token_expired",
                            "description": "token is expired"}, 401)
        except jwt.JWTClaimsError:
            raise AuthError({"code": "invalid_claims",
                            "description":
                                "incorrect claims,"
                                " please check the audience and issuer"}, 401)
        except Exception:
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Unable to parse authentication"
                                " token."}, 401)

        return payload
    else:
        raise AuthError({"code": "no_rsa_key",
                            "description":
                                "No RSA key in JWKS"}, 401)


@app.route('/')
def index():
    return "Please navigate to /users to use this API"\


# Get a list of all users in the database
@app.route('/' + USERS, methods=['GET'])
def get_users():
    if request.method == "GET":
        # Verify user has a valid password
        try:
            payload = verify_jwt(request)
            token = payload['sub']
        except AuthError as e:
            return ERROR_UNAUTHORIZED, 401

        # Verify user is an admin
        query = client.query(kind=USERS)
        query.add_filter('sub', '=', token)
        user = list(query.fetch())
        print(user)
        user_role = user[0]['role']
        if user_role != 'admin':
            return ERROR_PERMISSIONS, 403
        else:
            query = client.query(kind=USERS)
            results = list(query.fetch())
            for r in results:
                r['id'] = r.key.id
                r.pop('avatar')
                if 'courses' in r:
                    r.pop('courses')
            return results, 200
    else:
        return jsonify(error='Method not recognized')


# Get a user in the database
@app.route('/' + USERS + '/<int:id>', methods=['GET'])
def get_user(id):
    if request.method == 'GET':
        # Verify user has a valid password
        try:
            payload = verify_jwt(request)
            token = payload['sub']
        except AuthError as e:
            return ERROR_UNAUTHORIZED, 401

        # Get auth user info
        query = client.query(kind=USERS)
        query.add_filter('sub', '=', token)
        results = list(query.fetch())
        query_user = results[0]

        # Get requested user info
        user_key = client.key(USERS, id)
        user = client.get(key=user_key)
        user['id'] = user.key.id

        # Check if user has an avatar
        if user['avatar'] == '':
            user.pop('avatar')
        else:
            user['avatar_url'] = URL + '/' + USERS + '/' + str(user['id']) + '/' + AVATAR
            user.pop('avatar')

        # Verify user requesting is an admin or has matching sub
        if query_user['role'] == 'admin' or query_user['sub'] == user['sub']:
            return user, 200
        else:
            return ERROR_PERMISSIONS, 403
    else:
        return jsonify(error='Method not recognized')


# Create/update a user's avatar
@app.route('/' + USERS + '/' + '/<int:id>' + '/' + AVATAR, methods=['POST'])
def store_image(id):
    # Any files in the request will be available in request.files object
    # Check if there is an entry in request.files with the key 'file'
    if 'file' not in request.files:
        return ERROR_INVALID, 400

    # Verify user has a valid password
    try:
        payload = verify_jwt(request)
        token = payload['sub']
    except AuthError as e:
        return ERROR_UNAUTHORIZED, 401

    # Get query user's sub
    query = client.query(kind=USERS)
    query.add_filter('sub', '=', token)
    results = list(query.fetch())
    query_user_sub = results[0]['sub']

    # Get path parameter user's sub
    user_key = client.key(USERS, id)
    user = client.get(key=user_key)
    user_sub = user['sub']

    if query_user_sub != user_sub:
        return ERROR_PERMISSIONS, 403

    # Set file_obj to the file sent in the request
    file_obj = request.files['file']
    # Create a storage client
    storage_client = storage.Client()
    # Get a handle on the bucket
    bucket = storage_client.get_bucket(PHOTO_BUCKET)
    # Create a blob object for the bucket with the name of the file
    blob = bucket.blob(file_obj.filename)
    # Position the file_obj to its beginning
    file_obj.seek(0)
    # Upload the file into Cloud Storage
    blob.upload_from_file(file_obj)

    # Add file name to users avatar property
    user.update({
        'avatar': file_obj.filename
    })
    client.put(user)

    return {'avatar_url': URL + '/' + USERS + '/' + str(id) + '/' + AVATAR}, 200


# Get a user's avatar
@app.route('/' + USERS + '/' + '/<int:id>' + '/' + AVATAR, methods=['GET'])
def get_image(id):
    # Verify user has a valid password
    try:
        payload = verify_jwt(request)
        token = payload['sub']
    except AuthError as e:
        return ERROR_UNAUTHORIZED, 401

    # Get query user's sub
    query = client.query(kind=USERS)
    query.add_filter('sub', '=', token)
    results = list(query.fetch())
    query_user_sub = results[0]['sub']

    # Get path parameter user's sub
    user_key = client.key(USERS, id)
    user = client.get(key=user_key)
    user_sub = user['sub']

    # Verify users match
    if query_user_sub != user_sub:
        return ERROR_PERMISSIONS, 403

    # Get file name associated with id
    file_name = user.get('avatar')
    # Verify user has an avatar
    if file_name == '':
        return ERROR_NOT_FOUND, 404

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(PHOTO_BUCKET)

    # Create a blob with the given file name
    blob = bucket.blob(file_name)
    # Create a file object in memory using Python io package
    file_obj = io.BytesIO()
    # Download the file from Cloud Storage to the file_obj variable
    blob.download_to_file(file_obj)
    # Position the file_obj to its beginning
    file_obj.seek(0)
    # Send the object as a file in the response with the correct MIME type and file name
    return send_file(file_obj, mimetype='image/x-png', download_name=file_name)


# Delete a user's avatar
@app.route('/' + USERS + '/' + '/<int:id>' + '/' + AVATAR, methods=['DELETE'])
def delete_image(id):
    # Verify user has a valid password
    try:
        payload = verify_jwt(request)
        token = payload['sub']
    except AuthError as e:
        return ERROR_UNAUTHORIZED, 401

    # Get query user's sub
    query = client.query(kind=USERS)
    query.add_filter('sub', '=', token)
    results = list(query.fetch())
    query_user_sub = results[0]['sub']

    # Get path parameter user's sub
    user_key = client.key(USERS, id)
    user = client.get(key=user_key)
    user_sub = user['sub']

    # Verify users match
    if query_user_sub != user_sub:
        return ERROR_PERMISSIONS, 403

    # Get file name associated with id
    file_name = user.get('avatar')
    # Verify user has an avatar
    if file_name == '':
        return ERROR_NOT_FOUND, 404

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(PHOTO_BUCKET)

    blob = bucket.blob(file_name)
    # Delete the file from Cloud Storage
    blob.delete()

    # Remove avatar name from user parameters
    user.update({
        'avatar': ''
    })
    client.put(user)

    return '', 204


# Create a course if the Authorization header contains a valid JWT
@app.route('/' + COURSES, methods=['POST'])
def courses_post():
    if request.method == 'POST':
        # Verify user has a valid password
        try:
            payload = verify_jwt(request)
            token = payload['sub']
        except AuthError as e:
            return ERROR_UNAUTHORIZED, 401

        # Verify user is an admin
        query = client.query(kind=USERS)
        query.add_filter('sub', '=', token)
        results = list(query.fetch())
        user_role = results[0]['role']
        if user_role != 'admin':
            return ERROR_PERMISSIONS, 403
        else:
            content = request.get_json()
            # Verify all attributes are in the request body
            if (content.get('subject') is None or content.get('number') is None or content.get('title') is None or
                    content.get('term') is None or content.get('instructor_id') is None):
                return ERROR_INVALID, 400
            else:
                # Verify instructor_id belongs to an instructor
                user_key = client.key(USERS, content.get('instructor_id'))
                instructor = client.get(key=user_key)
                if instructor['role'] != 'instructor':
                    return ERROR_INVALID, 400
                else:
                    # Create new course
                    new_course = datastore.entity.Entity(key=client.key(COURSES))
                    new_course.update({
                        "subject": content["subject"],
                        "number": content["number"],
                        "title": content["title"],
                        "term": content["term"],
                        "instructor_id": content["instructor_id"],
                        "students": []
                    })
                    client.put(new_course)
                    new_course['id'] = new_course.key.id
                    new_course['self'] = URL + '/' + COURSES + '/' + str(new_course['id'])
                    new_course.pop('students')

                    # Add course to instructors list of courses
                    courses = instructor.get('courses')
                    courses.append(URL + '/' + COURSES + '/' + str(new_course['id']))
                    instructor.update({
                        'courses': courses
                    })
                    client.put(instructor)
                    return new_course, 201
    else:
        return jsonify(error='Method not recognized')


# Get a list of all courses in the database
@app.route('/' + COURSES, methods=['GET'])
def get_courses():
    if request.args.get('limit') is not None:
        offset = int(request.args.get('offset'))
        limit = int(request.args.get('limit'))
    else:
        offset = 0
        limit = 3
    query = client.query(kind=COURSES)
    query.order = ['subject']
    results = list(query.fetch(offset=offset,limit=limit))
    courses = []
    for r in results:
        r['id'] = r.key.id
        r['self'] = URL + '/' + COURSES + '/' + str(r['id'])
        r.pop('students')
        courses.append(r)

    if len(courses) < 3:
        return {'courses': courses}
    else:
        next = URL + '/' + COURSES + '?offset=' + str(offset + 3) + '&limit=3'
        return {'courses': courses, 'next': next}


# Get a course from the database
@app.route('/' + COURSES + '/<int:id>', methods=['GET'])
def get_course(id):
    course_key = client.key(COURSES, id)
    course = client.get(key=course_key)
    if course is None:
        return ERROR_NOT_FOUND, 404
    else:
        course['id'] = course.key.id
        course['self'] = URL + '/' + COURSES + '/' + str(course['id'])
        course.pop('students')
        return course, 200


# Update a course in the database
@app.route('/' + COURSES + '/<int:id>', methods=['PATCH'])
def patch_course(id):
    # Verify user has a valid password
    try:
        payload = verify_jwt(request)
        token = payload['sub']
    except AuthError as e:
        return ERROR_UNAUTHORIZED, 401
    content = request.get_json()
    course_key = client.key(COURSES, id)
    course = client.get(key=course_key)
    if course is None:
        return ERROR_PERMISSIONS, 403
    else:
        # Verify user is an admin
        query = client.query(kind=USERS)
        query.add_filter('sub', '=', token)
        results = list(query.fetch())
        user_role = results[0]['role']
        if user_role != 'admin':
            return ERROR_PERMISSIONS, 403
        else:
            # Check for updated instructor_id and validate
            if content.get('instructor_id') is not None:
                instructor_key = client.key(USERS, content['instructor_id'])
                new_instructor = client.get(key=instructor_key)
                if new_instructor is None or new_instructor['role'] != 'instructor':
                    return ERROR_INVALID, 400

                # Add course to new instructor's courses list
                courses = new_instructor.get('courses')
                courses.append(URL + '/' + COURSES + '/' + str(id))
                new_instructor.update({
                    'courses': courses
                })
                client.put(new_instructor)

                # Remove course from previous instructor's courses list
                instructor_key = client.key(USERS, course.get('instructor_id'))
                old_instructor = client.get(key=instructor_key)
                courses = old_instructor.get('courses')
                courses.remove(URL + '/' + COURSES + '/' + str(id))
                old_instructor.update({
                    'courses': courses
                })
                client.put(old_instructor)

            for x in content:
                course.update({
                    x: content[x]
                })
            client.put(course)
            course['id'] = course.key.id
            course['self'] = URL + '/' + COURSES + '/' + str(course['id'])
            course.pop('students')
            return course, 200


# Delete a course from the database
@app.route('/' + COURSES + '/<int:id>', methods=['DELETE'])
def delete_course(id):
    # Verify user has a valid password
    try:
        payload = verify_jwt(request)
        token = payload['sub']
    except AuthError as e:
        return ERROR_UNAUTHORIZED, 401

    course_key = client.key(COURSES, id)
    course = client.get(key=course_key)
    if course is None:
        return ERROR_PERMISSIONS, 403
    else:
        # Verify user is an admin
        query = client.query(kind=USERS)
        query.add_filter('sub', '=', token)
        results = list(query.fetch())
        user_role = results[0]['role']
        if user_role != 'admin':
            return ERROR_PERMISSIONS, 403
        else:
            # Delete course from instructors courses list
            instructor_key = client.key(USERS, course.get('instructor_id'))
            instructor = client.get(key=instructor_key)
            courses = instructor.get('courses')
            courses.remove(URL + '/' + COURSES + '/' + str(id))
            instructor.update({
                'courses': courses
            })
            client.put(instructor)

            # Delete course from students courses list
            students = course.get('students')
            for student in students:
                student_key = client.key(USERS, student)
                student = client.get(key=student_key)
                courses = student.get('courses')
                courses.remove(URL + '/' + COURSES + '/' + str(id))
                student.update({
                    'courses': courses
                })
                client.put(student)
            # Delete course
            client.delete(course_key)
            return '', 204


# Update enrollment for students in a course
@app.route('/' + COURSES + '/' + '/<int:id>' + '/' + STUDENTS, methods=['PATCH'])
def update_enrollment(id):
    # Verify user has a valid password
    try:
        payload = verify_jwt(request)
        token = payload['sub']
    except AuthError as e:
        return ERROR_UNAUTHORIZED, 401
    content = request.get_json()
    course_key = client.key(COURSES, id)
    course = client.get(key=course_key)
    if course is None:
        return ERROR_PERMISSIONS, 403
    else:
        # Verify user is an admin
        query = client.query(kind=USERS)
        query.add_filter('sub', '=', token)
        results = list(query.fetch())
        user_role = results[0]['role']
        if user_role == 'admin' or user_role == 'instructor':
            # If user is an instructor, verify it is the correct instructor
            if user_role == 'instructor':
                # Get sub for instructor assigned to course
                course_instructor = course.get('instructor_id')
                instructor_key = client.key(USERS, course_instructor)
                instructor = client.get(key=instructor_key)
                instructor_sub = instructor.get('sub')

                # Get sub for user making request
                user_sub = results[0]['sub']

                # Compare instructors
                if instructor_sub != user_sub:
                    return ERROR_PERMISSIONS, 403

            # Validate both arrays are included in the body
            if content.get('add') is None or content.get('remove') is None:
                return ERROR_INVALID_ENROLLMENT, 409

            # Validate student_id is not in both arrays
            for student in content.get('add'):
                if student in content.get('remove'):
                    return ERROR_INVALID_ENROLLMENT, 409

            # Validate student_id in add array belongs to a student
            for student in content.get('add'):
                # Get role using student_id
                student_key = client.key(USERS, student)
                student_info = client.get(key=student_key)
                if student_info is None:
                    return ERROR_INVALID_ENROLLMENT, 409

                # Check if role = student
                student_role = student_info.get('role')
                if student_role != 'student':
                    return ERROR_INVALID_ENROLLMENT, 409

            # Validate student_id in remove array belongs to a student
            for student in content.get('remove'):
                # Get role using student_id
                student_key = client.key(USERS, student)
                student_info = client.get(key=student_key)
                if student_info is None:
                    return ERROR_INVALID_ENROLLMENT, 409

                # Check if role = student
                student_role = student_info.get('role')
                if student_role != 'student':
                    return ERROR_INVALID_ENROLLMENT, 409

            # Loop through add array and add users to course students array
            students = course.get('students')
            for student in content.get('add'):
                if student in students:
                    continue
                students.append(student)
                # Add course to student's list of courses
                student_key = client.key(USERS, student)
                add_student = client.get(key=student_key)
                courses = add_student.get('courses')
                courses.append(URL + '/' + COURSES + '/' + str(id))
                add_student.update({
                    'courses': courses
                })
                client.put(add_student)
            # Loop through remove array and remove users from course students array
            for student in content.get('remove'):
                if student not in students:
                    continue
                students.remove(student)
                # Remove course from student's list of courses
                student_key = client.key(USERS, student)
                remove_student = client.get(key=student_key)
                courses = remove_student.get('courses')
                courses.remove(URL + '/' + COURSES + '/' + str(id))
                remove_student.update({
                    'courses': courses
                })
                client.put(remove_student)
            course.update({
                'students': students
            })
            client.put(course)
            return '', 200
        else:
            return ERROR_PERMISSIONS, 403


# Get enrollment for a course
@app.route('/' + COURSES + '/' + '/<int:id>' + '/' + STUDENTS, methods=['GET'])
def get_enrollment(id):
    # Verify user has a valid password
    try:
        payload = verify_jwt(request)
        user_sub = payload['sub']
    except AuthError as e:
        return ERROR_UNAUTHORIZED, 401

    course_key = client.key(COURSES, id)
    course = client.get(key=course_key)
    if course is None:
        return ERROR_PERMISSIONS, 403
    # Validate user is an admin or instructor
    query = client.query(kind=USERS)
    query.add_filter('sub', '=', user_sub)
    results = list(query.fetch())
    user_role = results[0]['role']
    if user_role == 'admin' or user_role == 'instructor':
        # If user is an instructor, validate instructor is instructor of the course
        if user_role == 'instructor':
            # Get sub for instructor assigned to course
            course_instructor = course.get('instructor_id')
            instructor_key = client.key(USERS, course_instructor)
            instructor = client.get(key=instructor_key)
            instructor_sub = instructor.get('sub')

            # Compare instructors
            if instructor_sub != user_sub:
                return ERROR_PERMISSIONS, 403
        return course['students'], 200
    else:
        return ERROR_PERMISSIONS, 403


# Decode the JWT supplied in the Authorization header
@app.route('/decode', methods=['GET'])
def decode_jwt():
    payload = verify_jwt(request)
    return payload          
        

# Generate a JWT from the Auth0 domain and return it
# Request: JSON body with 2 properties with "username" and "password"
#       of a user registered with this Auth0 domain
# Response: JSON with the JWT as the value of the property id_token
@app.route('/users' + '/login', methods=['POST'])
def login_user():
    content = request.get_json()
    if content.get('username') is None or content.get('password') is None:
        return ERROR_INVALID, 400
    username = content["username"]
    password = content["password"]
    body = {'grant_type':'password','username':username,
            'password':password,
            'client_id':CLIENT_ID,
            'client_secret':CLIENT_SECRET
           }
    headers = { 'content-type': 'application/json' }
    url = 'https://' + DOMAIN + '/oauth/token'
    r = requests.post(url, json=body, headers=headers)
    print(r.json())
    token = r.json().get('id_token')
    if token is None:
        return ERROR_UNAUTHORIZED, 401
    return {'token': token}, 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

