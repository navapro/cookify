import { useState } from "react";
import { ArrowLeft, ChefHat, Clock, Globe, Award } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { RecipeCard } from "@/components/RecipeCard";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel";

// Mock data - in a real app this would come from a database
const mockCookLists = [
  { 
    id: 1, 
    name: "Weekend Meal Prep", 
    recipeCount: 5,
    recipes: [
      {
        id: 101,
        title: "Gordon's Perfect Scrambled Eggs",
        image: "https://images.unsplash.com/photo-1506084868230-bb9d95c24759?auto=format&fit=crop&w=500&h=300",
        duration: 10,
        cuisine: "British",
        ingredients: ["3 eggs", "butter", "crème fraîche", "chives", "salt"],
        instructions: ["Crack eggs into cold pan", "Add butter", "Stir constantly over low heat", "Finish with crème fraîche"],
        isMyRecipe: true
      },
      {
        id: 102,
        title: "Remy's Ratatouille",
        image: "https://images.unsplash.com/photo-1572441713132-51c75654db73?auto=format&fit=crop&w=500&h=300",
        duration: 45,
        cuisine: "French",
        ingredients: ["eggplant", "zucchini", "bell peppers", "tomatoes", "herbs"],
        instructions: ["Slice vegetables thin", "Arrange in spiral", "Season with herbs", "Bake until tender"],
        isMyRecipe: false
      }
    ]
  },
  { 
    id: 2, 
    name: "Quick Dinners", 
    recipeCount: 8,
    recipes: [
      {
        id: 201,
        title: "5-Minute Pasta Aglio e Olio",
        image: "https://images.unsplash.com/photo-1621996346565-e3dbc353d2e5?auto=format&fit=crop&w=500&h=300",
        duration: 15,
        cuisine: "Italian",
        ingredients: ["spaghetti", "garlic", "olive oil", "red pepper flakes", "parsley"],
        instructions: ["Boil pasta", "Sauté garlic in oil", "Toss with pasta", "Add herbs"],
        isMyRecipe: true
      }
    ]
  },
  { 
    id: 3, 
    name: "Holiday Favorites", 
    recipeCount: 3,
    recipes: [
      {
        id: 301,
        title: "Christmas Beef Wellington",
        image: "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&h=300",
        duration: 120,
        cuisine: "British",
        ingredients: ["beef tenderloin", "puff pastry", "mushrooms", "prosciutto"],
        instructions: ["Sear beef", "Wrap in mushroom duxelles", "Encase in pastry", "Bake until golden"],
        isMyRecipe: true
      }
    ]
  },
  { 
    id: 4, 
    name: "Healthy Options", 
    recipeCount: 12,
    recipes: [
      {
        id: 401,
        title: "Mediterranean Quinoa Bowl",
        image: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=500&h=300",
        duration: 25,
        cuisine: "Mediterranean",
        ingredients: ["quinoa", "cucumber", "tomatoes", "feta", "olives"],
        instructions: ["Cook quinoa", "Chop vegetables", "Mix with dressing", "Top with feta"],
        isMyRecipe: false
      }
    ]
  },
];

// Sample recipes for the carousel
const myRecipes = [
  {
    id: 501,
    title: "Gordon's Perfect Scrambled Eggs",
    image: "https://images.unsplash.com/photo-1506084868230-bb9d95c24759?auto=format&fit=crop&w=500&h=300",
    duration: 10,
    cuisine: "British",
    ingredients: ["3 eggs", "butter", "crème fraîche", "chives", "salt"],
    instructions: ["Crack eggs into cold pan", "Add butter", "Stir constantly over low heat", "Finish with crème fraîche"],
    isMyRecipe: true
  },
  {
    id: 502,
    title: "5-Minute Pasta Aglio e Olio",
    image: "https://images.unsplash.com/photo-1621996346565-e3dbc353d2e5?auto=format&fit=crop&w=500&h=300",
    duration: 15,
    cuisine: "Italian",
    ingredients: ["spaghetti", "garlic", "olive oil", "red pepper flakes", "parsley"],
    instructions: ["Boil pasta", "Sauté garlic in oil", "Toss with pasta", "Add herbs"],
    isMyRecipe: true
  },
  {
    id: 503,
    title: "Christmas Beef Wellington",
    image: "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&h=300",
    duration: 120,
    cuisine: "British",
    ingredients: ["beef tenderloin", "puff pastry", "mushrooms", "prosciutto"],
    instructions: ["Sear beef", "Wrap in mushroom duxelles", "Encase in pastry", "Bake until golden"],
    isMyRecipe: true
  },
  {
    id: 504,
    title: "Classic French Croissants",
    image: "https://images.unsplash.com/photo-1555507036-ab794f0880f2?auto=format&fit=crop&w=500&h=300",
    duration: 240,
    cuisine: "French",
    ingredients: ["flour", "butter", "yeast", "milk", "sugar"],
    instructions: ["Make dough", "Fold butter", "Roll and shape", "Proof and bake"],
    isMyRecipe: true
  },
  {
    id: 505,
    title: "Spicy Thai Pad Thai",
    image: "https://images.unsplash.com/photo-1559847844-d5d6b5a32095?auto=format&fit=crop&w=500&h=300",
    duration: 30,
    cuisine: "Thai",
    ingredients: ["rice noodles", "shrimp", "bean sprouts", "tamarind", "fish sauce"],
    instructions: ["Soak noodles", "Stir fry ingredients", "Add sauce", "Garnish with peanuts"],
    isMyRecipe: true
  }
];

