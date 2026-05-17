const API_URL = "http://127.0.0.1:8000";

export async function registerUser(login: string, password: string) {
  const response = await fetch(`${API_URL}/registration`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ login, password }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Ошибка регистрации");
  }
  return response.json();
}

export async function loginUser(username: string, password: string) {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  const response = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Ошибка входа");
  }

  return response.json();
}
