export interface User {
  id: number;
  name: string;
  email: string;
}

export const getAccessToken = (): string | null => {
  return localStorage.getItem("access_token");
};

export const getUser = (): User | null => {
  const userStr = localStorage.getItem("user");
  if (!userStr) return null;
  
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
};

export const isAuthenticated = (): boolean => {
  return !!getAccessToken();
};

export const logout = (): void => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");
};

export const setAuthData = (accessToken: string, user: User): void => {
  localStorage.setItem("access_token", accessToken);
  localStorage.setItem("user", JSON.stringify(user));
}; 