import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ChefHat, Package, ShoppingCart, ArrowLeft, Check, X } from "lucide-react";
import { getUser } from "@/utils/auth";
import { getUserCookLists, getCookListRecipes, getUserIngredients } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

interface SmartShoppingDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface IngredientComparison {
  ingredient_id: number;
  name: string;
  required_quantity: string;
  user_quantity?: string;
  has_ingredient: boolean;
  category: string;
}

export const SmartShoppingDialog = ({
  open,
  onOpenChange,
}: SmartShoppingDialogProps) => {
  const [userCookLists, setUserCookLists] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCookList, setSelectedCookList] = useState<any | null>(null);
  const [ingredientComparison, setIngredientComparison] = useState<IngredientComparison[]>([]);
  const [generatingList, setGeneratingList] = useState(false);
  const { toast } = useToast();
  const currentUser = getUser();

  useEffect(() => {
    const fetchCookLists = async () => {
      if (currentUser?.id && open) {
        try {
          setLoading(true);
          const cookLists = await getUserCookLists(currentUser.id);
          setUserCookLists(cookLists);
        } catch (error) {
          console.error("Failed to fetch cooklists:", error);
          toast({
            title: "Error",
            description: "Failed to fetch your cooklists.",
            variant: "destructive",
          });
        } finally {
          setLoading(false);
        }
      }
    };

    fetchCookLists();
  }, [currentUser?.id, open]);

  const handleCookListSelect = async (cookList: any) => {
    setSelectedCookList(cookList);
    setGeneratingList(true);
    
    try {
      // Fetch recipes in the cooklist and user's ingredients in parallel
      const [cookListRecipes, userIngredients] = await Promise.all([
        getCookListRecipes(cookList.id),
        getUserIngredients(currentUser!.id)
      ]);

      // Collect all required ingredients from all recipes
      const requiredIngredients: { [key: number]: IngredientComparison } = {};
      
      for (const recipe of cookListRecipes) {
        if (recipe.ingredients && Array.isArray(recipe.ingredients)) {
          for (const ingredient of recipe.ingredients) {
            const ingredientId = ingredient.ingredient_id;
            const quantity = ingredient.unit ? `${ingredient.quantity} ${ingredient.unit}` : ingredient.quantity;
            
            if (!requiredIngredients[ingredientId]) {
              requiredIngredients[ingredientId] = {
                ingredient_id: ingredientId,
                name: ingredient.name,
                required_quantity: quantity,
                has_ingredient: false,
                category: ingredient.category || 'Other'
              };
            } else {
              // If ingredient appears in multiple recipes, combine quantities on separate lines
              requiredIngredients[ingredientId].required_quantity += `\n${quantity}`;
            }
          }
        }
      }

      // Check which ingredients user has
      const userIngredientMap = new Map(
        userIngredients.map(ing => [ing.ingredient_id, ing])
      );

      const comparison: IngredientComparison[] = Object.values(requiredIngredients).map(req => {
        const userHas = userIngredientMap.get(req.ingredient_id);
        return {
          ...req,
          user_quantity: userHas?.quantity,
          has_ingredient: !!userHas
        };
      });

      setIngredientComparison(comparison);
      
      toast({
        title: "Smart Shopping List Generated!",
        description: `Analyzed ${comparison.length} ingredients from "${cookList.name}".`,
      });
    } catch (error) {
      console.error("Failed to generate shopping list:", error);
      toast({
        title: "Error",
        description: "Failed to generate smart shopping list.",
        variant: "destructive",
      });
    } finally {
      setGeneratingList(false);
    }
  };

  const handleBackToCookLists = () => {
    setSelectedCookList(null);
    setIngredientComparison([]);
  };

  const ingredientsUserHas = ingredientComparison.filter(ing => ing.has_ingredient);
  const ingredientsUserNeedsToBuy = ingredientComparison.filter(ing => !ing.has_ingredient);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-gradient-to-br from-blue-50 to-indigo-50">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-blue-800 flex items-center gap-2">
            🛒 Smart Shopping
          </DialogTitle>
          <p className="text-blue-600 italic">
            "Choose a cooklist to create a smart shopping list"
          </p>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {loading ? (
            <div className="text-center py-8 text-blue-600">
              <div className="text-lg font-medium">Loading your cooklists...</div>
            </div>
          ) : generatingList ? (
            <div className="text-center py-8 text-blue-600">
              <ShoppingCart className="w-12 h-12 mx-auto mb-4 text-blue-400 animate-pulse" />
              <div className="text-lg font-medium">Generating your smart shopping list...</div>
              <div className="text-sm mt-2">Analyzing recipes and comparing with your pantry...</div>
            </div>
          ) : selectedCookList ? (
            <>
              {/* Back button and header */}
              <div className="flex items-center gap-4 mb-6">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleBackToCookLists}
                  className="border-blue-200 hover:bg-blue-50"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Cook Lists
                </Button>
                <div>
                  <h3 className="text-lg font-semibold text-blue-800">
                    Smart Shopping List for "{selectedCookList.name}"
                  </h3>
                  <p className="text-sm text-blue-600">
                    {ingredientComparison.length} total ingredients analyzed
                  </p>
                </div>
              </div>

              {/* Two column layout */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Ingredients User Has */}
                <div className="bg-white rounded-lg shadow-md p-6 border border-green-100">
                  <div className="flex items-center gap-2 mb-4">
                    <Package className="w-5 h-5 text-green-600" />
                    <h4 className="text-lg font-semibold text-green-800">
                      You Have ({ingredientsUserHas.length})
                    </h4>
                  </div>
                  
                  {ingredientsUserHas.length > 0 ? (
                    <div className="space-y-3">
                      {ingredientsUserHas.map((ingredient) => (
                        <div
                          key={ingredient.ingredient_id}
                          className="bg-green-50 rounded-lg p-3 border border-green-100"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <Check className="w-4 h-4 text-green-600" />
                                <span className="font-medium text-green-800">
                                  {ingredient.name}
                                </span>
                              </div>
                              <div className="text-sm text-green-600 mt-1">
                                <div>Need:</div>
                                {ingredient.required_quantity.split('\n').map((qty, idx) => (
                                  <div key={idx} className="ml-2">• {qty}</div>
                                ))}
                                <div className="mt-1">Have: {ingredient.user_quantity}</div>
                              </div>
                            </div>
                            <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">
                              {ingredient.category}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-4 text-green-600">
                      <Package className="w-8 h-8 mx-auto mb-2 text-green-400" />
                      <p className="text-sm">You don't have any of the required ingredients</p>
                    </div>
                  )}
                </div>

                {/* Ingredients User Needs to Buy */}
                <div className="bg-white rounded-lg shadow-md p-6 border border-orange-100">
                  <div className="flex items-center gap-2 mb-4">
                    <ShoppingCart className="w-5 h-5 text-orange-600" />
                    <h4 className="text-lg font-semibold text-orange-800">
                      Need to Buy ({ingredientsUserNeedsToBuy.length})
                    </h4>
                  </div>
                  
                  {ingredientsUserNeedsToBuy.length > 0 ? (
                    <div className="space-y-3">
                      {ingredientsUserNeedsToBuy.map((ingredient) => (
                        <div
                          key={ingredient.ingredient_id}
                          className="bg-orange-50 rounded-lg p-3 border border-orange-100"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <X className="w-4 h-4 text-orange-600" />
                                <span className="font-medium text-orange-800">
                                  {ingredient.name}
                                </span>
                              </div>
                              <div className="text-sm text-orange-600 mt-1">
                                <div>Quantity needed:</div>
                                {ingredient.required_quantity.split('\n').map((qty, idx) => (
                                  <div key={idx} className="ml-2">• {qty}</div>
                                ))}
                              </div>
                            </div>
                            <span className="text-xs text-orange-600 bg-orange-100 px-2 py-1 rounded-full">
                              {ingredient.category}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-4 text-green-600">
                      <Check className="w-8 h-8 mx-auto mb-2 text-green-400" />
                      <p className="text-sm font-medium">Amazing! You have everything you need!</p>
                      <p className="text-xs mt-1">No shopping required for this cooklist.</p>
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <>
              <div>
                <h3 className="text-lg font-semibold text-blue-800 mb-4">
                  Select a Cook List to Shop For:
                </h3>
                
                {userCookLists.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {userCookLists.map((cookList) => (
                      <div
                        key={cookList.id}
                        onClick={() => handleCookListSelect(cookList)}
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
                        <p className="text-blue-600 text-sm mb-2">
                          {cookList.description}
                        </p>
                        <p className="text-blue-500 text-xs italic">
                          Click to generate smart shopping list for this collection
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-blue-600">
                    <ChefHat className="w-12 h-12 mx-auto mb-4 text-blue-400" />
                    <p className="text-lg font-medium mb-2">No cook lists found!</p>
                    <p className="text-sm">Create a cook list first to use smart shopping.</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};