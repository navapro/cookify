import { handleTokenExpiration, isTokenExpiredError } from "@/utils/auth";

const API_BASE_URL = "http://localhost:5001/api";

// Helper function to handle API responses and detect token expiration
const handleApiResponse = async (response: Response) => {
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { error: "Unknown error" };
    }

    const errorMessage = errorData.error || errorData.msg || "Request failed";
    
    // Check if it's a token expiration error
    if (response.status === 401 && (
      errorMessage.includes('Token has expired') ||
      errorMessage.includes('token expired') ||
      errorMessage.includes('jwt expired') ||
      errorMessage.includes('Signature verification failed')
    )) {
      // Automatically logout and redirect
      handleTokenExpiration();
      throw new Error("Session expired. Please log in again.");
    }
    
    throw new Error(errorMessage);
  }
  
  return response.json();
};

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

// User Details
export const getUserDetails = async (userId: number): Promise<User> => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to fetch user details");
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
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const response = await fetch(`${API_BASE_URL}/recipes/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify(recipeData),
  });

  return handleApiResponse(response);
};

export const getRecipe = async (id: number) => {
  const response = await fetch(`${API_BASE_URL}/recipes/${id}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to fetch recipe");
  }

  return response.json();
};

export const getUserRecipes = async (userId: number): Promise<Recipe[]> => {
  const response = await fetch(`${API_BASE_URL}/recipes/user/${userId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to fetch user recipes");
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

export const getUserCookLists = async (userId: number) => {
  const response = await fetch(`${API_BASE_URL}/cooklists/user/${userId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to fetch user cooklists");
  }

  return response.json();
};

export const createCookList = async (name: string, description: string = "", userId: number) => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const response = await fetch(`${API_BASE_URL}/cooklists/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({ name, description, user_id: userId }),
  });

  return handleApiResponse(response);
};

export const addRecipeToCookList = async (cooklistId: number, recipeId: number) => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const response = await fetch(`${API_BASE_URL}/cooklists/${cooklistId}/recipes`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({ recipe_id: recipeId }),
  });

  return handleApiResponse(response);
};

// get sorted cooklists - BASIC FEATURE 3
export const getCookListRecipes = async (cookListId: number, sort: string = "date_desc") => {
  const response = await fetch(`${API_BASE_URL}/cooklists/${cookListId}/recipes?sort=${sort}`);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to fetch cooklist recipes");
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

export const likeRecipe = async (recipeId: number) => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}/like`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });

  return handleApiResponse(response);
};

export const unlikeRecipe = async (recipeId: number) => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}/unlike`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });

  return handleApiResponse(response);
};

export const checkRecipeLiked = async (recipeId: number) => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("No access token found");
  }

  const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}/liked`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });

  return handleApiResponse(response);
};
