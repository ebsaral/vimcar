# vimcar

## Routes

**POST** - /users

Request parameters: `email` and `password` - Both required

Example response: 

`
{
  "code": "ce5dfa32a7a347548b5331b4841ca338",
  "email": "test@me.com",
  "id": 4
}
`

**GET** - /activation/{code} (In fact, it should be a POST but I couldn't decide)


**GET** - /protected


**POST** - /login
Request parameters: `email` and `password` - Both required


**GET** - /logout

## Notes

Gunicorn and Nginx configurations are added to repository in case you would like to run with a supervisor. Be aware of the `paths`.


I don't have experience on Dockers, therefore I will leave it like this. 
