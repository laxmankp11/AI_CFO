<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Supplier;
use App\Models\Tenant;

class SupplierController extends Controller
{
    /**
     * Store a newly created Supplier.
     * Accessible by Business Owner.
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'gstin' => 'nullable|string|max:15',
            'contact_person' => 'nullable|string|max:255',
            'default_expense_category' => 'nullable|string|max:255',
        ]);

        $supplier = new Supplier();
        $supplier->name = $validated['name'];
        $supplier->gstin = $validated['gstin'] ?? null;
        $supplier->contact_person = $validated['contact_person'] ?? null;
        $supplier->default_expense_category = $validated['default_expense_category'] ?? null;
        $supplier->save();

        return response()->json([
            'message' => 'Supplier created successfully',
            'data' => $supplier
        ], 201);
    }
}
