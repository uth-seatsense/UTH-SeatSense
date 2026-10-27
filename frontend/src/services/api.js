const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export async function getApiHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Backend health request failed (${response.status})`);
  }
  return response.json();
}
