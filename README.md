# Tarpaulin- A Course Management Tool
Tarpaulin is a RESTful API for a fake course management tool called Tarpaulin. It has a number of functions that allow for manipulating user accounts and their courses. This README includes a detailed list of each endpoint included in the API.

*As this course management tool has been made for demonstration purposes, all users have been generated ahead of time. Their usernames and password are listed within the **User Login** endpoint.*

## Endpoints
### User Login
Generates a JWT for a registered user of the app by sending a request to an Auth0 domain created for the REST API to get a token.
```
POST https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/users/login
```

**Request Body**  
JSON format
<table>
  <tr>
    <th>Name</th>
    <th>Description</th>
    <th>Required?</th>
  </tr>
  <tr>
    <td>username</td>
    <td>User's username</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>password</td>
    <td>User's password</td>
    <td>Yes</td>
  </tr>
</table>

```
{ 
	"username": "{{username}}",
	"password": "{{password}}"
}
```

**List of all pre-generated usernames:**  
<ul>
	<li>admin1@osu.com</li>
	<li>instructor1@osu.com</li>
	<li>instructor2@osu.com</li>
	<li>student1@osu.com</li>
	<li>student2@osu.com</li>
	<li>student3@osu.com</li>
	<li>student4@osu.com</li>
	<li>student5@osu.com</li>
	<li>student6@osu.com</li>
</ul>

*Every user shares the same password: **Tarp1234!*** 

**Responses**  
<table>
	<tr>
		<th>Outcome</th>
		<th>Status Code</th>
		<th>Notes</th>
	</tr>
	<tr>
		<td>Success</td>
		<td>200</td>
		<td>Only one property, token, whose value is the JWT</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>400</td>
		<td>Request body is invalid</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>401</td>
		<td>Username and/or password is incorrect</td>
	</tr>
</table>

### Get all Users
Returns an array with all 9 pre-created users from the kind "users" in Datastore.
```
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/users
```

**Protection**  
Only users with the role *admin*

**Header**  
The JWT as a Bearer token in the Authorization header

**Responses**  
<table>
	<tr>
		<th>Outcome</th>
		<th>Status Code</th>
		<th>Notes</th>
	</tr>
	<tr>
		<td>Success</td>
		<td>200</td>
		<td></td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>401</td>
		<td>The JWT is missing or invalid</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>403</td>
		<td>The JWT is valid but doesn't belong to an admin</td>
	</tr>
</table>

### Get a User
Returns the details of one user.
```
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/users/:user_id
```

**Header**  
The JWT as a Bearer token in the Authorization header

**Responses**  
<table>
	<tr>
		<th>Outcome</th>
		<th>Status Code</th>
		<th>Notes</th>
	</tr>
	<tr>
		<td>Success</td>
		<td>200</td>
		<td></td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>401</td>
		<td>The JWT is missing or invalid, regardless of whether the user exists or not</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>403</td>
		<td>The JWT is valid, but the user doesn't exist. The JWT is valid, and the user exists, but the JWT does not.</td>
	</tr>
</table>

### Create/Update a User's Avatar
Uploads a .png in the request as the user's avatar to Google Cloud Storage. If there is already an avatar for the user, it gets updated with the new file.
```
POST https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/users/:user_id/avatar
```

**Protection**  
JWT is owned by user_id in the path parameter

**Header**  
The JWT as a Bearer token in the Authorization header

**Request Body**  
Form-data with one required key file in .png format

**Responses**  
<table>
	<tr>
		<th>Outcome</th>
		<th>Status Code</th>
		<th>Notes</th>
	</tr>
	<tr>
		<td>Success</td>
		<td>200</td>
		<td></td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>400</td>
		<td>The request doesn't contain the key file</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>401</td>
		<td>The JWT is missing or invalid</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>403</td>
		<td>The JWT is valid but doesn't belong to the user whose ID is in the path parameter</td>
	</tr>
</table>

### Get a User's Avatar
Return the file stored in Google Cloud Storage as the user's avatar.
```
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/users/:user_id/avatar
```

**Protection**  
JWT is owned by user_id in the path parameter

