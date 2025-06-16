
import { useState } from "react";
import { Plus } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface Recipe {
  id: number;
  title: string;
  image: string;
  duration: number;
  cuisine: string;
  ingredients: string[];
  instructions: string[];
  isMyRecipe?: boolean;
}

interface CookListDialogProps {
  recipe: Recipe | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

// Mock cook lists data - in a real app this would come from a database
const mockCookLists = [
  { id: 1, name: "Weekend Meal Prep", recipeCount: 5 },
  { id: 2, name: "Quick Dinners", recipeCount: 8 },
  { id: 3, name: "Holiday Favorites", recipeCount: 3 },
  { id: 4, name: "Healthy Options", recipeCount: 12 },
];

export const CookListDialog = ({ recipe, open, onOpenChange }: CookListDialogProps) => {
  const [cookLists] = useState(mockCookLists);

  const handleAddToList = (listName: string) => {
    console.log(`Adding "${recipe?.title}" to "${listName}"`);
    // Here you would typically make an API call to add the recipe to the selected list
    onOpenChange(false);
  };

  if (!recipe) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold text-blue-700">
            Add to Cook List
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Add "{recipe.title}" to one of your cook lists:
          </p>
          
          <div className="space-y-2">
            {cookLists.map((list) => (
              <Button
                key={list.id}
                variant="outline"
                className="w-full justify-between p-3 h-auto hover:bg-blue-50 hover:border-blue-200"
                onClick={() => handleAddToList(list.name)}
              >
                <div className="text-left">
                  <div className="font-medium">{list.name}</div>
                  <div className="text-xs text-gray-500">
                    {list.recipeCount} recipes
                  </div>
                </div>
                <Plus className="w-4 h-4 text-blue-600" />
              </Button>
            ))}
          </div>
          
          <Button
            variant="ghost"
            className="w-full text-blue-600 hover:bg-blue-50"
            onClick={() => console.log("Create new cook list")}
          >
            <Plus className="w-4 h-4 mr-2" />
            Create New Cook List
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
