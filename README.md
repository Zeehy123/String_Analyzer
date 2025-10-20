String Analyzer API

A Django REST Framework project that analyzes strings and stores computed components (length, palindrome check, character frequency, etc.).
Includes endpoints for creating, listing, filtering, and querying strings via natural language queries.

------------------------------------------------------------------------------------------------------------------------------------------
Features

Create a string analysis entry.

List all analyzed strings.

Filter strings by components (length, palindrome, word count, letters, etc.).

Query strings using natural language (e.g., "single word palindrome containing letter a").

JSON-safe responses.
---------------------------------------------------------------------------------------------------------------------------------
Local Setup
1️ Clone the repository
  git clone zeehy123/String_Analyzer
  cd string-analyzer

2. Create a Virtual Environment
     python -m venv venv
   
3. Activate it
    venv\Scripts\activate

4. Install all dependencies
    pip install -r requirements.txt

5. Apply migrations
    python manage.py migrate

6. Run server locally
     python manage.py runserver

-----------------------------------------------------------------------------------------------------------------------------------------
🚀 Endpoints
| Method | URL                                                      | Description                                   |
| ------ | -------------------------------------------------------- | --------------------------------------------- |
| POST   | `/api/strings/create`                                    | Create a new string analysis entry.           |
| GET    | `/api/strings/`                                          | List all analyzed strings (supports filters). |
| GET    | `/api/strings/<string_value>`                            | Get analysis for a specific string.           |
| DELETE | `/api/strings/<string_value>`                            | Delete a string analysis entry.               |
| GET    | `/api/strings/filter-by-natural-language/?query=<query>` | Query strings using natural language.         |

 ------------------------------------------------------------------------------------------------------------------------------------------
 
