import { ShoppingListOverview } from "@/components/ShoppingListOverview";
import { ProtectedRoute } from "@/components/ProtectedRoute";

export function ShoppingLists() {
  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-8">
        <ShoppingListOverview />
      </div>
    </ProtectedRoute>
  );
}