**Header**  
The JWT as a Bearer token in the Authorization header

**Responses**  
<table>
	<tr>
		<th>Outcome</th>
		<th>Status Code</th>
		<th>Notes</th>
	</tr>
	<tr>
		<td>Success</td>
		<td>200</td>
		<td></td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>401</td>
		<td>The JWT is missing or invalid</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>403</td>
		<td>The JWT is valid but doesn't belong to the user whose ID is in the path parameter</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>404</td>
		<td>The JWT is valid, belongs to the user whose ID is in the path parameter, but the user doesn't have an avatar
		</td>
	</tr>
</table>

### Delete a User's Avatar
Delete the file stored in Google Cloud Storage as the user's avatar.
```
DELETE https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/users/:user_id/avatar
```

**Protection**  
JWT is owned by user_id in the path parameter

**Header**  
The JWT as a Bearer token in the Authorization header

**Responses**  
<table>
	<tr>
		<th>Outcome</th>
		<th>Status Code</th>
		<th>Notes</th>
	</tr>
	<tr>
		<td>Success</td>
		<td>204</td>
		<td></td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>401</td>
		<td>The JWT is missing or invalid</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>403</td>
		<td>The JWT is valid but doesn't belong to the user whose ID is in the path parameter</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>404</td>
		<td>The JWT is valid, belongs to the user whose ID is in the path parameter, but the user doesn't have an avatar
		</td>
	</tr>
</table>

### Create a Course
Create a course.
```
POST https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses
```

**Protection**  
Only users with the role *admin*

**Header**  
The JWT as a Bearer token in the Authorization header

**Request Body**  
JSON format
<table>
  <tr>
    <th>Name</th>
    <th>Description</th>
    <th>Required?</th>
  </tr>
  <tr>
    <td>subject</td>
    <td>String. Subject code up to 4 characters.</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>number</td>
    <td>Integer</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>title</td>
    <td>String. Course title. Up to 50 characters.</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>term</td>
    <td>String. Up to 10 characters.</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>instructor_id</td>
    <td>Integer. The instructor assigned to teach the course.</td>
    <td>Yes</td>
  </tr>
</table>

```
{ 
	"subject": "CS",
  "number": 493,
  "title": "Cloud Application Development",
  "term": "fall-26",
  "instructor_id": {{instructor1_id}}
}
```

**Responses**  
<table>
	<tr>
		<th>Outcome</th>
		<th>Status Code</th>
		<th>Notes</th>
	</tr>
	<tr>
		<td>Success</td>
		<td>201</td>
		<td></td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>400</td>
		<td>The request is missing any of the attributes or the value of instructor_id doesn't correspond to the id of an instructor</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>401</td>
		<td>The JWT is missing or invalid</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>403</td>
		<td>The JWT is valid but doesn't belong to an admin</td>
	</tr>
</table>

### Get all Courses
Returns a paginated list of all courses.
```
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses?offset=3&limit=3
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses?offset=12&limit=6
```

**Responses**  
<table>
	<tr>
		<th>Outcome</th>
		<th>Status Code</th>
		<th>Notes</th>
	</tr>
	<tr>
		<td>Success</td>
		<td>200</td>
		<td></td>
	</tr>
</table>

### Get a Course
Returns an existing course.
```
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses/:course_id
```

**Responses**  
<table>
	<tr>
		<th>Outcome</th>
		<th>Status Code</th>
		<th>Notes</th>
	</tr>
	<tr>
		<td>Success</td>
		<td>200</td>
		<td></td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>404</td>
		<td>No course with this ID exists</td>
	</tr>
</table>

### Update a Course
Performs a partial update on the course.
```
PATCH https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses/:course_id
```

**Protection**  
Only users with the role *admin*

**Header**  
The JWT as a Bearer token in the Authorization header