const Profile = () => {
  const navigate = useNavigate();
  const [selectedCookList, setSelectedCookList] = useState<typeof mockCookLists[0] | null>(null);

  const handleBackClick = () => {
    if (selectedCookList) {
      setSelectedCookList(null);
    } else {
      navigate("/");
    }
  };

  const handleCookListClick = (cookList: typeof mockCookLists[0]) => {
    setSelectedCookList(cookList);
  };

  // Chef level calculation based on recipes created
  const getChefLevel = (recipeCount: number) => {
    if (recipeCount >= 50) return { level: "Master Chef", color: "text-purple-600", bgColor: "bg-purple-100" };
    if (recipeCount >= 30) return { level: "Expert Chef", color: "text-gold-600", bgColor: "bg-yellow-100" };
    if (recipeCount >= 15) return { level: "Skilled Chef", color: "text-orange-600", bgColor: "bg-orange-100" };
    if (recipeCount >= 5) return { level: "Home Chef", color: "text-green-600", bgColor: "bg-green-100" };
    return { level: "Beginner", color: "text-blue-600", bgColor: "bg-blue-100" };
  };

  const chefLevel = getChefLevel(23);

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
                    <h2 className="text-2xl font-bold text-blue-800">Chef Linguini</h2>
                    <p className="text-blue-600 italic">"Anyone can cook, but only the fearless can be great!"</p>
                    <div className={`inline-flex items-center gap-2 mt-2 px-3 py-1 rounded-full ${chefLevel.bgColor}`}>
                      <Award className="w-4 h-4" />
                      <span className={`text-sm font-medium ${chefLevel.color}`}>{chefLevel.level}</span>
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                    <div className="text-2xl font-bold text-blue-700">23</div>
                    <div className="text-blue-600 text-sm">Recipes Created</div>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                    <div className="text-2xl font-bold text-blue-700">4</div>
                    <div className="text-blue-600 text-sm">Cook Lists</div>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                    <div className="text-2xl font-bold text-blue-700">156</div>
                    <div className="text-blue-600 text-sm">Meals Cooked</div>
                  </div>
                </div>
              </div>

              {/* My Recipes Carousel */}
              <div className="mb-8">
                <h3 className="text-xl font-bold text-blue-800 mb-4">My Latest Recipes</h3>
                <div className="bg-white rounded-lg shadow-md p-6 border border-blue-100">
                  <Carousel className="w-full">
                    <CarouselContent className="-ml-2 md:-ml-4">
                      {myRecipes.map((recipe) => (
                        <CarouselItem key={recipe.id} className="pl-2 md:pl-4 md:basis-1/2 lg:basis-1/3">
                          <RecipeCard recipe={recipe} />
                        </CarouselItem>
                      ))}
                    </CarouselContent>
                    <CarouselPrevious className="left-2" />
                    <CarouselNext className="right-2" />
                  </Carousel>
                </div>
              </div>

              {/* Cook Lists */}
              <div>
                <h3 className="text-xl font-bold text-blue-800 mb-4">My Cook Lists</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {mockCookLists.map((cookList) => (
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
                      <p className="text-blue-600 text-sm italic">
                        Click to view recipes in this collection
                      </p>
                    </div>
                  ))}
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
              </div>

              {/* Recipes in Cook List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {selectedCookList.recipes.map(recipe => (
                  <RecipeCard key={recipe.id} recipe={recipe} />
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
