# PMRSmartContractAPI


## Database

we use SQLite database to store user information and their conversations. The database file is located at `notes.db` in the project directory.

## API Endpoints

### Authentication

- **POST /login**

  - Description: Endpoint for user authentication and token generation.
  - Request Body:
    - `username` (string): User's username.
    - `password` (string): User's password.
  - Response:
    - `access_token` (string): Generated access token.
    - `token_type` (string): Token type (e.g., "bearer").

### User Conversations

- **GET /conversations**

  - Description: Get all conversations for the authenticated user.
  - Authorization: Bearer token required.
  - Response:
    - `conversations` (list): List of conversation objects.

- **POST /conversations**

  - Description: Create a new conversation for the authenticated user.
  - Authorization: Bearer token required.
  - Request Body:
    - `text` (string): Text content of the conversation.
    - `summary` (string): Summary of the conversation.
  - Response:
    - `message` (string): Success message.
    - `conversation` (object): Created conversation object.

- **POST /conversations/{conversation_id}/parts**

  - Description: Add a new part to an existing conversation.
  - Authorization: Bearer token required.
  - Path Parameters:
    - `conversation_id` (integer): ID of the conversation to add the part to.
  - Request Body:
    - `part_text` (string): Text content of the conversation part.
  - Response:
    - `message` (string): Success message.

- **DELETE /conversations/{conversation_id}**

  - Description: Delete a conversation.
  - Authorization: Bearer token required.
  - Path Parameters:
    - `conversation_id` (integer): ID of the conversation to delete.
  - Response:
    - `message` (string): Success message.