**Request Body**  
JSON format
<table>
  <tr>
    <th>Name</th>
    <th>Description</th>
    <th>Required?</th>
  </tr>
  <tr>
    <td>subject</td>
    <td>String. Subject code up to 4 characters.</td>
    <td>No</td>
  </tr>
  <tr>
    <td>number</td>
    <td>Integer</td>
    <td>No</td>
  </tr>
  <tr>
    <td>title</td>
    <td>String. Course title. Up to 50 characters.</td>
    <td>No</td>
  </tr>
  <tr>
    <td>term</td>
    <td>String. Up to 10 characters.</td>
    <td>No</td>
  </tr>
  <tr>
    <td>instructor_id</td>
    <td>Integer. The instructor assigned to teach the course.</td>
    <td>No</td>
  </tr>
</table>

```
{ 
  "term": "spring-26"
}
```

**Responses**  
<table>
	<tr>
		<th>Outcome</th>
		<th>Status Code</th>
		<th>Notes</th>
	</tr>
	<tr>
		<td>Success</td>
		<td>200</td>
		<td></td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>400</td>
		<td>The request contains the property instructor_id, but the value of instructor_id doesn't correspond to the id of an instructor</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>401</td>
		<td>The JWT is missing or invalid, regardless of whether a course with this ID exists or not</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>403</td>
		<td>The JWT is valid, but the course doesn't exist. The JWT is valid, and the course exists, but the JWT doesn't belong to an admin</td>
	</tr>
</table>

### Delete a Course
Deletes a course.
```
DELETE https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses/:course_id
```

**Protection**  
Only users with the role *admin*

**Header**  
The JWT as a Bearer token in the Authorization header

**Responses**  
<table>
	<tr>
		<th>Outcome</th>
		<th>Status Code</th>
		<th>Notes</th>
	</tr>
	<tr>
		<td>Success</td>
		<td>204</td>
		<td></td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>401</td>
		<td>The JWT is missing or invalid, regardless of whether a course with this ID exists or not</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>403</td>
		<td>The JWT is valid, but the course doesn't exist. The JWT is valid, and the course exists, but the JWT doesn't belong to an admin</td>
	</tr>
</table>

### Update Enrollment in a Course
Enroll and/or disenroll students from a course.
```
PATCH https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses/:course_id/students
```

**Protection**  
Uer with admin role or when JWT is owned by the instructor of this course

**Header**  
The JWT as a Bearer token in the Authorization header

**Request Body**  
JSON format
<table>
  <tr>
    <th>Name</th>
    <th>Description</th>
    <th>Required?</th>
  </tr>
  <tr>
    <td>add</td>
    <td>An array, possibly empty, containing student IDs for students to enroll in the course.</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>remove</td>
    <td>An array, possibly empty, containing student IDs for students to be removed from the course.</td>
    <td>Yes</td>
  </tr>
</table>

```
{ 
  "add": [{{studentid_1}}, {{studentid_2}}, {{studentid_3}}],
  "remove": []
}
```

**Responses**  
<table>
	<tr>
		<th>Outcome</th>
		<th>Status Code</th>
		<th>Notes</th>
	</tr>
	<tr>
		<td>Success</td>
		<td>200</td>
		<td></td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>401</td>
		<td>The JWT is missing or invalid, regardless of whether a course with this ID exists or not</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>403</td>
		<td>The JWT is valid, but the course doesn't exist. The JWT is valid, and the course exists, but the JWT doesn't belong to either an admin or the instructor of the course</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>409</td>
		<td>The enrollment data in the arrays "add" and/or "remove" is invalid</td>
	</tr>
</table>

### Get Enrollment for a Course
Get the list of students enrolled in a course.
```
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses/:course_id/students
```

**Protection**  
User with admin role or when JWT is owned by the instructor of this course

**Header**  
The JWT as a Bearer token in the Authorization header

**Responses**  
<table>
	<tr>
		<th>Outcome</th>
		<th>Status Code</th>
		<th>Notes</th>
	</tr>
	<tr>
		<td>Success</td>
		<td>200</td>
		<td></td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>401</td>
		<td>The JWT is missing or invalid, regardless of whether a course with this ID exists or not</td>
	</tr>
	<tr>
		<td>Failure</td>
		<td>403</td>
		<td>The JWT is valid, but the course doesn't exist. The JWT is valid, and the course exists, but the JWT doesn't belong to either an admin or the instructor of the course</td>
	</tr>
</table>
