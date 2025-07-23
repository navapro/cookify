import { useState, useEffect } from "react";
import { ArrowLeft, ChefHat, Award, Package } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { RecipeCard } from "@/components/RecipeCard";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel";
import { getUser } from "@/utils/auth";
import { getUserDetails, getUserStats, getUserRecipes, getUserCookLists, getCookList, getUserIngredients, type User, type UserStats, type Recipe, type UserIngredient } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { getCookListRecipes } from "@/services/api";
import { useLikedRecipes } from "@/contexts/LikedRecipesContext";

// Helper function to convert cookify level to title with emojis
const getCookifyLevelTitle = (level: string): string => {
  switch (level) {
    case "Remy the Rat":
      return "👑🐭 Remy the Rat";
    case "Michelin Star Chef":
      return "👨‍🍳 Michelin Star Chef";
    case "Head Chef":
      return "👨‍🍳 Head Chef";
    case "Sous Chef":
      return "🧂 Sous Chef";
    case "Chef":
      return "👨‍🍳 Chef";
    case "Prep Cook":
      return "🔪 Prep Cook";
    case "Dishwasher":
      return "🧽 Dishwasher";
    case "Street Rat":
      return "🐀 Street Rat";
    default:
      return `🍳 ${level}`;
  }
};

const Profile = () => {
  const navigate = useNavigate();
  const [selectedCookList, setSelectedCookList] = useState<any | null>(null);
  const [userDetails, setUserDetails] = useState<User | null>(null);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [userRecipes, setUserRecipes] = useState<Recipe[]>([]);
  const [userCookLists, setUserCookLists] = useState<any[]>([]);
  const [userIngredients, setUserIngredients] = useState<UserIngredient[]>([]);
  const [loading, setLoading] = useState(true);
  const [cookListRecipes, setCookListRecipes] = useState<any[]>([]);
  const [cookListSort, setCookListSort] = useState<'date_desc' | 'date_asc' | 'name_asc'>('date_desc');
  const { toast } = useToast();
  const { likedRecipesVersion } = useLikedRecipes();
  
  // Get the current user's information
  const currentUser = getUser();
  const userName = userDetails?.name || currentUser?.name || "Chef";

  useEffect(() => {
    const fetchUserData = async () => {
      if (currentUser?.id) {
        try {
          // Fetch user details, stats, recipes, cooklists, and ingredients
          const [details, stats, recipes, cookLists, ingredients] = await Promise.all([
            getUserDetails(currentUser.id),
            getUserStats(currentUser.id),
            getUserRecipes(currentUser.id),
            getUserCookLists(currentUser.id),
            getUserIngredients(currentUser.id)
          ]);
          
          setUserDetails(details);
          setUserStats({
            ...stats,
            cookify_level: getCookifyLevelTitle(stats.cookify_level) // Change from Number(details.level)
          });
          setUserRecipes(recipes);
          setUserCookLists(cookLists);
          setUserIngredients(ingredients);
        } catch (error) {
          console.error("Failed to fetch user data:", error);
          // Set default values if API fails
          setUserStats({
            points: 0,
            cookify_level: "🐀 Street Rat",
            recipes_created: 0,
            cooklists_created: 0
          });
        } finally {
          setLoading(false);
        }
      } else {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [currentUser?.id]);

  // Refresh cooklists when liked recipes change
  useEffect(() => {
    const refreshCookLists = async () => {
      if (currentUser?.id && likedRecipesVersion > 0) {
        try {
          const cookLists = await getUserCookLists(currentUser.id);
          setUserCookLists(cookLists);
          
          // If we're currently viewing a cooklist, refresh its recipes too
          if (selectedCookList) {
            fetchCookListRecipes(selectedCookList.id, cookListSort);
          }
        } catch (error) {
          console.error("Failed to refresh cooklists:", error);
        }
      }
    };

    refreshCookLists();
  }, [likedRecipesVersion, currentUser?.id, selectedCookList?.id, cookListSort]);

  const handleBackClick = () => {
    if (selectedCookList) {
      setSelectedCookList(null);
    } else {
      navigate("/");
    }
  };

  // Fetch cooklist details and recipes (with sorting)
  const handleCookListClick = async (cookList: any) => {
    try {
      // Fetch detailed cooklist data with recipes
      const detailedCookList = await getCookList(cookList.id);
      setSelectedCookList(detailedCookList);
      // Fetch sorted recipes for this cooklist
      fetchCookListRecipes(cookList.id, cookListSort);
    } catch (error) {
      console.error('Error fetching cooklist details:', error);
      setSelectedCookList(cookList);
      setCookListRecipes([]);
    }
  };

  // Fetch recipes for a cooklist with sorting
  const fetchCookListRecipes = async (cookListId: number, sort: string) => {
    try {
      const data = await getCookListRecipes(cookListId, sort);
      setCookListRecipes(data);
    } catch (err) {
      setCookListRecipes([]);
      toast({
        title: "Error",
        description: "Failed to fetch cooklist recipes.",
        variant: "destructive",
      });
    }
  };

  // When sort changes, refetch recipes for the selected cooklist
  useEffect(() => {
    if (selectedCookList) {
      fetchCookListRecipes(selectedCookList.id, cookListSort);
    }
    // eslint-disable-next-line
  }, [cookListSort, selectedCookList?.id]);

  // Chef level styling based on level title
  const getChefLevelStyle = (level: string) => {
    switch (level) {
      case "👑🐭 Remy the Rat":
        return { color: "text-purple-600", bgColor: "bg-purple-100" };
      case "👨‍🍳 Michelin Star Chef":
        return { color: "text-red-600", bgColor: "bg-red-100" };
      case "👨‍🍳 Head Chef":
        return { color: "text-orange-600", bgColor: "bg-orange-100" };
      case "🧂 Sous Chef":
        return { color: "text-green-600", bgColor: "bg-green-100" };
      case "👨‍🍳 Chef":
        return { color: "text-blue-600", bgColor: "bg-blue-100" };
      case "🔪 Prep Cook":
        return { color: "text-indigo-600", bgColor: "bg-indigo-100" };
      case "🧽 Dishwasher":
        return { color: "text-gray-600", bgColor: "bg-gray-100" };
      case "🐀 Street Rat":
        return { color: "text-gray-500", bgColor: "bg-gray-50" };
      default:
        return { color: "text-gray-500", bgColor: "bg-gray-50" };
    }
  };

  const chefLevelStyle = getChefLevelStyle(userStats?.cookify_level || "🐀 Street Rat");

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-100 via-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-blue-600 text-lg font-medium">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-blue-50 to-indigo-50 relative">
      {/* Grainy texture overlay */}
      <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_1px_1px,rgba(255,255,255,0.8)_1px,transparent_0)] bg-[length:20px_20px]"></div>
      
      <div className="relative z-10">
        {/* Header */}
        <header className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 shadow-xl">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleBackClick}
              className="hover:bg-blue-500 text-white"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <h1 className="text-2xl font-bold">
              {selectedCookList ? selectedCookList.name : "My Profile"}
            </h1>
          </div>
        </header>

        <div className="p-6">
          {!selectedCookList ? (
            <>
              {/* Profile Info */}
              <div className="bg-white rounded-lg shadow-md p-6 mb-8 border border-blue-100">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                    <ChefHat className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-blue-800">Chef {userName}</h2>
                    <p className="text-blue-600 text-sm">{userDetails?.email}</p>
                    <p className="text-blue-600 italic mt-1">"Anyone can cook, but only the fearless can be great!"</p>
                    <div className={`inline-flex items-center gap-2 mt-2 px-3 py-1 rounded-full ${chefLevelStyle.bgColor}`}>
                      <Award className="w-4 h-4" />
                      <span className={`text-sm font-medium ${chefLevelStyle.color}`}>{userStats?.cookify_level}</span>
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                    <div className="text-2xl font-bold text-blue-700">{userStats?.cookify_level || "🐀 Street Rat"}</div>
                    <div className="text-blue-600 text-sm">Chef Level</div>
                    <div className="text-sm text-blue-500 mt-1">{userDetails?.points || 0} points</div>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                    <div className="text-2xl font-bold text-blue-700">{userStats?.recipes_created || 0}</div>
                    <div className="text-blue-600 text-sm">Recipes Created</div>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                    <div className="text-2xl font-bold text-blue-700">{userStats?.cooklists_created || 0}</div>
                    <div className="text-blue-600 text-sm">Cook Lists</div>
                  </div>
                </div>
              </div>

              {/* My Recipes Carousel */}
              <div className="mb-8">
                <h3 className="text-xl font-bold text-blue-800 mb-4">My Latest Recipes</h3>
                <div className="bg-white rounded-lg shadow-md p-6 border border-blue-100">
                  {userRecipes.length > 0 ? (
                    <Carousel className="w-full">
                      <CarouselContent className="-ml-2 md:-ml-4">
                        {userRecipes.map((recipe: Recipe) => (
                          <CarouselItem key={recipe.id} className="pl-2 md:pl-4 md:basis-1/2 lg:basis-1/3">
                            <RecipeCard recipe={recipe} />
                          </CarouselItem>
                        ))}
                      </CarouselContent>
                      <CarouselPrevious className="left-2" />
                      <CarouselNext className="right-2" />
                    </Carousel>
                  ) : (
                    <div className="text-center py-8 text-blue-600">
                      <ChefHat className="w-12 h-12 mx-auto mb-4 text-blue-400" />
                      <p className="text-lg font-medium mb-2">No recipes yet!</p>
                      <p className="text-sm">Create your first recipe to see it here.</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Cook Lists */}
              <div className="mb-8">
                <h3 className="text-xl font-bold text-blue-800 mb-4">My Cook Lists</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {userCookLists.length > 0 ? (
                    userCookLists.map((cookList) => (
                      <div
                        key={cookList.id}
                        onClick={() => handleCookListClick(cookList)}
                        className="bg-white rounded-lg shadow-md p-6 border border-blue-100 hover:shadow-lg transition-all duration-200 cursor-pointer hover:bg-blue-50 group"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-semibold text-blue-800 group-hover:text-blue-900">
                            {cookList.name}
                          </h4>
                          <span className="text-sm text-blue-600 bg-blue-100 px-2 py-1 rounded-full">
                            {cookList.recipeCount} recipes
                          </span>
                        </div>
                        <p className="text-blue-600 text-sm">
                          {cookList.description}
                        </p>
                        <p className="text-blue-500 text-xs mt-2 italic">
                          Click to view recipes in this collection
                        </p>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-full text-center py-8 text-blue-600">
                      <ChefHat className="w-12 h-12 mx-auto mb-4 text-blue-400" />
                      <p className="text-lg font-medium mb-2">No cook lists yet!</p>
                      <p className="text-sm">Create your first cook list to organize your recipes.</p>
                    </div>
                  )}
                </div>
              </div>

              {/* My Pantry */}
              <div>
                <h3 className="text-xl font-bold text-blue-800 mb-4">My Pantry</h3>
                <div className="bg-white rounded-lg shadow-md p-6 border border-blue-100">
                  {userIngredients.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {userIngredients.map((ingredient) => (
                        <div
                          key={ingredient.ingredient_id}
                          className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border border-green-100 hover:shadow-md transition-all duration-200"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <Package className="w-4 h-4 text-green-600" />
                              <h4 className="font-semibold text-green-800">{ingredient.name}</h4>
                            </div>
                            {ingredient.category && (
                              <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">
                                {ingredient.category}
                              </span>
                            )}
                          </div>
                          <p className="text-green-700 font-medium mb-1">
                            Quantity: {ingredient.quantity}
                          </p>
                          {ingredient.season && (
                            <p className="text-green-600 text-sm">
                              Season: {ingredient.season}
                            </p>
                          )}
                          {ingredient.price && (
                            <p className="text-green-600 text-sm">
                              Est. Price: ${ingredient.price}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-blue-600">
                      <Package className="w-12 h-12 mx-auto mb-4 text-blue-400" />
                      <p className="text-lg font-medium mb-2">Your pantry is empty!</p>
                      <p className="text-sm">Add ingredients to track what you have available for cooking.</p>
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <>
              {/* Cook List Details */}
              <div className="bg-white rounded-lg shadow-md p-6 mb-6 border border-blue-100">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                    <ChefHat className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-blue-800">{selectedCookList.name}</h2>
                    <p className="text-blue-600">{selectedCookList.recipeCount} recipes in this collection</p>
                  </div>
                </div>
                {/* Sorting Buttons */}
                <div className="flex gap-2 mt-2">
                  <Button
                    variant={cookListSort === "date_desc" ? "default" : "outline"}
                    onClick={() => setCookListSort("date_desc")}
                  >
                    Newest First
                  </Button>
                  <Button
                    variant={cookListSort === "date_asc" ? "default" : "outline"}
                    onClick={() => setCookListSort("date_asc")}
                  >
                    Oldest First
                  </Button>
                  <Button
                    variant={cookListSort === "name_asc" ? "default" : "outline"}
                    onClick={() => setCookListSort("name_asc")}
                  >
                    A-Z
                  </Button>
                </div>
              </div>

              {/* Recipes in Cook List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {cookListRecipes.map(recipe => (
                  <RecipeCard key={recipe.id} recipe={{
                    ...recipe,
                    title: recipe.name, // adapt backend field to frontend
                    image: recipe.image || "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=500&h=300",
                    ingredients: recipe.ingredients || [],
                    instructions: recipe.instructions || [],
                    added_at: recipe.added_at,
                  }} />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
