import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  ShoppingCart, 
  Calendar,
  Package,
  CheckCircle2,
  Plus
} from "lucide-react";
import { 
  getShoppingLists,
  type ShoppingList 
} from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { CreateShoppingListDialog } from "./CreateShoppingListDialog";
import { ShoppingListDialog } from "./ShoppingListDialog";

export function ShoppingListOverview() {
  const [shoppingLists, setShoppingLists] = useState<ShoppingList[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchShoppingLists();
  }, []);

  const fetchShoppingLists = async () => {
    setIsLoading(true);
    try {
      const lists = await getShoppingLists();
      setShoppingLists(lists);
    } catch (error) {
      console.error('Failed to fetch shopping lists:', error);
      toast({
        title: "Error",
        description: "Failed to load shopping lists",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getProgressColor = (purchased: number, total: number) => {
    if (total === 0) return 'bg-gray-200';
    const percentage = (purchased / total) * 100;
    if (percentage === 100) return 'bg-green-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-blue-500';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <ShoppingCart className="h-6 w-6" />
            Shopping Lists
          </h2>
          <p className="text-gray-600">
            Manage your shopping lists and track your grocery needs
          </p>
        </div>
        <CreateShoppingListDialog onShoppingListCreated={fetchShoppingLists}>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Shopping List
          </Button>
        </CreateShoppingListDialog>
      </div>

      {shoppingLists.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <ShoppingCart className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-medium mb-2">No shopping lists yet</h3>
            <p className="text-gray-600 mb-4">
              Create your first shopping list to get started
            </p>
            <CreateShoppingListDialog onShoppingListCreated={fetchShoppingLists}>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Shopping List
              </Button>
            </CreateShoppingListDialog>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {shoppingLists.map((list) => (
            <ShoppingListDialog
              key={list.id}
              shoppingListId={list.id}
              onShoppingListDeleted={fetchShoppingLists}
            >
              <Card className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{list.name}</CardTitle>
                    <Badge variant="outline" className="text-xs">
                      {list.purchased_items}/{list.total_items}
                    </Badge>
                  </div>
                  {list.cooklist_name && (
                    <CardDescription>
                      From: {list.cooklist_name}
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {/* Progress bar */}
                    <div className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span>Progress</span>
                        <span>
                          {list.total_items > 0
                            ? Math.round((list.purchased_items / list.total_items) * 100)
                            : 0}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            getProgressColor(list.purchased_items, list.total_items)
                          }`}
                          style={{
                            width: `${list.total_items > 0 
                              ? (list.purchased_items / list.total_items) * 100 
                              : 0}%`
                          }}
                        />
                      </div>
                    </div>
                    
                    {/* Stats */}
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Package className="h-4 w-4" />
                        <span>{list.total_items} items</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <CheckCircle2 className="h-4 w-4" />
                        <span>{list.purchased_items} done</span>
                      </div>
                    </div>
                    
                    {/* Date */}
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <Calendar className="h-3 w-3" />
                      <span>Created {formatDate(list.created_at)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </ShoppingListDialog>
          ))}
        </div>
      )}
    </div>
  );
}