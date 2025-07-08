
import { useState, useEffect } from "react";
import { Plus } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { getUserCookLists, addRecipeToCookList } from "@/services/api";
import { getUser } from "@/utils/auth";

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

export const CookListDialog = ({ recipe, open, onOpenChange }: CookListDialogProps) => {
  const [cookLists, setCookLists] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [addingToList, setAddingToList] = useState<number | null>(null);
  const { toast } = useToast();
  const currentUser = getUser();

  useEffect(() => {
    const fetchCookLists = async () => {
      if (open && currentUser?.id) {
        setLoading(true);
        try {
          const userCookLists = await getUserCookLists(currentUser.id);
          setCookLists(userCookLists);
        } catch (error) {
          console.error("Failed to fetch cook lists:", error);
          toast({
            title: "Error",
            description: "Failed to load your cook lists",
            variant: "destructive",
          });
        } finally {
          setLoading(false);
        }
      }
    };

    fetchCookLists();
  }, [open, currentUser?.id, toast]);

  const handleAddToList = async (cookListId: number, listName: string) => {
    if (!recipe) return;
    
    setAddingToList(cookListId);
    try {
      await addRecipeToCookList(cookListId, recipe.id);
      toast({
        title: "Recipe Added! 🍳",
        description: `"${recipe.title}" has been added to "${listName}"`,
      });
      onOpenChange(false);
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to add recipe to cooklist",
        variant: "destructive",
      });
    } finally {
      setAddingToList(null);
    }
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
            {loading ? (
              <div className="text-center py-4 text-blue-600">Loading your cook lists...</div>
            ) : cookLists.length > 0 ? (
              cookLists.map((list) => (
                <Button
                  key={list.id}
                  variant="outline"
                  className="w-full justify-between p-3 h-auto hover:bg-blue-50 hover:border-blue-200"
                  onClick={() => handleAddToList(list.id, list.name)}
                  disabled={addingToList === list.id}
                >
                  <div className="text-left">
                    <div className="font-medium">{list.name}</div>
                    <div className="text-xs text-gray-500">
                      {list.recipeCount} recipes
                    </div>
                  </div>
                  {addingToList === list.id ? (
                    <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Plus className="w-4 h-4 text-blue-600" />
                  )}
                </Button>
              ))
            ) : (
              <div className="text-center py-4 text-gray-500">
                <p className="mb-2">No cook lists found</p>
                <p className="text-xs">Create your first cook list to get started!</p>
              </div>
            )}
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
