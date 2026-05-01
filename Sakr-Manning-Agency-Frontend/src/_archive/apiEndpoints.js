// utils/apiEndpoints.js

export const API_BASE_URL = "http://localhost:8000/api";

export const ENDPOINTS = {
  //  Authentication
  LOGIN: `${API_BASE_URL}/auth/login/`, // POST { email, password }
  SIGNUP: `${API_BASE_URL}/auth/signup/`, // POST { name, email, password }
  SEND_CODE: `${API_BASE_URL}/auth/send-code/`, // POST { email }
  VERIFY_CODE: `${API_BASE_URL}/auth/verify-code/`, // POST { email, code }
  RESEND_CODE: `${API_BASE_URL}/auth/resend-code/`, // POST { email }
  LOGOUT: `${API_BASE_URL}/auth/logout/`, // POST (token in header)

  //  User
  CURRENT_USER: `${API_BASE_URL}/user/me/`, // GET (token in header)

  // Sakr Form
  FORM_SUBMIT: `${API_BASE_URL}/forms/sakr/`, // POST { userId, formData }
  FORM_MY: `${API_BASE_URL}/forms/my/`, // GET (user's submitted forms)
};

/*
---------------------------------------
1. All auth endpoints return JSON with { success: boolean, ... }.
2. JWT authentication is assumed → return `token` on login/signup/verify.
   - Frontend will include `Authorization: Bearer <token>` for protected routes.
3. SakrForm submission:
   - `POST /forms/sakr/` → expects { userId, formData }.
   - `GET /forms/my/` → returns all forms submitted by logged-in user.
4. Error handling:
   - If request fails (bad credentials, invalid code, etc.), return
     { "success": false, "error": "Message here" } with appropriate status.
*/
