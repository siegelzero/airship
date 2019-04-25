# Example Contacts API

## Setup
All necessary packages are included in `requirements.txt`. To set up these packages in a virtual environment, execute
```bash
make venv
```

## Running the service
You can start the service by executing
```bash
make start
```
This starts the service on `http://localhost:5000/`.

## Tests
Run unit tests by executing
```bash
make test
```

## Using the API
You can use the API from the command line via `curl`. Very basic username/password authentication is performed for endpoints that modify data. The file `credentials.json` contains valid username/password pairs. Edit this file as needed to add new users.
### Creating a new contact
```bash
curl -u admin:adminpw -d '{"name": "James"}' -H "Content-Type: application/json" -X POST http://localhost:5000/contacts/
```
This yelds
```bash
{
  "data": [
    {
      "created_by": "admin",
      "created_time": "Thu, 25 Apr 2019 21:33:56 GMT",
      "email": "",
      "id": "9b779040-46d9-4554-b451-772dfa388cc5",
      "last_modified_by": "admin",
      "last_modified_time": "Thu, 25 Apr 2019 21:33:56 GMT",
      "name": "James",
      "phone": ""
    }
  ]
}
```
reflecting the contact just created.

### Getting lists of contacts
```bash
curl -X GET "http://127.0.0.1:5000/contacts/"
```

### Getting a specific contact by `id`.
To get the data for the contact with id `id`, execute
```bash
curl -X GET "http://127.0.0.1:5000/contacts/9b779040-46d9-4554-b451-772dfa388cc5"
```

### Getting contacts by filtering.
To get a list of all contacts with given name "Charles", execute
```bash
curl -d '{"name": "Charles"}' -H "Content-Type: application/json" -X GET http://localhost:5000/contacts/
```
You may specify/filter-by any of the fields in the model.

### Updating a contact.
To update a field in a given contact, execute
```bash
curl -u admin:adminpw -d '{"name": "Charlie"}' -H "Content-Type: application/json" -X PATCH http://localhost:5000/contacts/9b779040-46d9-4554-b451-772dfa388cc5
```
This updates the record with given `id` to have `"name": "Charlie"` instead of `"Charles"`.

### Deleting a contact by `id`.
Delete a contact by
```bash
curl -u admin:adminpw -H "Content-Type: application/json" -X DELETE http://localhost:5000/contacts/9b779040-46d9-4554-b451-772dfa388cc5
```



