const API_BASE_URL = "http://localhost:5001/api";

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
  points: number;
  level: string;
}

export interface UserStats {
  points: number;
  cookify_level: string;
  recipes_created: number;
  cooklists_created: number;
}

export interface CookList {
  id: number;
  name: string;
  description: string;
  user: string;
  recipes: string[];
}

export interface ShoppingList {
  id: number;
  name: string;
  cooklist_id?: number;
  cooklist_name?: string;
  created_at: string;
  updated_at: string;
  total_items: number;
  purchased_items: number;
}

export interface ShoppingListItem {
  ingredient_id: number;
  name: string;
  quantity: string;
  is_purchased: boolean;
  category: string;
  price?: number;
  added_at: string;
}

export interface ShoppingListDetail {
  id: number;
  name: string;
  cooklist_id?: number;
  cooklist_name?: string;
  items: ShoppingListItem[];
}

// Authentication
export const login = async (email: string, password: string) => {
  const response = await fetch(`${API_BASE_URL}/users/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Login failed");
  }

  return response.json();
};

export const register = async (name: string, email: string, password: string) => {
  const response = await fetch(`${API_BASE_URL}/users/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Registration failed");
  }

  return response.json();
};

// User Statistics
export const getUserStats = async (userId: number): Promise<UserStats> => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const response = await fetch(`${API_BASE_URL}/users/${userId}/stats`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to fetch user stats");
  }

  return response.json();
};

// Recipes
export const getRecipes = async () => {
  const response = await fetch(`${API_BASE_URL}/recipes/`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to fetch recipes");
  }

  return response.json();
};

// Create a new recipe
export const createRecipe = async (recipeData) => {
  const response = await fetch(`${API_BASE_URL}/recipes/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(recipeData),
  });

  if (!response.ok) {
    let errorMsg = "Failed to create recipe";
    try {
      const errorJson = await response.json();
      errorMsg = errorJson.error || errorMsg;
    } catch {
      // ignore JSON parse errors
    }
    throw new Error(errorMsg);
  }

  return response.json();
};

export const getRecipe = async (id: number) => {
  const response = await fetch(`${API_BASE_URL}/recipes/${id}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to fetch recipe");
  }

  return response.json();
};

// CookLists
export const getCookLists = async () => {
  const response = await fetch(`${API_BASE_URL}/cooklists/`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to fetch cooklists");
  }

  return response.json();
};

export const getCookList = async (id: number) => {
  const response = await fetch(`${API_BASE_URL}/cooklists/${id}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to fetch cooklist");
  }

  return response.json();
};

// Shopping Lists
export const getShoppingLists = async (): Promise<ShoppingList[]> => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const response = await fetch(`${API_BASE_URL}/shopping-lists/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to fetch shopping lists");
  }

  return response.json();
};

export const getShoppingList = async (id: number): Promise<ShoppingListDetail> => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const response = await fetch(`${API_BASE_URL}/shopping-lists/${id}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to fetch shopping list");
  }

  return response.json();
};

export const createShoppingList = async (name: string, cooklistId?: number) => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const response = await fetch(`${API_BASE_URL}/shopping-lists/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({ name, cooklist_id: cooklistId }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to create shopping list");
  }

  return response.json();
};

export const addItemToShoppingList = async (
  shoppingListId: number,
  ingredientId: number,
  quantity: string
) => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const response = await fetch(`${API_BASE_URL}/shopping-lists/${shoppingListId}/items`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({ ingredient_id: ingredientId, quantity }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to add item to shopping list");
  }

  return response.json();
};

export const updateShoppingListItem = async (
  shoppingListId: number,
  ingredientId: number,
  isPurchased: boolean,
  quantity?: string
) => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const body: any = { is_purchased: isPurchased };
  if (quantity !== undefined) {
    body.quantity = quantity;
  }

  const response = await fetch(`${API_BASE_URL}/shopping-lists/${shoppingListId}/items/${ingredientId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to update shopping list item");
  }

  return response.json();
};

export const removeItemFromShoppingList = async (
  shoppingListId: number,
  ingredientId: number
) => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const response = await fetch(`${API_BASE_URL}/shopping-lists/${shoppingListId}/items/${ingredientId}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to remove item from shopping list");
  }

  return response.json();
};

export const deleteShoppingList = async (shoppingListId: number) => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const response = await fetch(`${API_BASE_URL}/shopping-lists/${shoppingListId}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to delete shopping list");
  }

  return response.json();
};
