const API_BASE_URL = 'http://localhost:5001/api';

export interface Recipe {
  id: number;
  title: string;
  image: string;
  duration: number;
  cuisine: string;
  ingredients: string[];
  instructions: string[];
  isMyRecipe?: boolean;
}

export interface User {
  id: number;
  name: string;
  email: string;
  level: number;
}

export interface CookList {
  id: number;
  name: string;
  description: string;
  user: string;
  recipes: string[];
}

// Authentication
export const login = async (email: string, password: string) => {
  const response = await fetch(`${API_BASE_URL}/users/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Login failed');
  }
  
  return response.json();
};

// Recipes
export const getRecipes = async () => {
  const response = await fetch(`${API_BASE_URL}/recipes/`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch recipes');
  }
  
  return response.json();
};

export const getRecipe = async (id: number) => {
  const response = await fetch(`${API_BASE_URL}/recipes/${id}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch recipe');
  }
  
  return response.json();
};

// CookLists
export const getCookLists = async () => {
  const response = await fetch(`${API_BASE_URL}/cooklists/`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch cooklists');
  }
  
  return response.json();
};

export const getCookList = async (id: number) => {
  const response = await fetch(`${API_BASE_URL}/cooklists/${id}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch cooklist');
  }
  
  return response.json();
};