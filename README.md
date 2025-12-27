# Tarpaulin- A Course Management Tool
Tarpaulin is a RESTful API for a fake course management tool called Tarpaulin. It has a number of functions that allow for manipulating users and their courses.
## Endpoints
### User Login
Generates a JWT for a registered user of the app by sending a request to an Auth0 domain created for the REST API to get a token. Contains the username and password for the user in the body of the request.
```
POST https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/users/login
```
### Get all Users
Returns an array with all 9 pre-created users from the kind "users" in Datastore.
```
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/users
```
### Get a User
Returns the details of one user.
```
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/users/:user_id
```
### Create/Update a User's Avatar
Uploads a .png in the request as the user's avatar to Google Cloud Storage. If there is already an avatar for the user, it gets updated with the new file.
```
POST https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/users/:user_id/avatar
```
### Get a User's Avatar
Return the file stored in Google Cloud Storage as the user's avatar.
```
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/users/:user_id/avatar
```
### Delete a User's Avatar
Delete the file stored in Google Cloud Storage as the user's avatar.
```
DELETE https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/users/:user_id/avatar
```
### Create a Course
Create a course.
```
POST https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses
```
### Get all Courses
Returns a paginated list of all courses.
```
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses?offset=3&limit=3
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses?offset=12&limit=6
```
### Get a Course
Returns an existing course.
```
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses/:course_id
```
### Update a Course
Performs a partial update on the course.
```
PATCH https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses/:course_id
```
### Delete a Course
Deletes a course.
```
DELETE https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses/:course_id
```
### Update Enrollment in a Course
Enroll and/or disenroll students from a course.
```
PATCH https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses/:course_id/students
```
### Get Enrollment for a Course
Get the list of students enrolled in a course.
```
GET https://ekacala-tarpaulin-portfolio.uc.r.appspot.com/courses/:course_id/students
```
