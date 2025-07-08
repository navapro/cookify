import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { 
  ShoppingCart, 
  Trash2, 
  CheckCircle2, 
  Circle,
  Package,
  DollarSign
} from "lucide-react";
import { 
  getShoppingList,
  updateShoppingListItem,
  removeItemFromShoppingList,
  deleteShoppingList,
  type ShoppingListDetail 
} from "@/services/api";
import { useToast } from "@/hooks/use-toast";

interface ShoppingListDialogProps {
  shoppingListId: number;
  onShoppingListDeleted: () => void;
  children: React.ReactNode;
}

export function ShoppingListDialog({
  shoppingListId,
  onShoppingListDeleted,
  children,
}: ShoppingListDialogProps) {
  const [open, setOpen] = useState(false);
  const [shoppingList, setShoppingList] = useState<ShoppingListDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (open) {
      fetchShoppingList();
    }
  }, [open, shoppingListId]);

  const fetchShoppingList = async () => {
    setIsLoading(true);
    try {
      const list = await getShoppingList(shoppingListId);
      setShoppingList(list);
    } catch (error) {
      console.error('Failed to fetch shopping list:', error);
      toast({
        title: "Error",
        description: "Failed to load shopping list",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleTogglePurchased = async (ingredientId: number, isPurchased: boolean) => {
    try {
      await updateShoppingListItem(shoppingListId, ingredientId, isPurchased);
      
      // Update local state
      setShoppingList(prev => {
        if (!prev) return prev;
        return {
          ...prev,
          items: prev.items.map(item => 
            item.ingredient_id === ingredientId 
              ? { ...item, is_purchased: isPurchased }
              : item
          )
        };
      });
      
      toast({
        title: "Success",
        description: isPurchased ? "Item marked as purchased" : "Item marked as not purchased",
      });
    } catch (error) {
      console.error('Failed to update item:', error);
      toast({
        title: "Error",
        description: "Failed to update item",
        variant: "destructive",
      });
    }
  };

  const handleRemoveItem = async (ingredientId: number) => {
    try {
      await removeItemFromShoppingList(shoppingListId, ingredientId);
      
      // Update local state
      setShoppingList(prev => {
        if (!prev) return prev;
        return {
          ...prev,
          items: prev.items.filter(item => item.ingredient_id !== ingredientId)
        };
      });
      
      toast({
        title: "Success",
        description: "Item removed from shopping list",
      });
    } catch (error) {
      console.error('Failed to remove item:', error);
      toast({
        title: "Error",
        description: "Failed to remove item",
        variant: "destructive",
      });
    }
  };

  const handleDeleteList = async () => {
    try {
      await deleteShoppingList(shoppingListId);
      
      toast({
        title: "Success",
        description: "Shopping list deleted successfully",
      });
      
      setOpen(false);
      onShoppingListDeleted();
    } catch (error) {
      console.error('Failed to delete shopping list:', error);
      toast({
        title: "Error",
        description: "Failed to delete shopping list",
        variant: "destructive",
      });
    }
  };

  const groupedItems = shoppingList?.items.reduce((acc, item) => {
    const category = item.category || 'Other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(item);
    return acc;
  }, {} as Record<string, typeof shoppingList.items>) || {};

  const totalItems = shoppingList?.items.length || 0;
  const purchasedItems = shoppingList?.items.filter(item => item.is_purchased).length || 0;
  const totalPrice = shoppingList?.items.reduce((sum, item) => sum + (item.price || 0), 0) || 0;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ShoppingCart className="h-5 w-5" />
            {shoppingList?.name || 'Shopping List'}
          </DialogTitle>
          <DialogDescription>
            {shoppingList?.cooklist_name && (
              <span>Based on cook list: {shoppingList.cooklist_name}</span>
            )}
          </DialogDescription>
        </DialogHeader>
        
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Summary */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Package className="h-4 w-4" />
                  <span className="text-sm font-medium">
                    {purchasedItems}/{totalItems} items
                  </span>
                </div>
                {totalPrice > 0 && (
                  <div className="flex items-center gap-2">
                    <DollarSign className="h-4 w-4" />
                    <span className="text-sm font-medium">
                      ${totalPrice.toFixed(2)}
                    </span>
                  </div>
                )}
              </div>
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete List
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This will permanently delete this shopping list and all its items.
                      This action cannot be undone.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={handleDeleteList}>
                      Delete
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
            
            {/* Items */}
            <ScrollArea className="h-[400px] w-full">
              <div className="space-y-4">
                {Object.entries(groupedItems).map(([category, items]) => (
                  <div key={category}>
                    <h3 className="font-medium text-sm text-gray-600 mb-2">
                      {category}
                    </h3>
                    <div className="space-y-2">
                      {items.map((item) => (
                        <div
                          key={item.ingredient_id}
                          className={`flex items-center justify-between p-3 rounded-lg border ${
                            item.is_purchased
                              ? 'bg-green-50 border-green-200'
                              : 'bg-white border-gray-200'
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <Checkbox
                              checked={item.is_purchased}
                              onCheckedChange={(checked) => 
                                handleTogglePurchased(item.ingredient_id, checked as boolean)
                              }
                            />
                            <div className="flex-1">
                              <div className={`font-medium ${
                                item.is_purchased ? 'line-through text-gray-500' : ''
                              }`}>
                                {item.name}
                              </div>
                              <div className="text-sm text-gray-500">
                                {item.quantity}
                                {item.price && (
                                  <span className="ml-2">
                                    ${item.price.toFixed(2)}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveItem(item.ingredient_id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                    <Separator className="my-4" />
                  </div>
                ))}
                
                {totalItems === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <ShoppingCart className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>No items in this shopping list</p>
                  </div>
                )}
              </div>
            </ScrollArea>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}